# PCA Book of Church Order (BCO)

## Source

- Current edition: **2026**, including amendments approved up to and including
  the 53rd General Assembly (Louisville, Kentucky, June 22–26, 2026).
- PDF: https://www.pcaac.org/wp-content/uploads/2026/07/BCO_2026.pdf, linked
  from https://www.pcaac.org/bco/ ("Download BCO PDF").
- The PCA publishes each edition at a **new URL**. `version.json` records the
  URL and SHA-256 of the PDF the data was parsed from.

## Copyright

The PDF carries this notice (2026 edition, p. 2):

> This publication is intended for the work and mission of the Church. It may
> not be reproduced, stored in a retrieval system, transmitted, or made
> available to others in any form or by any means without the prior written
> permission of the Stated Clerk of General Assembly. Publication of any
> commentary or other reference work, including electronic resources and AI
> models, must include notice of prior written permission from the Stated
> Clerk for use of text from this document.

The site publishes the full text. **Written permission from the Stated Clerk
should be on file**, and the notice of that permission should be shown on the
BCO pages once it is. Until then the BCO's description carries the copyright
line from the PDF. The PDF itself is not committed (`.gitignore`).

## Updating to a new edition

1. `python manage.py check_bco_update` — reads the PCA's BCO page and reports
   whether the linked PDF differs from the one in `version.json`
   (`--fail-if-outdated` exits non-zero, for a scheduled check).
2. Download the PDF it names.
3. `python scripts/parse_pca_bco.py BCO.pdf --url <that URL>` — rewrites
   `data/pca_bco/pca_bco.json`, `data/pca_bco/version.json` and
   `data/pca-bco_proof_texts.json`. It refuses to write anything if the
   structure does not validate (chapters 1–63, sections consecutive, no
   running headers or private-use glyphs, no section swallowed by another,
   every footnote placed).
4. Diff the JSON against the previous edition. The amended sections should be
   exactly those listed for the year on p. 4 of the PDF.
5. Deploy. `load_pca_bco` updates sections in place by reference, so readers'
   notes and the cross-references survive; `load_bco_crossrefs` and
   `build_scripture_index` rebuild because their inputs changed.

## How the data is shaped

- `pca_bco.json`: `preface` (Preface I–III), then `parts`, each with
  `chapters` and their `sections`. A section has `number` ("21-4"), `text`
  (paragraphs separated by a blank line, without the leading number), and
  optionally `title` (a heading printed with the number: 21-4 "Ordination
  Requirements and Procedures") or `division` (an unnumbered heading printed
  above it: "A. Mission Churches" above 5-1). Part III carries the
  `introduction` the Third General Assembly adopted to preface the Directory
  for Worship. Footnotes are appended to their section as "Note: …".
- `pca-bco_proof_texts.json`: Scripture cited inline in each section, keyed
  by reference. Loaded as the sections' proof texts, so the Scripture index
  covers the BCO.
- `bco_cross_references.json`: editorial links from BCO chapters to WCF
  chapters and WLC/WSC questions (`load_bco_crossrefs`).

## How it is loaded

- `Catechism(slug='pca-bco', uses_native_references=True)`; one `Topic` per
  chapter ("Chapter 1: The Doctrine of Church Government"), plus "Preface" and
  "Preface to the Directory for Worship"; one `Question` per section with
  `reference` set to the printed reference. 435 sections in the 2026 edition.
- `Question.display_number` returns the reference, so the site, citations
  (`/cite/pca-bco/21-4/`, `/cite/pca-bco/preface-ii/`) and handouts all say
  "BCO 21-4". The sequential `number` (used in `/pca-bco/sections/<n>/`) shifts
  whenever a section is inserted; the `/cite/` URL is the stable link.

## Update log

- **2026-11-02**: Rebuilt from the 2026 edition with a new parser. Picked up
  the 53rd GA's amendments (12-3, 18-2, 24-1, 29-1, 31-10, 35-9, 36-4, 36-5,
  new 36-8, 41-3, 42-2) and fixed extraction faults in the previous data:
  chapter titles appended to the last section of the chapter before (6-4,
  15-6, 18-8, 19-6, 22-6, 24-5, 26-6, 27-5, 38-4, 43-10, 47-9, 49-4); the
  Directory for Worship's preface appended to 46-8; 56-6 merged into 56-5;
  the 36-4 sentence of suspension missing; footnotes on the ordination and
  installation questions attached to the wrong sections; every section stored
  as hard-wrapped PDF lines with its lists run together; chapter titles
  truncated (34, 39) or out of date (19, 23, 28, 56).
- **2026-07-01**: Updated to the 2025 edition (52nd GA).

## Future work

- Show the Stated Clerk's permission notice on BCO pages once permission is
  obtained (see Copyright above).
- Expand the editorial cross-reference map to further chapters as needed.
- Add BCO material to comparison themes if it proves useful.
