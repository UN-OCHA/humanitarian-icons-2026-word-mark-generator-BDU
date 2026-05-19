#!/usr/bin/env python3
"""
populate_metadata.py — Rebuild metadata.json from the SVG folder + existing
metadata.json. This is the single canonical "refresh metadata" script.

It does three jobs idempotently:

  1. Sync the icon set with svg/ — add stub entries for any new SVGs,
     drop entries whose SVG was removed (loudly logged).
  2. Normalise display names (sentence case, preserving acronyms like
     UN/NGO/IDP/UX/UI/AI etc.) — derives a name from the filename only
     if the entry has no human-supplied `name` yet.
  3. Reassign `font_codepoint` for every icon, sequentially U+E001…,
     alphabetical by key.

Everything else (`family`, `tags`, `wordmark`, `wordmark_valign`,
`date_added`) is the human's domain — preserved untouched across runs.

The old Excel/curator-JSON pipeline and the separate `tags.json` are
retired — tags now live inside each icon's metadata.json entry.

Source of truth for human-curated fields: metadata.json itself.
Edit it directly, or use icon-manager/index.html.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SVG_DIR = REPO / "svg"
METADATA_PATH = REPO / "metadata.json"

# ──────────────────────────────────────────────────────────────────────
# Display-name helpers
# ──────────────────────────────────────────────────────────────────────

# Tokens that must remain uppercase (or have a fixed mixed case) in the
# display name. Anything outside this set is sentence-cased.
UPPERCASE_WORDS = {
    "UN", "NGO", "IDP", "AI", "API", "PDF", "CSV", "XLSX", "DOCX",
    "ZIP", "UX", "UI", "CCCM", "WASH", "MHPSS",
}

# Words that are spelled with a fixed mixed case (typically the second
# segment of a hyphenated token like "E-mail" or "P-code").
SPECIAL_TOKENS = {
    "e-mail": "E-mail",
    "p-code": "P-code",
    "covid-19": "COVID-19",
}


def display_name_from_key(key: str) -> str:
    """Filename stem → display name. 'Indigenous-people' → 'Indigenous people'.
    Acronyms stay uppercase. Special tokens get their canonical casing."""
    # Special tokens first (case-insensitive lookup)
    if key.lower() in SPECIAL_TOKENS:
        return SPECIAL_TOKENS[key.lower()]

    # Replace dashes/underscores with spaces
    raw = re.sub(r"[-_]+", " ", key).strip()
    tokens = raw.split()
    out: list[str] = []
    for i, tok in enumerate(tokens):
        upper = tok.upper()
        if upper in UPPERCASE_WORDS:
            out.append(upper)
        elif i == 0:
            out.append(tok[:1].upper() + tok[1:].lower())
        else:
            out.append(tok.lower())
    name = " ".join(out)

    # Repair embedded special tokens that lost their hyphen
    name = re.sub(r"\bE\s+mail\b", "E-mail", name, flags=re.IGNORECASE)
    name = re.sub(r"\bP\s+code\b", "P-code", name, flags=re.IGNORECASE)
    name = re.sub(r"\bCOVID\s+19\b", "COVID-19", name, flags=re.IGNORECASE)
    return name


# ──────────────────────────────────────────────────────────────────────
# Families list helpers
# ──────────────────────────────────────────────────────────────────────

# Canonical ordering for the families list. Any family used by an icon
# but not in this list is appended alphabetically at the end.
PREFERRED_FAMILY_ORDER = [
    "Clusters",
    "Other sectors",
    "Disasters, hazards and crises",
    "Socioeconomic and development",
    "People",
    "Activities strategy",
    "Product type",
    "Food and non-food items",
    "Water sanitation and hygiene",
    "Camp",
    "Security and incident",
    "Physical barriers",
    "Damage",
    "General infrastructure",
    "Logistics",
    "Telecommunications and technology",
    "UX UI",
    "Health",
    "Lockdown",
]


def build_families_list(icons: dict) -> list[str]:
    """Collect every family in actual use, ordered by PREFERRED_FAMILY_ORDER.
    Drops 'Unassigned' from the list (it's a stub, not a real family)."""
    used = {v["family"] for v in icons.values() if v["family"] != "Unassigned"}
    ordered = [f for f in PREFERRED_FAMILY_ORDER if f in used]
    extras = sorted(used - set(ordered))
    return ordered + extras


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main() -> int:
    if not SVG_DIR.is_dir():
        sys.exit(f"SVG folder not found at {SVG_DIR}.")
    if not METADATA_PATH.is_file():
        sys.exit(
            f"metadata.json not found at {METADATA_PATH}. "
            "This script preserves existing metadata — it cannot bootstrap "
            "from scratch."
        )

    metadata = json.loads(METADATA_PATH.read_text())
    icons = metadata.setdefault("icons", {})

    svg_keys = sorted({p.stem for p in SVG_DIR.glob("*.svg")})
    print(f"Icons in svg/: {len(svg_keys)}")
    print(f"Existing metadata entries: {len(icons)}")

    today = date.today().isoformat()

    # 1. Drop entries whose SVG no longer exists.
    stale = [k for k in icons if k not in set(svg_keys)]
    for k in stale:
        print(f"  WARNING: dropping {k!r} — no matching SVG in svg/.")
        del icons[k]

    # 2. Add stubs for new icons.
    new_keys: list[str] = []
    for key in svg_keys:
        if key in icons:
            continue
        icons[key] = {
            "name": display_name_from_key(key),
            "family": "Unassigned",
            "tags": [],
            "wordmark": False,
            "wordmark_valign": 0,
            "font_codepoint": "",  # set in step 5
            "date_added": today,
        }
        new_keys.append(key)

    # 3. Backfill missing fields on every entry (idempotent).
    for key, entry in icons.items():
        if not entry.get("name"):
            entry["name"] = display_name_from_key(key)
        entry.setdefault("family", "Unassigned")
        entry.setdefault("tags", [])
        entry.setdefault("wordmark", False)
        entry.setdefault("wordmark_valign", 0)
        entry.setdefault("date_added", today)

    # 4. Sort icons by key (case-insensitive) for stable, alphabetical output.
    sorted_icons = {k: icons[k] for k in sorted(icons, key=str.casefold)}

    # 5. Reassign font_codepoints sequentially, alphabetically.
    codepoint = 0xE001
    for entry in sorted_icons.values():
        entry["font_codepoint"] = f"U+{codepoint:04X}"
        codepoint += 1
    next_codepoint = f"U+{codepoint:04X}"

    # 6. Rebuild families list.
    families = build_families_list(sorted_icons)

    # 7. Write final metadata.
    output = {
        "meta": {
            "version": "2.0",
            "last_updated": today,
            "next_font_codepoint": next_codepoint,
        },
        "families": families,
        "icons": sorted_icons,
    }
    METADATA_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    )

    print()
    print(f"Wrote {len(sorted_icons)} icons.")
    print(f"Codepoints: U+E001 → U+{codepoint - 1:04X}  (next: {next_codepoint})")
    print(f"Families:   {len(families)}")
    if new_keys:
        print(f"\nNew icon stubs created ({len(new_keys)}):")
        for k in new_keys:
            print(f"  + {k}  (family=Unassigned, tags=[])")
        print()
        print("Open icon-manager/index.html in Chrome to assign family + tags.")
    if stale:
        print(f"\nDropped {len(stale)} stale entries (SVG missing).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
