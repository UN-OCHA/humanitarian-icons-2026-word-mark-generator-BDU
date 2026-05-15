# OCHA Humanitarian Icons 2026

The official set of humanitarian icons used across OCHA products, publications, and digital platforms. Maintained by the **OCHA Brand and Design Unit (BDU)**.

## What's in this repo

| Path | Description |
|---|---|
| `svg/` | 388 SVG icons (optimized, single-color, OCHA blue `#009edb`) |
| `metadata.json` | Icon metadata: names, families, keywords, wordmark approval flags |
| `word-mark-generator/` | Web-based wordmark generator with approval workflow ([live tool](https://un-ocha.github.io/humanitarian-icons-2026-BDU/word-mark-generator/)) |
| `curator/` | Icon curator tool for browsing and managing the collection |
| `scripts/` | Python utilities for generating exports (Excel, PowerPoint, font, grid, wordmarks) |
| `output/` | Pre-built exports: CSV, PPTX, XLSX, SVG grid, icon font |
| `assets/` | OCHA logo and favicon |

## Wordmark Generator

A browser-based tool for creating branded wordmarks using Humanitarian Icons. Includes an approval workflow managed via Google Sheets.

**Live tool:** https://un-ocha.github.io/humanitarian-icons-2026-BDU/word-mark-generator/

98 icons are approved for use in wordmarks. The full workflow:

1. User selects an icon and enters text
2. User submits a request for approval
3. BDU reviews and approves/rejects via the Google Sheet
4. User receives an automated email with a direct download link

See [`word-mark-generator/APPROVAL_SETUP.md`](word-mark-generator/APPROVAL_SETUP.md) for setup and operations documentation.

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

## Project Owner

Javier Cueto, Lead of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
