# Changelog

All notable project changes should be recorded here. This project uses a simple
reverse-chronological changelog rather than formal release tags.

## 2026-08-24

### Changed

- Made the memorisation deck findable. It shipped behind a login wall whose only entry point was a navbar link that signed-out visitors never saw, so nobody who did not already know about it could find it. `/accounts/memorize/` now explains itself to signed-out visitors — what it is, how the schedule works, and what can be memorised — instead of bouncing them to a login form, and is listed in the sitemap. The navbar offers it to everyone; the study desk shows what is due with a link through; the home page carries a "Memorise the Catechism" card; and catechism and topic pages offer to add a whole document or one topic at a time. Confessions are deliberately left out of the shortcuts — memorising prose section by section is a different exercise from a catechism's questions and answers.

### Added

- Made a divine's departures from the Confession clickable on Atlas persona pages. Every attribute value now links to the page explaining that position — what it is, who else held it, what it was argued against — and where a persona departs from the Westminster baseline, the Confession's own position is named inline and linked beside it. John Arrowsmith's "Hypothetical-Universal ≠" now reads "Hypothetical-Universal ≠ Westminster: Particular", both linked. The school and comparison pages already did this; the persona page, where the departures actually live, did not.
- Added every answer under one topic to the deck in a single action (`/accounts/memorize/add-topic/<pk>/`), which is the unit a reader working through a catechism actually uses.

## 2026-08-23 (later still)

### Changed

- Vendored Bootstrap, Bootstrap Icons and both typefaces under `static/vendor/`, served by WhiteNoise from this origin. They previously loaded from `cdn.jsdelivr.net` and Google Fonts, which made the entire design contingent on two other companies being reachable — with those blocked the site rendered as unstyled markup — and disclosed every visitor's IP address to both on every page load. Licences travel with the code (MIT for Bootstrap and its icons, the SIL Open Font License for the fonts). CI now runs `collectstatic` with the production storage, so a dangling font reference fails there rather than on deploy.

## 2026-08-23 (later)

### Added

- **Memorisation deck.** Signed-in readers can add an answer from its own page or a whole catechism at once, and review what is due. Scheduling is an SM-2 variant (`accounts/scheduling.py`): recall widens the gap (1, 6, 15, 38, 95 days…), a miss returns it tomorrow with reduced ease. The deck reports what is due, what is being learned, and what is known.
- **Notes export and search.** Every note, annotation and highlight downloads as one Markdown file grouped by document and question, with absolute links back. The study desk now searches your own material too.
- **Printable small-group handout** for any question or chapter: the text, proof texts with their verses, where the other standards treat the same ground, leader's notes excerpted from the commentators, and discussion prompts built from that passage's own proofs, parallels and Assembly cruxes.
- **Citations.** `/cite/wcf/3.4/` resolves the reference a reader actually writes and redirects to the canonical page; the same reference exports as BibTeX or RIS.
- **Cross-edition diff.** Parallel chapters of the Confession, Savoy and 1689 diffed word by word, ignoring punctuation and capitalisation so the substantive revisions surface.
- **Transcription check.** `check_transcription` compares the loaded text against the Atlas's independently sourced copy and ranks the divergences.
- **Data-integrity CI job.** `check_site_integrity` loads the real corpus and asserts what only a populated database can answer — every sitemap URL fetchable by an anonymous crawler, every Atlas page and chip resolving, every Westminster item carrying a doctrine head. A second CI job runs the whole suite against Postgres, which nothing previously did.
- **Sentry** error monitoring behind `SENTRY_DSN`, with PII off.
- **Operations runbook** (`docs/OPERATIONS.md`) covering backups, a rehearsed restore procedure with `scripts/verify_restore.sh`, and health-check monitoring.

### Changed

- The Postgres search matches a stored, GIN-indexed `search_vector` column instead of building a tsvector per row per query.
- Read-only pages are cached for anonymous visitors, keyed by path and active collections; signed-in readers are never served from or written to the cache.
- Rate limiting extended to password reset, search, and the new endpoints.
- `build.sh`'s load sequence moved to `scripts/load_data.sh` so deploys and CI load identically.

### Fixed

- Submitting the password-reset form raised `NoReverseMatch`: Django's default success URL is not namespaced.

## 2026-08-23

### Added

- Site search now shows the part of a result that matched, with the search terms marked, instead of the opening words of the question and answer.
- Typing a Scripture reference into the search box ("Rom 8:30", "1 Cor 13") goes to that book's page in the Scripture index, narrowed to the chapter, with a link back to a plain text search. Only references with a chapter number are recognised, so searching for "acts" or "job" still searches the text.
- Comparison pages gained a document switcher on narrow screens. The columns previously stacked below `lg`, turning a side-by-side reading into three documents in sequence; the switcher shows one at a time in place so you can flip between them without losing your position.
- The Atlas is now in `sitemap.xml` — 432 pages (personas, cruxes, schools, heads of doctrine, and every locus, attribute and value page) that were previously unindexed.

### Changed

- Accessibility: the skip link now targets a real `<main>` landmark that can take focus and is styled without depending on Bootstrap's utility classes; the document-collection toggles expose their pressed state; and the eight Atlas locus accents are passed to CSS as a custom property so the stylesheet can darken them for the light theme, where the pastels were too faint to read as a boundary.

## 2026-08-23

### Added

- Published the five Reformed confessions that were loaded but unreachable. The 1689 London Baptist Confession, Savoy Declaration, Scots Confession, Second Helvetic Confession, and Irish Articles were all created with the default tradition (`other`), which every view gates on, so the documents and the two comparison sets built on them — Confessional Lineage and Pre-Westminster Confessions — could not be reached from anywhere on the site. They now form a third document collection, **Reformed Confessions**, with its own filter toggle; a data migration moves the existing rows. Also added "Confessional Lineage" and "Pre-Westminster" quick-start presets to the custom comparison selector.

### Changed

- Comparison columns are ordered oldest-document-first instead of alphabetically by abbreviation, which had put the 1689 before the 1646 Confession it revises.
- Comparison theme pages name the documents in the set that have no parallel section for that theme, rather than silently showing a narrower table — the omission (the 1689 has no chapter answering WCF XXXI) is part of what the comparison shows.

### Fixed

- `sitemap.xml` advertised doctrine and comparison pages that 404 for search engines. Those pages are gated on the visitor's active collections and a crawler sends no filter cookie, but the sitemap was built over every valid tradition — so a theme carried only by the 1689 and Savoy (e.g. "Of the Gospel") was advertised and then 404'd. The sitemap is now built over the anonymous defaults.

## 2026-08-23

### Fixed

- Stopped the sitemap advertising comparison URLs that 404. A theme inside a comparison set that references an unsupported tradition — e.g. the Confessional Lineage set's "Of Church Government", whose 1689 and Savoy ranges are null, leaving it with only a Westminster entry — passed the per-theme tradition filter and was listed in `sitemap.xml`, while `CompareSetThemeView` gates the whole *set* and returned 404. `_comparison_themes_for_traditions` is now set-aware, matching `_comparison_sets_for_traditions`, so `/compare/1689-baptist/of-church-government/` is no longer advertised or linked from the doctrine index.

### Changed

- Unified the doctrine-head taxonomy on the Atlas. The database previously carried its own 33 heads (one per Confession chapter, seeded from `data/westminster_ontology.json`) alongside the Atlas app's 39 richer heads in `heads_of_doctrine.py`; the two shared only 8 slugs, so 25 of the 33 head chips on Study Reformed question pages linked to Atlas pages that did not exist. `load_westminster_ontology` now mirrors the Atlas's heads into the database and derives every question-to-head link from the Atlas's own coverage lists, and the duplicate `doctrine_heads` block and per-question `heads` field are dropped from the JSON, which keeps the loci, attributes, and the hand-authored per-question attribute tags. Every Confession section and catechism question now carries at least one head, and every head chip resolves to a real `/atlas/heads/<slug>/` page.
- Made the "Loci treated here" panel read the loaded ontology. `catechism.atlas.topic_loci` previously bypassed the database because the per-question tags were sparse; they no longer are, so it now derives loci from the question tags and head links and falls back to the Atlas's static chapter/question mapping only when the ontology has not been loaded.

### Added

- Site search now reaches the Atlas. Search results show an "Also in the Atlas" section covering the layers the standards' text has no counterpart for — heads of doctrine, cruxes, divines, and schools — grouped by layer, capped per layer, and linking through to the Atlas's own search for the rest. Matching lives in the new `westminster_standards/entity_search.py` so the ported `views.py` stays untouched for upstream syncs.

## 2026-07-02

### Changed

- Made the Westminster Standards Atlas feel native to Study Reformed. The Atlas's own dark section sub-nav is replaced by an **Atlas dropdown** in the site navbar that lists every Atlas section (Ontology, Personas, Cruxes, Heads of Doctrine, Schools, Works, Compare, Intersections, Search). Atlas pages now use the site's standard layout — a Bootstrap breadcrumb (Home / Atlas / …), an `h1` + lead + rule page header, and cards styled to match Study Reformed's (`--wm-*` surfaces, `0.5rem` radius, subtle shadow) — instead of the ported standalone chrome. The eight locus accent colours are retained.

## 2026-07-01

### Added

- Ported the Westminster Standards Atlas into Study Reformed as the self-contained `westminster_standards` app, mounted at `/atlas/`. Brings the full ontology (8 loci, 35 attributes with contested-value spreads), 181 personas, 30 cruxes, 16 schools, and 39 heads of doctrine on-site as native pages, rather than linking out to ontologicalatlas.com. The app is pure-Python (no models/migrations). Mounted ahead of the catechism catch-all route so `/atlas/...` is not shadowed. (Phase 1 of the Atlas merge.)

### Changed

- Unified the doctrine taxonomies and added chapter/topic reverse links (Phase 4). The hand-authored comparison themes (tagged with a classical systematic-theology locus — Prolegomena, Theology Proper, Hamartiology, Eschatology, …) now crosswalk to the eight Westminster Atlas loci via `catechism.atlas.comparison_locus_atlas`: the Doctrine index shows an "Atlas: <locus>" link on each locus group, and comparison-theme pages link to their nearest Atlas locus. Confession chapter and catechism topic pages gain a "Loci treated here" panel — driven by the Atlas's comprehensive chapter/question→locus mapping (`catechism.atlas.topic_loci`), so it is populated for every Westminster chapter/topic rather than only the sparsely tagged questions — whose locus chips link into the Atlas. (The upstream `questions`/`controversies`/`cases` layers are empty stubs and are left for dedicated authoring.)

- Cross-linked the Atlas with the rest of Study Reformed (Phase 3). The on-page "Ontology placement" chips on Westminster question/chapter pages — and the "Open Atlas" / "Doctrine Map" links on the home, compare, and comparison-theme pages — now resolve to the internal `/atlas/` pages instead of opening ontologicalatlas.com in a new tab (`catechism/atlas.py` now defaults to the `/atlas/` mount; `WESTMINSTER_ATLAS_BASE_URL` can still point back at the public deployment). The Atlas's own duplicate full-text pages for the Confession chapters and catechism questions now redirect to Study Reformed's canonical pages (which carry commentary, proof texts, cross-references, and notes), via a new `westminster_standards/bridge.py`; the Directory for Public Worship, Form of Presbyterial Church Government, and Sum of Saving Knowledge — which Study Reformed does not host — keep their Atlas pages. The redundant per-question "Open in Atlas" button (which would have redirected back to the same page) is replaced with a "Browse the Atlas" link to the ontology.

- Integrated the Atlas visually into Study Reformed (Phase 2). The Atlas templates now extend the site `base.html`, inheriting the shared navbar, footer, and light/dark/colour-scheme switching. The Atlas's standalone design tokens (`--bg-*`, `--text-*`, `--gold`, `--font-*`, …) are re-mapped onto Study Reformed's `--wm-*` tokens in `static/westminster_standards/atlas-theme.css`, so the Atlas follows the site theme with no per-page rework; the eight locus accent colours are retained. The Atlas's own navigation is kept as a section sub-nav beneath the site navbar. The navbar "Atlas" link now points to the internal `/atlas/` home instead of opening ontologicalatlas.com in a new tab. (The foreign core stylesheet vendored in Phase 1 is dropped in favour of the token bridge.)

## 2026-06-19

### Changed

- Replaced the Stripe-powered supporter membership with a Buy Me a Coffee link (`buymeacoffee.com/martingallagher`). Removed the Stripe checkout, customer portal, and webhook handling along with the `SupporterSubscription` model, the supporter badge, and all Stripe configuration (settings, environment variables, `render.yaml`, and the `stripe` dependency).

### Added

- Added editorial cross-references from the PCA Book of Church Order to the Westminster Standards, seeded from `data/pca_bco/bco_cross_references.json` via the new `load_bco_crossrefs` command (wired into `build.sh` after the BCO load). BCO chapters now link to the relevant WCF chapters and WLC/WSC questions, and those standards show the reverse "See also in BCO" references.
- Added quick-start presets ("Westminster Standards", "Three Forms of Unity") to the custom comparison selector. Presets are filtered to the documents available in the active traditions and pre-select the matching documents for refinement before comparing.

## 2026-06-11

### Added

- Added a configurable Westminster Standards Atlas bridge via `WESTMINSTER_ATLAS_BASE_URL`.
- Added local ontology models for Atlas loci, attributes, doctrine heads, and question mappings.
- Added `load_westminster_ontology` plus `data/westminster_ontology.json` to seed the eight Atlas loci, 35 attributes, and initial prolegomena question tags.
- Added an Atlas placement panel to Westminster detail pages so local ontology tags and doctrine heads appear inside Study Reformed.

### Changed

- Centralized public Atlas links through the shared Atlas helper and context processor.
- Included the ontology loader in `build.sh` after the Westminster source texts load.

## 2026-06-10

### Changed

- Restored a code-level development `SECRET_KEY` fallback in shared settings while keeping production tied to the real environment secret.
- Added a project handoff file so future work has a clear status, next-step, and validation trail.
- Refreshed README setup instructions to match the current Django settings layout and deployment data-loading pipeline.
- Reworked the project TODO file into a forward-looking backlog instead of mixing completed implementation notes with active work.
- Switched search toward PostgreSQL full-text search in production, with the existing SQLite-friendly fallback retained for local development and tests.
- Expanded search matching so generated topic/theme search links can match topic names and individual meaningful terms instead of requiring exact long-phrase matches.
- Updated Atlas links to open as external links with `noopener` protection.
- Removed the checked-in duplicate `* 2.*` artifact set from the repository working tree.

### Fixed

- Added a build-only `SECRET_KEY` fallback in `build.sh` so Render deploy builds can run Django management commands even when generated secre