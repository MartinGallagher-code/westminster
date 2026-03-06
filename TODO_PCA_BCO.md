# PCA Book of Church Order (BCO)

## Source

- PDF: https://www.pcaac.org/wp-content/uploads/2024/08/BCO-2024-1.pdf
- Edition: 2024 (51st General Assembly, Richmond, VA)
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

Total: 433 sections across 62 active chapters + preface.

## Data Model

- `document_type = 'confession'`, `tradition = 'westminster'`
- `abbreviation = 'BCO'`, `slug = 'pca-bco'`
- One `Topic` per chapter (+ preface)
- One `Question` per numbered section, sequentially numbered 1–433

## Files

- `data/pca_bco/bco.pdf` — source PDF
- `data/pca_bco/bco_raw.txt` — extracted raw text
- `data/pca_bco/pca_bco.json` — structured JSON
- `data/pca_bco/version.json` — version tracking
- `catechism/management/commands/load_pca_bco.py` — load command
- `catechism/management/commands/check_bco_update.py` — update checker

## Implementation Steps

- [x] **1. Download and parse the PDF** — extracted via pdfplumber
- [x] **2. Structure the extracted text into JSON** — 433 sections in pca_bco.json
- [x] **3. Create the management command** — load_pca_bco.py with DataVersion support
- [x] **4. Add to deploy pipeline** — added to build.sh
- [x] **5. Version check script** — check_bco_update management command

## Future Work

- Add cross-references to WCF, WLC, and WSC
- Strip GA action date footnotes if they cause display issues
- Add to comparison themes if applicable
