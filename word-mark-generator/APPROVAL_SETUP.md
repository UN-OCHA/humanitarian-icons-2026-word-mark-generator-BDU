# Wordmark Approval System

## Overview

The OCHA wordmark generator uses a Google Sheet + Google Apps Script backend to enforce an approval workflow. Users cannot download a clean wordmark without approval from the OCHA Brand and Design Unit.

### Workflow

1. **User** creates a wordmark preview on the generator page (can download a DRAFT-watermarked PNG)
2. **User** submits a request with their email → progress bar shown during submission
3. **BDU** receives an email notification at ochavisual@un.org with a preview image attached
4. **BDU** opens the Google Sheet and changes the status from "Pending" to "Approved" (or "Rejected")
5. **User** automatically receives an approval email from "OCHA Visual" (unochavisual@gmail.com) with a direct download link; BDU is CC'd at ochavisual@un.org
6. **User** clicks the link → generator opens with request pre-loaded, scrolls to download section, shows progress bar, and presents the download button
7. **User** downloads the clean SVG + PNG package (unlimited downloads once approved)

---

## Published URL

**Generator:** https://un-ocha.github.io/humanitarian-icons-2026-BDU/word-mark-generator/

**Deep-link format (used in approval emails):**
```
https://un-ocha.github.io/humanitarian-icons-2026-BDU/word-mark-generator/?requestId=WM-XXXXX&email=user@example.com
```

---

## Current Setup

### Google Sheet

- **Name:** OCHA word mark generator approval request
- **Account:** unochavisual@gmail.com
- **URL:** https://docs.google.com/spreadsheets/d/1eEb70cPxF8dYkomCcBR6TZXy0Q7jTnDM-LxWPbAspxE/edit
- **Sheet ID:** `1eEb70cPxF8dYkomCcBR6TZXy0Q7jTnDM-LxWPbAspxE`
- **Tab:** Requests

#### Column headers (row 1)

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| Timestamp | Email | Icon | Line 1 | Line 2 | Line 3 | Layout | Request ID | Status | Downloaded At |

#### Status dropdown (column I)

Column I has a data validation dropdown with color-coded options:

| Status | Color | Meaning |
|---|---|---|
| Pending | Orange | Request submitted, awaiting review |
| Approved | Blue | Approved by BDU, user can download |
| Rejected | Red | Rejected by BDU |

### Apps Script (Standalone Project)

- **Account:** unochavisual@gmail.com
- **Project name:** OCHA Wordmark Approval API
- **Project URL:** https://script.google.com/u/1/home/projects/1YQbKuIz2Y8MOf8QNI2O2Fv6dpdsykCGtxX0Jl8s_IbQZB2XjHt32jXin/edit
- **Execute as:** unochavisual@gmail.com
- **Who has access:** Anyone
- **Notification email:** ochavisual@un.org (set via `NOTIFY_EMAIL` constant)
- **Sender display name:** "OCHA Visual" (set via `name` option in `MailApp.sendEmail`)

This is a **standalone** script (not bound to the sheet). It accesses the sheet via `SpreadsheetApp.openById(SHEET_ID)`.

### Web App Deployment

- **Deployment URL:** `https://script.google.com/macros/s/AKfycbz3zxqniGTEE5vmxGlceBb0MJj9u6x7nU3As3CdauwS_4WWONZ3xKTDgre7vMXlbcfv3w/exec`
- This URL is referenced in `index.html` as `APPROVAL_API_URL`

### Installable Trigger (onEdit)

- **Function:** `onStatusChange`
- **Event:** From spreadsheet → On edit
- **What it does:** When the Status column (I) changes to "Approved" or "Rejected", it automatically sends an email to the requester
- **Approved email** includes: request details + a direct deep-link to download
- **Rejected email** includes: request details + instruction to contact ochavisual@un.org
- **CC:** ochavisual@un.org on all emails (so BDU has a copy)
- **Sender:** "OCHA Visual" <unochavisual@gmail.com>

The trigger runs as unochavisual@gmail.com regardless of which Google account edits the sheet. You can approve from your personal account, UN account, or mobile — the email always comes from the OCHA Visual address.

### Generator HTML

The approval API URL is set in `index.html`:
```js
const APPROVAL_API_URL = "https://script.google.com/macros/s/AKfycbz3zxqniGTEE5vmxGlceBb0MJj9u6x7nU3As3CdauwS_4WWONZ3xKTDgre7vMXlbcfv3w/exec";
```

SVG icons are loaded via **relative paths** (`../svg/`) on GitHub Pages (not jsDelivr CDN), avoiding cache issues after repo renames.

---

## Day-to-Day Operations

### When a user submits a request

- A new row appears in the Google Sheet with status **Pending** (orange)
- You receive an email at ochavisual@un.org with the request details and a preview PNG attached
- The email is sent from unochavisual@gmail.com
- The user sees their **Request ID** on screen (e.g., WM-A3K7P2)

### To approve a request

1. Open the Google Sheet
2. Find the row
3. Use the Status dropdown in column I to change from **Pending** to **Approved**
4. Done — the user automatically receives an email with a download link, and BDU gets a CC copy

### To reject a request

1. Use the Status dropdown to change from **Pending** to **Rejected**
2. Done — the user automatically receives an email explaining they need to contact BDU

### When the user downloads

- They click the link in their approval email (or manually enter Request ID + email on the generator)
- The generator auto-verifies the request and shows the download button
- They download the clean SVG + PNG package (no watermark)
- The download timestamp is recorded in column J
- Downloads are unlimited once approved

---

## Troubleshooting

**"Could not reach the approval service"**
- Verify the Web App URL in `index.html` matches the deployed URL
- Confirm the Apps Script deployment has "Who has access: Anyone"
- Check the Apps Script execution log for errors

**Approval email not sending**
- Check the Triggers page in Apps Script (clock icon in sidebar) — should show 1 trigger: `onStatusChange`, From spreadsheet, On edit
- If missing, click "+ Add Trigger": function = `onStatusChange`, event source = From spreadsheet, event type = On edit, then Save
- Check the Executions page for errors

**Approval email goes to spam**
- Ask the user to mark it as "Not spam" — Gmail learns quickly
- BDU always gets a CC at ochavisual@un.org to follow up if needed

**User says they didn't get a Request ID**
- Check the Google Sheet — the row should still be there
- The Request ID is shown on screen immediately after submission

**Need to re-approve (user needs to re-download)**
- Change the status back to "Approved" using the dropdown — the user gets a new email

**Updating the Apps Script code**
- Edit in the Apps Script editor (Project URL above)
- The onEdit trigger runs from "Head" (latest saved code) — no redeployment needed for trigger changes
- For Web App changes: Deploy > Manage deployments > Edit (pencil) > Version: New version > Deploy

---

## Rebuilding from Scratch

If the system ever needs to be rebuilt (new account, new sheet, etc.):

1. Create a new Google Sheet with the column headers listed above
2. Add data validation on column I (Status) with dropdown options: Pending, Approved, Rejected
3. Go to https://script.google.com and create a new project
4. Paste the contents of `google-apps-script.js`
5. Update `SHEET_ID` with the new sheet's ID
6. Update `NOTIFY_EMAIL` if needed
7. Deploy as a Web App (Execute as: Me, Who has access: Anyone)
8. Authorize the script when prompted (it needs access to Sheets and Mail)
9. Copy the Web App URL and update `APPROVAL_API_URL` in `index.html`
10. Add a trigger: Function = `onStatusChange`, Event = From spreadsheet → On edit
11. Authorize the trigger when prompted
