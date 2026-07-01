# /westminster_standards — TODO

Honest assessment of where the subproject stands and how to improve it.
Ordered roughly by impact.

## What's already solid

- 8-locus / 35-attribute ontology with the baseline + override pattern
- 181 personas, with bios fleshed out from the historical record where
  material exists (truly thin county-minister entries left short rather
  than padded)
- 30 cruxes with background, parties, outcomes, confessional language,
  and legacy sections
- Clean URL structure; visual identity consistent with the puritans atlas
- `WESTMINSTER_BASELINE_ATTRS` validated at import time
- Heads of doctrine carry ontology `attribute_keys`; every WCF section,
  catechism question, and directory section is tagged (via its covering
  heads) with the ontology attributes it bears on, rendered as chips that
  link to the Westminster baseline value

## Highest-impact gaps

### 1. The Standards' actual text — partially done
Loaded the public-domain text via the NonlinearFruit/Creeds.json
corpus and built the work/chapter/question routes. The cruxes still
quote snippets inline rather than linking into the loaded chapters.

- [x] Full text of the Westminster Confession (33 chapters, with proofs)
- [x] Full text of the Larger Catechism (196 Q&As, with proofs)
- [x] Full text of the Shorter Catechism (107 Q&As)
- [ ] Full text of the Directory for Public Worship (1645)
- [ ] Full text of the Form of Presbyterial Church Government (1645)
- [ ] Full text of the Sum of Saving Knowledge (1650)
- [x] Hyperlink the cruxes' confessional-language quotes into the full text
- [x] Reverse index: each WCF chapter and catechism question shows the
      cruxes that bear on it
- [ ] Diff the loaded text against a canonical print edition (FPP 1976
      or the OPC web edition) to catch transcription drift

### 2. Personas don't link to cruxes — done
Each persona detail page now shows the cruxes in which they appear as
a party, with party name and position. 51 of 181 personas have at
least one crux appearance.

- [x] On each persona detail page, list the cruxes in which the persona
      appears as a party (with their position)

### 3. The Schools layer — done
16 schools populated (7 Assembly parties + 9 receiving traditions),
each with complete 35-attribute profile, anchor personas, and
description. Views, URLs, templates, nav link, and 4 invariant tests
all in place.

- [x] Populate `schools.py` with the Assembly parties (~8-12 schools)
- [x] Each school: complete 35-attribute `attrs` profile, anchor
      personas, description
- [x] Add `schools_list` + `school_detail` views
- [x] Link personas to their primary school

## Medium-impact

### 4. Receiving traditions — done (merged into schools layer)
9 receiving traditions added as schools with `period='receiving-tradition'`:
Savoy 1658, 1689 Particular Baptists, 1788 American revision, Free
Church 1843, Reformed Presbyterian Covenanters, Marrow Men, Cumberland
Presbyterians, OPC 1936, PCA 1973.

- [x] Add receiving traditions as a layer (merged with schools)
- [x] Each tradition: how it relates to the 1646 Standards, its
      revisions, its current standing
- [ ] Hyperlink the cruxes' "Legacy" sections into the relevant
      receiving tradition

### 5. Cross-layer search — done
Full-text substring search across all layers: personas, cruxes,
schools, WCF chapters, and catechism Q&As. Search box in the nav bar.

- [x] Add `/westminster_standards/search/?q=…` endpoint
- [x] Simple substring-match across persona name/bio, crux
      title/background/summary, work text

### 6. Comparison views — partially done
Persona-vs-persona comparison is live. Remaining items are lower
priority.

- [ ] 1646 vs 1788 side-by-side text comparison
- [x] Persona-vs-persona ontology comparison
- [ ] Dimension-pair intersection views (which personas hold *both*
      Independent polity *and* hypothetical-universal atonement?)

### 7. Some cruxes don't map onto the 35-attribute grid — resolved (by design)
The "Pope as Antichrist", Solemn League, Self-Denying Ordinance, and
1788 American revision cruxes have empty `attribute_keys`. This is
correct: these are structural/polemical/procedural cruxes that don't
reduce to a single attribute-value position in the way that (e.g.)
the decree-order or polity cruxes do. Adding a forced "antichrist"
attribute would be shoehorning a crux into the grid where it doesn't
naturally fit. The crux detail page already renders gracefully when
`attribute_keys` is empty — it simply omits the "Ontology placement"
section.

- [x] Decide: accept structural cruxes with no attribute mapping
- [x] Crux detail page renders gracefully when `attribute_keys` is empty

## Polish

### 8. Bio thinness audit
38 personas are under 200 chars. Some (the truly obscure 1643-ordinance
ministers) genuinely can't be expanded without fabrication. A handful
might be substantively documentable with more careful DNB / ODNB
research.

- [ ] Audit each <200-char persona; identify which 5-10 have
      substantive ODNB entries that could ground further expansion
- [ ] Leave the rest as short factual entries (no fabrication)

### 9. Data invariant tests — done
20-test invariant module in `tests.py`. Catches: ontology drift,
baseline coverage, persona attrs key/value validity, duplicate slugs,
crux locus/attribute/persona reference validity, outcome values,
work structure (33 chapters, 196 LC, 107 SC), contiguous numbering,
citation-parser resolution coverage. Runs with
`python manage.py test westminster_standards` in <10ms.

- [x] Persona `attrs` keys are all valid `(dim, attr)` pairs
- [x] Persona `attrs` values are all real value labels for that
      attribute
- [x] Crux `persona_slugs` all exist in `PERSONAS`
- [x] Crux `attribute_keys` all exist in the ontology (or are empty)
- [x] No duplicate persona slugs, no duplicate crux slugs
- [x] WCF/LC/SC structure complete and contiguous

### 10. Cross-references between cruxes — done
All 30 cruxes have `related_crux_slugs` linking doctrinally or
procedurally connected cruxes. "See also" on every crux detail page.

- [x] Add `related_cruxes` field to crux dicts
- [x] Render "see also" section on crux detail pages

### 11. Personas' `attrs` are mostly uniform with the baseline
Many personas inherit the baseline with no overrides. They could be
enriched with positions on the cruxes (e.g., a persona's specific
stance on hypothetical universalism, on the third use, on the
Erastian question).

- [ ] Where evidence exists, add overrides on the relevant cruxes'
      attributes — at least for the most active divines

## Nice-to-have

### 12. Graph view
D3 force-directed graph like the puritans atlas, showing personas,
schools, and cruxes as nodes with weighted edges.

- [ ] Port the puritans `graph` view and template

### 13. Proof-text apparatus
The Standards include extensive proof-text scriptural apparatus. Part
of the original document and an important polemical layer.

- [ ] Once full text is added, include proof texts inline

### 14. Visual elements
- [ ] Era-locator timeline (1640s decade, 1643-1649 Assembly span)
- [ ] Map of where divines came from (Scotland, English counties)
- [ ] Portrait placeholders (where contemporary engravings exist)

### 15. Mobile responsiveness
- [ ] Test all templates at narrow widths; the ontology grid and
      cruxes grid may need refinement

### 16. Quote-of-the-day — done
Daily rotating text on the home page, seeded by today's date. Pool
draws from all 107 Shorter Catechism Q&As and from short, self-
contained WCF sections (200-700 chars). Clicks through to the
chapter or question detail page.

- [x] Randomly select a Q&A or chapter excerpt for the home page

## Priorities

If picking one thing to do next: **#1 (full WCF/LC/SC text in
`works.py`)**. It's the biggest gap and was the original brief.

If picking a small, high-payoff thing: **#2 (reverse-link cruxes from
persona pages)** — small code change, large UX improvement.
