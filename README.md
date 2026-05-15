# OCHA Humanitarian Icons 2026

The official set of humanitarian icons used across OCHA products, publications, and digital platforms. Maintained by the **OCHA Brand and Design Unit (BDU)**.

## What's in this repo

| Path | Description |
|---|---|
| `svg/` | 388 SVG icons (optimized, single-color, OCHA blue `#009edb`) |
| `metadata.json` | Icon metadata: names, families, keywords, wordmark approval flags |
| `curator/` | Icon curator tool for browsing and managing the collection |
| `scripts/` | Python utilities for generating exports (Excel, PowerPoint, font, grid, wordmarks) |
| `output/` | Pre-built exports: CSV, PPTX, XLSX, SVG grid, icon font |
| `assets/` | OCHA logo and favicon |

## Using the Icons

### CDN (jsDelivr)

```
https://cdn.jsdelivr.net/gh/UN-OCHA/humanitarian-icons-2026-BDU@main/svg/{icon-name}.svg
```

### GitHub Pages

All icons are also available via GitHub Pages:
```
https://un-ocha.github.io/humanitarian-icons-2026-BDU/svg/{icon-name}.svg
```

### Metadata

`metadata.json` contains structured data for each icon:

```json
{
  "icons": {
    "Agriculture": {
      "name": "Agriculture",
      "family": "Food security",
      "keywords": ["farming", "crops"],
      "wordmark": true,
      "wordmark_valign": 0
    }
  }
}
```

## Scripts

Requires Python 3.9+ with dependencies in `.venv/`.

| Script | What it does |
|---|---|
| `populate_metadata.py` | Scans `svg/` and builds `metadata.json` |
| `generate-excel.py` | Generates the Excel export |
| `generate-pptx.py` | Generates the PowerPoint export |
| `generate-font.py` | Generates the icon font |
| `generate-grid.py` | Generates the complete SVG grid |
| `generate-wordmark.py` | Batch generates wordmarks from metadata |
| `fix_metadata.py` | Utility for metadata corrections |

## License

The OCHA Humanitarian Icons are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Additional Tool: Wordmark Generator

A separate browser-based tool hosted from this repo that allows OCHA staff to create branded wordmarks using Humanitarian Icons. It includes a full approval workflow so that all wordmarks are reviewed by BDU before final download.

**Live tool:** https://un-ocha.github.io/humanitarian-icons-2026-BDU/word-mark-generator/

98 of the 388 icons are approved for use in wordmarks. The tool lives in `word-mark-generator/` and consists of:

| File | Purpose |
|---|---|
| `index.html` | The generator (single-page app, no build step) |
| `google-apps-script.js` | Backend code deployed as a Google Apps Script web app |
| `APPROVAL_SETUP.md` | Full setup and operations documentation |

### How the approval workflow works

1. User selects an icon, enters text, and submits a request
2. BDU receives an email notification with a preview image
3. BDU opens the Google Sheet and changes the status to "Approved" or "Rejected"
4. User automatically receives an email with a direct download link

See [`word-mark-generator/APPROVAL_SETUP.md`](word-mark-generator/APPROVAL_SETUP.md) for detailed setup, day-to-day operations, and troubleshooting.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
