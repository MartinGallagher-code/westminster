# PCA Book of Church Order (BCO)

## Source

- PDF: https://www.pcaac.org/wp-content/uploads/2025/08/BCO2025-1.pdf
- Edition: 2025 (52nd General Assembly, Chattanooga, TN)
- The BCO is updated at each General Assembly; track the version so we know when it changes

## Local Tracking

- PDF stored at `data/pca_bco/bco.pdf`
- Version info at `data/pca_bco/version.json` (url, sha256, downloaded_at, edition)
- Run `python manage.py check_bco_update` to check if the PDF has changed upstream

## Document Structure

The BCO has three main parts plus a preface:

1. **Preface** — The King and Head of the Church, Preliminary Principles, The Constitution Defined
2. **Part I — Form of Government** (chapters 1–26)
3. **Part II — The Rules of Discipline** (chapters 27–46, ch 44 vacated)
4. **Part III — The Directory for the Worship of God** (chapters 47–63)

Total: 432 sections across 62 active chapters + preface.

## Data Model

- `document_type = 'confession'`, `tradition = 'westminster'`
- `abbreviation = 'BCO'`, `slug = 'pca-bco'`
- One `Topic` per chapter (+ preface)
- One `Question` per numbered section, sequentially numbered 1–432

## Files

- `data/pca_bco/bco.pdf` — source PDF
- `data/pca_bco/bco_raw.txt` — extracted raw text
- `data/pca_bco/pca_bco.json` — structured JSON
- `data/pca_bco/version.json` — version tracking
- `catechism/management/commands/load_pca_bco.py` — load command
- `catechism/management/commands/check_bco_update.py` — update checker

## Implementation Steps

- [x] **1. Download and parse the PDF** — extracted via pdfplumber
- [x] **2. Structure the extracted text into JSON** — 432 sections in pca_bco.json
- [x] **3. Create the management command** — load_pca_bco.py with DataVersion support
- [x] **4. Add to deploy pipeline** — added to build.sh
- [x] **5. Version check script** — check_bco_update management command

## Update Log

- **2026-07-01**: Updated to the 2025 edition (amendments through the 52nd General Assembly). Revised text for 13-6 (ministers transferring into a Presbytery), 32-19 (representation in cases of process), and 43-1 (complaints filed during a pending judicial process). While updating, also fixed two pre-existing extraction bugs unrelated to the new edition: a stray Private Use Area glyph (``, a leaked bullet-point character) scattered through several section texts, and a mis-split paragraph that had been extracted as a spurious duplicate "32-19" section when it was actually the tail end of 38-1's text referencing "BCO 32-19" — it's now correctly appended to 38-1 and the phantom chapter-32 duplicate is gone (total sections dropped from 433 to 432 as a result).

## Known Gap: 53rd General Assembly (June 2026)

The data above reflects the last **officially published** edition (2025, through the 52nd GA). The 53rd General Assembly met in June 2026 and ratified 9 more amendment items that had been approved at the 52nd GA and subsequently passed by the presbyteries (items 2, 4, 6, 7, 8, 9, 10, 11, 12 per GA reporting) — including raising the threshold for presbyteries to request the General Assembly assume original jurisdiction in a judicial case from 2 to 18 presbyteries (20%), and a new requirement that congregations list Session and Diaconate members in their minutes. One further amendment (from Ascension Presbytery, on listing officers) was itself sent to presbyteries for approval and is not yet ratified.

These changes are constitutionally in effect but **pcaac.org has not yet published a 2026 edition PDF** codifying them (checked 2026-07-01; still serving `BCO2025-1.pdf`). Deliberately not reflected in `pca_bco.json` — the exact section text should come from the official reprint, not paraphrased from news/blog reporting of the Assembly's actions. Re-run `check_bco_update`, and update this data, once the 2026 edition PDF is published.

## Future Work

- [x] Add cross-references to WCF, WLC, and WSC — see `data/pca_bco/bco_cross_references.json` and `load_bco_crossrefs`
- Strip GA action date footnotes if they cause display issues
- Add to comparison themes if applicable
- Expand the editorial cross-reference map to additional BCO chapters as needed
