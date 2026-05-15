# OCHA Humanitarian Icons 2026

The official set of **388 humanitarian icons** used across OCHA products, publications, and digital platforms. All icons are single-color SVGs in OCHA blue (`#009edb`), designed to work at any size from 16px to print resolution.

Maintained by the **OCHA Brand and Design Unit (BDU)**.

## Using the Icons

### Direct download

Browse the [`svg/`](svg/) folder and download individual SVG files.

### CDN (recommended for web)

Load any icon directly via jsDelivr — no download needed:

```html
<img src="https://cdn.jsdelivr.net/gh/UN-OCHA/humanitarian-icons-2026-BDU@main/svg/Shelter.svg" alt="Shelter" />
```

Pattern:
```
https://cdn.jsdelivr.net/gh/UN-OCHA/humanitarian-icons-2026-BDU@main/svg/{Icon-name}.svg
```

### GitHub Pages

All icons are also served from GitHub Pages:
```
https://un-ocha.github.io/humanitarian-icons-2026-BDU/svg/{Icon-name}.svg
```

### Pre-built exports

Ready-to-use packages in the [`output/`](output/) folder:

| File | Format | Use case |
|---|---|---|
| `Humanitarian_icons.xlsx` | Excel | Reference sheets, internal catalogues |
| `Humanitarian_icons.pptx` | PowerPoint | Presentations, slide decks |
| `Humanitarian_icons.csv` | CSV | Data integrations, lookups |
| `Humanitarian_icons_complete_library.svg` | SVG grid | Visual overview of the full set |
| `font/` | Icon font | Web and app interfaces |

### Metadata

[`metadata.json`](metadata.json) contains structured data for every icon — name, family, keywords, and wordmark eligibility:

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

### Colour

All SVGs use OCHA blue `#009edb`. To change colour, apply a CSS filter or edit the `fill` attribute. The icons are designed to work in monochrome — do not add gradients or multiple colours.

## License

The OCHA Humanitarian Icons are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt them with appropriate credit to OCHA.

---

## Internal Tools

These tools are used by BDU to manage, generate, and distribute the icon collection. They are not intended for end users.

### Wordmark Generator

A browser-based tool that allows OCHA staff to create branded wordmarks using Humanitarian Icons. All wordmarks require BDU approval before final download.

**Live tool:** https://un-ocha.github.io/humanitarian-icons-2026-BDU/word-mark-generator/

98 of the 388 icons are approved for use in wordmarks. The approval workflow is automated: BDU changes a status in a Google Sheet, and the requester receives an email with a direct download link.

| File | Purpose |
|---|---|
| `word-mark-generator/index.html` | The generator (single-page app, no build step) |
| `word-mark-generator/google-apps-script.js` | Backend code deployed as a Google Apps Script web app |
| `word-mark-generator/APPROVAL_SETUP.md` | Setup and operations documentation |

### Icon Curator

A browser-based tool for browsing, reviewing, and managing icon metadata.

| File | Purpose |
|---|---|
| `curator/index.html` | The curator interface |

### Build Scripts

Python utilities for generating the distributable exports. Requires Python 3.9+ with dependencies in `.venv/`.

| Script | What it does |
|---|---|
| `scripts/populate_metadata.py` | Scans `svg/` and builds `metadata.json` |
| `scripts/generate-excel.py` | Generates the Excel export |
| `scripts/generate-pptx.py` | Generates the PowerPoint export |
| `scripts/generate-font.py` | Generates the icon font |
| `scripts/generate-grid.py` | Generates the complete SVG grid |
| `scripts/generate-wordmark.py` | Batch generates wordmarks from metadata |
| `scripts/fix_metadata.py` | Utility for metadata corrections |

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
