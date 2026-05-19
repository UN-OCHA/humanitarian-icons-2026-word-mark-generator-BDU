#!/usr/bin/env python3
"""
Sync the local `svg/` folder + `metadata.json` to OCHA's Frontify icon library.

What it does:
  1. Lists every `svg/*.svg` filename in the repo.
  2. Queries the Frontify icon library (project id 251023) for all current assets
     and their tags.
  3. Diffs the two.
  4. For each icon in the repo but NOT in Frontify: uploads the SVG and applies
     the tags from the matching `metadata.json["icons"][key]` entry.
  5. For each icon in Frontify but NOT in the repo: prints a warning. NEVER
     deletes anything — manual cleanup only.
  6. For each icon in both: checks if metadata.json has tags missing from
     Frontify and adds them (additive only — existing tags are never removed).
  7. Prints a summary and exits 0 on success, 1 if any individual operation
     failed (so CI can decide whether to fail the job).

Usage:
    python scripts/sync_to_frontify.py            # apply changes
    python scripts/sync_to_frontify.py --dry-run  # show what would change

Required env var:
    FRONTIFY_TOKEN — personal access token with the brand and asset scopes.

Optional env vars (sensible defaults for OCHA):
    FRONTIFY_DOMAIN     (default: brand.unocha.org)
    FRONTIFY_LIBRARY_ID (default: 251023)

Maintained by the OCHA Brand and Design Unit (BDU). Focal point: cuetoj@un.org.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
SVG_DIR = REPO_ROOT / "svg"
METADATA_JSON = REPO_ROOT / "metadata.json"

FRONTIFY_DOMAIN = os.environ.get("FRONTIFY_DOMAIN", "brand.unocha.org")
FRONTIFY_LIBRARY_ID = int(os.environ.get("FRONTIFY_LIBRARY_ID", "251023"))
GRAPHQL_URL = f"https://{FRONTIFY_DOMAIN}/graphql"

TOKEN = os.environ.get("FRONTIFY_TOKEN", "").strip()


# ---------- Helpers ----------


def _norm(name: str) -> str:
    """Normalize an icon name for matching (dashes/underscores/spaces collapse,
    casing dropped). Both 'Indigenous people' and 'Indigenous-people' compare equal."""
    return re.sub(r"[\s_\-]+", "-", name.strip().lower())


def _bearer_headers() -> dict[str, str]:
    if not TOKEN:
        sys.exit("FRONTIFY_TOKEN env var is empty. Aborting.")
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def gql(client: httpx.Client, query: str, variables: dict | None = None) -> dict:
    """One GraphQL call. Raises if HTTP status is bad; returns the JSON body
    untouched (callers inspect `errors` and `data` themselves)."""
    body: dict = {"query": query}
    if variables is not None:
        body["variables"] = variables
    r = client.post(GRAPHQL_URL, json=body, headers=_bearer_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


# ---------- Frontify library reads ----------


def fetch_library_assets(client: httpx.Client) -> list[dict]:
    """Page through `library(id).assets` and return [{id, opaque_id, title, tags}, …]."""
    query = """
    query GetAssets($id: ID!, $page: Int!, $limit: Int!) {
      library(id: $id) {
        assets(page: $page, limit: $limit) {
          total page limit hasNextPage
          items { id title tags { value source } }
        }
      }
    }
    """
    items: list[dict] = []
    page = 1
    while True:
        r = gql(client, query, {"id": str(FRONTIFY_LIBRARY_ID), "page": page, "limit": 100})
        if "errors" in r:
            sys.exit(f"GraphQL errors when listing assets: {r['errors']}")
        block = r["data"]["library"]["assets"]
        for it in block["items"]:
            items.append(
                {
                    "opaque_id": it["id"],
                    "asset_id": _decode_opaque(it["id"]),
                    "title": it["title"],
                    "tags": sorted({(t.get("value") or "").strip().lower() for t in (it.get("tags") or []) if t.get("value")}),
                }
            )
        if not block["hasNextPage"]:
            break
        page += 1
        if page > 50:
            sys.exit("Pagination guard tripped (>50 pages); something is off.")
    return items


def _decode_opaque(opaque: str) -> int | None:
    """Frontify asset ids in GraphQL are base64-encoded {identifier, type} JSON.
    Decode to the numeric identifier for logging."""
    try:
        return int(json.loads(base64.b64decode(opaque))["identifier"])
    except Exception:
        return None


# ---------- Frontify mutations ----------


def upload_svg(client: httpx.Client, file_path: Path, title: str) -> tuple[str, int | None]:
    """Three-step pipeline: uploadFile → S3 PUT → createAsset.
    Returns (opaque_id, numeric_asset_id)."""
    size = file_path.stat().st_size
    filename = file_path.name

    r = gql(
        client,
        "mutation U($i: UploadFileInput!) { uploadFile(input: $i) { id urls } }",
        {"i": {"filename": filename, "size": size}},
    )
    if r.get("errors"):
        sys.exit(f"uploadFile error for {title}: {r['errors']}")
    upload_id = r["data"]["uploadFile"]["id"]
    s3_url = r["data"]["uploadFile"]["urls"][0]

    with open(file_path, "rb") as f:
        data = f.read()
    s3_resp = client.put(s3_url, content=data, timeout=120)
    if s3_resp.status_code not in (200, 201, 204):
        sys.exit(f"S3 upload failed for {title}: HTTP {s3_resp.status_code}")

    r = gql(
        client,
        "mutation CA($i: CreateAssetInput!) { createAsset(input: $i) { job { assetId } } }",
        {"i": {"fileId": upload_id, "title": title, "projectId": str(FRONTIFY_LIBRARY_ID)}},
    )
    if r.get("errors"):
        sys.exit(f"createAsset error for {title}: {r['errors']}")
    opaque = r["data"]["createAsset"]["job"]["assetId"]
    return opaque, _decode_opaque(opaque)


def add_tags(client: httpx.Client, opaque_id: str, tags: list[str]) -> None:
    """Additive only. Never removes existing tags. No-op if `tags` is empty."""
    if not tags:
        return
    r = gql(
        client,
        "mutation A($i: AddAssetTagsInput!) { addAssetTags(input: $i) { asset { id } } }",
        {"i": {"id": opaque_id, "tags": [{"value": t} for t in tags]}},
    )
    if r.get("errors"):
        raise RuntimeError(f"addAssetTags errors: {r['errors']}")


# ---------- Main ----------


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync SVG icons to the Frontify icon library.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without applying them.")
    args = parser.parse_args()

    if not SVG_DIR.is_dir():
        sys.exit(f"SVG folder not found at {SVG_DIR}. Run from the repo root.")
    if not METADATA_JSON.is_file():
        sys.exit(f"metadata.json not found at {METADATA_JSON}.")

    # Load metadata.json icons (key = filename stem; value has .name, .family, .tags, …)
    metadata = json.loads(METADATA_JSON.read_text())
    md_icons: dict[str, dict] = metadata.get("icons", {})
    md_norm: dict[str, str] = {_norm(k): k for k in md_icons}

    # Local icons (filename stem; we strip the .svg)
    local_files = sorted(p for p in SVG_DIR.glob("*.svg") if p.is_file())
    local_norm: dict[str, Path] = {_norm(p.stem): p for p in local_files}

    print(f"Repo svg/ icons: {len(local_files)}")

    with httpx.Client() as client:
        remote = fetch_library_assets(client)
        remote_norm: dict[str, dict] = {_norm(a["title"]): a for a in remote}
        print(f"Frontify library assets (id {FRONTIFY_LIBRARY_ID}): {len(remote)}")

        # 1. New icons: in repo, not in Frontify
        new_icons = [(n, local_norm[n]) for n in sorted(local_norm) if n not in remote_norm]
        # 2. Orphans: in Frontify, not in repo
        orphans = [remote_norm[n] for n in sorted(remote_norm) if n not in local_norm]
        # 3. Tag updates: in both, metadata.json has values missing from Frontify
        tag_adds: list[tuple[dict, list[str]]] = []
        for n in sorted(local_norm):
            if n not in remote_norm:
                continue
            md_key = md_norm.get(n)
            if not md_key:
                continue
            desired = [t for t in md_icons[md_key].get("tags", []) if t and t.strip()]
            existing = set(remote_norm[n]["tags"])
            to_add = [t for t in desired if t.strip().lower() not in existing]
            if to_add:
                tag_adds.append((remote_norm[n], to_add))

        print()
        print(f"  • New icons to upload:    {len(new_icons)}")
        for _, p in new_icons:
            print(f"      + {p.name}")
        print(f"  • Existing icons getting new tags: {len(tag_adds)}")
        for asset, adds in tag_adds[:10]:
            print(f"      ~ {asset['title']:<40s} + {adds}")
        if len(tag_adds) > 10:
            print(f"      … and {len(tag_adds) - 10} more")
        print(f"  • Orphans (in Frontify, not in repo): {len(orphans)}")
        for a in orphans:
            print(f"      ? {a['title']}  (asset_id={a['asset_id']})  ← not deleted; investigate manually")

        if args.dry_run:
            print("\nDry run — no changes applied. Re-run without --dry-run to apply.")
            return 0

        if not new_icons and not tag_adds:
            print("\nNothing to do. Library is in sync with the repo.")
            return 0

        failures: list[str] = []

        # 1. Upload new icons + tag them
        for n, path in new_icons:
            md_key = md_norm.get(n)
            title = md_icons[md_key]["name"] if md_key else path.stem
            try:
                opaque, asset_id = upload_svg(client, path, title)
                print(f"  uploaded: {title}  (asset_id={asset_id})")
                if md_key:
                    tags = [t for t in md_icons[md_key].get("tags", []) if t and t.strip()]
                    if tags:
                        add_tags(client, opaque, tags)
                        print(f"      tagged: {tags}")
                else:
                    print(f"      (no metadata.json entry — uploaded with no tags)")
            except Exception as e:
                failures.append(f"{path.name}: {e}")
                print(f"  FAIL upload: {path.name} → {e}")
            time.sleep(0.1)  # gentle pacing

        # 2. Add missing tags to existing icons (additive)
        for asset, adds in tag_adds:
            try:
                add_tags(client, asset["opaque_id"], adds)
                print(f"  tagged: {asset['title']}  + {adds}")
            except Exception as e:
                failures.append(f"{asset['title']} tags: {e}")
                print(f"  FAIL tag: {asset['title']} → {e}")
            time.sleep(0.05)

        # Summary
        print()
        if failures:
            print(f"Done with {len(failures)} failure(s):")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("Done. Library is in sync with the repo.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
