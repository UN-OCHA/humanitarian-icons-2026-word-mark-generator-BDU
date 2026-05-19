# Icon Manager

A browser-based tool for managing the OCHA humanitarian icon library — add new icons, edit tags, change families, toggle wordmark approval. Edits write back to `metadata.json` at the repo root.

## Opening it

Open `icon-manager/index.html` in **Chrome** or **Edge** (uses the File System Access API for save dialogs — Safari and Firefox will still work but fall back to plain downloads).

No build step. No server needed. Just open the HTML file in the browser.

## What you can do

### Browse and search

- All 389 icons grouped by family.
- Search by name, key, or family.
- Sort by family, alphabetical, codepoint, or date added.

### Edit an icon

Each icon card lets you edit:

- **Name** — display name (e.g. "Drone")
- **Family** — pick from the dropdown
- **Tags** — type a tag and press <kbd>Enter</kbd> (or use commas to add several at once); click ✕ on a chip to remove
- **Wordmark approved** — toggle the checkbox; reveal a vertical-alignment slider if true
- **Remove icon** — the × button on the card (removes the metadata entry only, not the SVG file)

Changes are tracked. A yellow banner appears at the top when you have unsaved changes.

### Add a new icon

Click **+ Add Icon** in the toolbar:

1. **Drop the SVG** into the drop zone (or click to browse). The filename becomes the icon key — use kebab-case-with-capital-first (e.g. `Drone.svg`, `Air-quality.svg`).
2. **Pick a family** from the dropdown.
3. **Type tags** — press <kbd>Enter</kbd> after each, or paste a comma-separated list.
4. **Toggle wordmark** if applicable.
5. Click **Add Icon** → save the SVG into the repo's `svg/` folder when prompted.

The icon's font codepoint is auto-assigned (visible in the modal). It may be reshuffled on the next `git push` because `populate_metadata.py` reassigns codepoints alphabetically across the whole set — that's expected.

### Save

Click **Export metadata.json** in the toolbar. Save it over the repo's existing `metadata.json`.

Then commit and push:

```bash
git add svg/ metadata.json
git commit -m "add: <icon-name>"   # or "edit: tags for <icon-name>"
git push
```

CI takes over from there — regenerates the Excel/PowerPoint/font/grid outputs and syncs the change to the OCHA Frontify icon library.

## Notes

- **SVG colour** — all icons must be single-colour OCHA blue (`#009edb`). The preview cleans embedded styles and forces this fill colour, but the source SVG should match.
- **No autosave** — refresh and you lose unsaved edits. Always Export before closing.
- **Existing SVG check** — if you type a key that matches an SVG already in `svg/`, the preview loads from there. Drop a new SVG to overwrite.
- **Tags are case-sensitive in the data** but Frontify-side matching is normalised, so don't worry about consistency for casing.

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
