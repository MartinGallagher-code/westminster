# /atlas — TODO

Open work on the Westminster Standards Atlas. Completed items are recorded in
the project `CHANGELOG.md` rather than kept here; this file lists what is left.

See [`README.md`](README.md) for what each layer holds, and
[`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) for how the app sits
inside Study Reformed.

## Where it stands

Populated: the 8-locus / 35-attribute ontology with baseline-plus-override,
39 heads of doctrine covering every WCF section and catechism question, 181
personas, 30 cruxes, 16 schools (7 Assembly parties, 9 receiving traditions),
and all six works in full — WCF (33 chapters), LC (196), SC (107), the
Directory for Public Worship (15), the Form of Presbyterial Church Government
(19), and the Sum of Saving Knowledge (14).

Working: cross-layer search, persona-to-crux reverse links, crux-to-crux "see
also", a quote of the day, and a 20-test invariant module
(`python manage.py test westminster_standards`) covering ontology drift,
attribute validity, slug uniqueness, and work structure.

## Content

1. **Transcription drift.** Diff the loaded text against a canonical print
   edition (FPP 1976, or the OPC web edition) to catch OCR and transcription
   errors. Several have already been found and fixed by hand; a systematic
   pass would be better than waiting to trip over the rest.

2. **Persona attributes are mostly uniform with the baseline.** Many personas
   inherit `WESTMINSTER_BASELINE_ATTRS` with no overrides. Where evidence
   exists, add overrides on the attributes the cruxes turn on — a divine's
   actual stance on hypothetical universalism, the third use, the Erastian
   question. Worth doing for the most active divines first.

3. **Bio thinness.** 38 personas are under 200 characters. Most are the
   obscure 1643-ordinance ministers and genuinely cannot be expanded without
   fabrication, which is not worth doing. A handful likely have substantive
   ODNB entries that would ground a real expansion; identifying which 5–10
   those are is the task.

4. **Legacy sections don't link to receiving traditions.** Each crux has a
   "Legacy" section naming traditions that are themselves schools in the
   Atlas. Hyperlink them.

## Features

5. **1646 vs 1788 side-by-side.** The American revision changed WCF XX.4,
   XXIII.3 and XXXI.2. Study Reformed already has a word-level diff view for
   Westminster/Savoy/1689; the same treatment would suit this.

6. **Dimension-pair intersections.** Which personas hold *both* Independent
   polity *and* hypothetical-universal atonement? The `dimension_pairs` route
   exists; the intersection query does not.

7. **Graph view.** A force-directed graph of personas, schools and cruxes as
   nodes with weighted edges. Would need a vendored D3 — the site serves no
   external assets, so this is a heavier lift than it looks.

8. **Visual elements.** An era-locator timeline over the 1643–1649 Assembly
   span; a map of where the divines came from; portrait placeholders where
   contemporary engravings exist and are public domain.

## Known non-issues

- **Four cruxes have empty `attribute_keys`** — "Pope as Antichrist", the
  Solemn League, the Self-Denying Ordinance, and the 1788 revision. This is by
  design: they are structural, polemical or procedural, and do not reduce to a
  position on one attribute the way the decree-order or polity cruxes do.
  Forcing an "antichrist" attribute onto the grid would be shoehorning. The
  detail page omits the ontology section when the list is empty.

- **`questions.py`, `controversies.py` and `cases.py` hold no rows.** They are
  kept for the shape the upstream project expects. The material they were
  meant to hold is in `cruxes.py`, which turned out to be the better structure
  for it.
