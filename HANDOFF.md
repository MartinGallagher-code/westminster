# Handoff

## Current State

- Repository: `MartinGallagher-code/westminster`
- Local checkout: `/Users/martin/Documents/Study/westminster`
- App: Django 4.2 study site for Reformed standards, commentaries, proof texts, cross-references, notes/highlights, and supporter memberships.
- Deployment: Render via `render.yaml`, with production settings at `config.settings.production`.

## Most Recent Work

- Site-wide improvement pass (2026-08-23), in five commits on top of the Atlas integration work below. **Discovery:** the five Reformed confessions that were loaded but unreachable behind `tradition='other'` are published as their own collection; the Atlas's 432 pages are in the sitemap; search shows the matching phrase with the terms marked, and routes Scripture references to the Scripture index; comparison columns are readable on a phone and ordered oldest-first. **Study:** a memorisation deck with spaced repetition, Markdown export and search of a reader's own notes, printable small-group handouts, shareable custom comparisons, citation permalinks with BibTeX/RIS export, and a word-level diff between the Confession, Savoy and the 1689. **Production:** Sentry, a data-integrity CI job over the loaded corpus, a Postgres CI job, a GIN-indexed search vector, page caching for anonymous visitors, wider rate limiting, and an operations runbook with a rehearsed restore.
- Along the way: the password-reset form raised `NoReverseMatch` on submit (Django's default success URL is not namespaced), and the sitemap advertised comparison and doctrine URLs that 404 for crawlers. Both fixed with regression tests.


- Closed the remaining Atlas integration seams (2026-08-23). **One doctrine-head taxonomy:** the database previously carried 33 heads of its own (seeded from `data/westminster_ontology.json`) while the Atlas app carried 39 richer ones in `heads_of_doctrine.py`; only 8 slugs overlapped, so 25 of the 33 head chips on Study Reformed pages linked to `/atlas/heads/<slug>/` pages that 404'd. `load_westminster_ontology` now mirrors the Atlas's heads and derives every question-to-head link from the Atlas's coverage lists (verified against a full load: 39 heads, 575 links, every WCF/WLC/WSC item covered, zero broken chips); the JSON keeps only the loci, attributes, and hand-authored per-question attribute tags. The heads module is part of the load's version hash, so editing it re-triggers the loader. **Ontology-driven loci panel:** `catechism.atlas.topic_loci` reads the loaded ontology (question tags plus head links) and falls back to the Atlas's static mapping only when the ontology tables are empty — the old "tags are still sparse" bypass is gone. **Site-wide search:** search results now include an "Also in the Atlas" section over heads, cruxes, divines, and schools, matched by the new `westminster_standards/entity_search.py` (kept out of the ported `views.py` so it stays syncable).
- Fixed a live 404 (2026-08-23): `sitemap.xml` advertised `/compare/1689-baptist/of-church-government/`, which `CompareSetThemeView` 404s. A theme is only reachable if its whole comparison set is, but the per-theme tradition filter checked only the theme's own entries — and that theme's 1689/Savoy ranges are null, leaving it all-Westminster. `_comparison_themes_for_traditions` is now set-aware. Note the underlying cause: the Confessional Lineage and Pre-Westminster comparison sets are fully loaded but invisible on the live site, because the 1689, Savoy, Scots, Second Helvetic, and Irish Articles documents carry `tradition='other'` and `VALID_TRADITIONS` is `{westminster, three_forms_of_unity}`. Giving those documents a real tradition (and a filter toggle) would publish that material rather than hide it — a product decision, not a bug.
- Finished the Westminster Standards Atlas ontology (2026-07-01): added 32 more `doctrine_heads` (one per WCF chapter, 33 total, up from just "prolegomena") and tagged all 475 questions/sections across WSC (107), WLC (196), and WCF (172) with doctrine-head and ontology-attribute links — up from 6 hand-tagged examples. Generated via parallel review of the actual catechism/confession text, then validated (every attribute/head slug checked against the taxonomy, full coverage confirmed, no duplicates) and smoke-tested by actually running `load_westminster_ontology` against a populated test database. Attribute tagging intentionally leaves `attributes: []` where a question doesn't genuinely address one of the 35 fine-grained doctrinal dimensions, rather than forcing a loose fit — the `heads` link (one per question, tied to its WCF chapter topic) is complete for all 475 entries. This is a good-faith first full pass; spot-checking or refining individual attribute tags against the primary text would be reasonable future work.
- Site-wide cleanup pass (2026-07-01): fixed a hardcoded default admin password in `create_admin` (now reads `DJANGO_ADMIN_USERNAME`/`DJANGO_ADMIN_EMAIL`/`DJANGO_ADMIN_PASSWORD` env vars or generates a random one); narrowed a bare `except Exception: pass` in `BlockedUserMiddleware`; guarded against `ZeroDivisionError` in `HomeView`/`CatechismHomeView` if a catechism's `total_questions` is ever 0; added the missing "select at least two documents" guard to `CustomCompareThemeView` (present in `CustomCompareView` but not its sibling); made `load_standard_crossrefs` fail with a clear warning instead of an uncaught `KeyError` when run before the Westminster Standards are loaded; added `Question.DoesNotExist` guards to `load_fisher`/`load_bethune`/`load_fisher_hc`/`load_thelemann`/`load_ursinus`/`load_vanderkemp`/`load_whitmer`; guarded `load_hodge_outlines` against a required-FK crash if a chapter number ever falls outside the declared part ranges; removed the dead `load_vincent` command (pointed at a `data/vincent_commentary/` directory that never existed, silently creating an empty `CommentarySource` row every build — see TODO.md); fixed a dead auto-scroll-to-current-question feature in chapter mode (the `.chapter-mode-active` class was never applied by any template); hardened `main.js`'s tab-restore logic against a malformed/stale `localStorage` value breaking `querySelector`; corrected several OCR artifacts (duplicated words, digit-glued-into-word corruption, garbled Scripture verse citations) in the Hodge/Shaw/Ridgley/Watson/Fisher-Erskine/Westminster-Assembly-catechism-exposition source texts. Full audit also flagged (not fixed, needs real data re-sourcing): `data/pca_bco/version.json` is likely stale by up to two General Assembly cycles, and `data/westminster_ontology.json` is a mostly-unpopulated scaffold (1 of 8 loci tagged).
- Added editorial PCA BCO cross-references to the Westminster Standards: `data/pca_bco/bco_cross_references.json` maps ~30 doctrinally substantive BCO chapters to WCF chapters and WLC/WSC question ranges, loaded by the new `load_bco_crossrefs` command (wired into `build.sh` after `load_pca_bco`). These surface on BCO detail pages and, bidirectionally, as "See also in BCO" on WCF/WLC/WSC pages (capped at 8 per group by the existing view logic).
- Added comparison presets ("Westminster Standards", "Three Forms of Unity") to the custom comparison selector. `CompareIndexView` builds them via `_available_comparison_presets`, filtered to documents available in the active traditions; `compare.js` wires the preset buttons to pre-select checkboxes.

## Earlier Work

- Centralized Westminster Standards Atlas URL generation in `catechism/atlas.py`, backed by `WESTMINSTER_ATLAS_BASE_URL`.
- Replaced hardcoded Atlas template links with the shared `atlas_home_url` context value.
- Added ontology models for Atlas loci, attributes, doctrine heads, question-to-attribute tags, and question-to-head links.
- Added `data/westminster_ontology.json` with the eight Atlas loci, 35 attributes, one initial doctrine head, and opening WSC/WLC prolegomena mappings.
- Added `load_westminster_ontology` and wired it into `build.sh` after the Westminster source-text loaders.
- Added an Atlas placement panel on question/detail pages for local ontology chips, doctrine-head chips, and the contextual external Atlas route.
- Added focused tests for ontology loading and detail-page ontology rendering.

## Known Follow-Ups

- The Atlas app owns the doctrine-head taxonomy; add or rename heads in `westminster_standards/heads_of_doctrine.py`, never in `data/westminster_ontology.json` (which now holds only loci, attributes, and per-question attribute tags).
- The ontology is now fully tagged (WSC/WLC/WCF, 475 questions); if the upstream Atlas exports richer mappings later, reconcile against those rather than starting over.
- Decide whether the 1689/Savoy/pre-Westminster documents should get real traditions and a filter toggle, or stay gated; today they are loaded but unreachable.
- `westminster_standards/README.md` and `TODO.md` still describe the app's pre-port life (the tsmo mount, the `/puritans/` sister app, personas/schools as stubbed, DPW/FPCG/SSK text as missing). All are now inaccurate; worth a pass.
- Consider adding a Study Reformed doctrine-map/index page over `OntologyLocus` and `OntologyAttribute`.
- Consider adding a generated PostgreSQL search vector column or indexes if search volume grows.
- Verify Render has `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` set.
- Set `WESTMINSTER_ATLAS_BASE_URL` if the Atlas later moves under `study.site`.
- Add BCO cross-references and comparison-theme coverage when ready.

## Validation Notes

- `python3 -m pytest -q` passes: 380 passed, 5 skipped (the Postgres-only search tests). Against Postgres: 385 passed. `python3 manage.py test westminster_standards` passes: 37 tests.
- `python3 manage.py check_site_integrity` passes against a fully loaded database.
- Restore rehearsed against PostgreSQL 16: dump, drop, restore, `scripts/verify_restore.sh` green.
- `python3 -m pytest catechism/tests/test_models.py::test_atlas_url_normalizes_public_subproject_paths catechism/tests/test_commands.py::test_load_westminster_ontology_smoke catechism/tests/test_views.py::TestQuestionDetailView::test_renders_ontology_tags -q` passes: 3 passed.
- `python3 -m flake8 catechism/ accounts/ config/ --max-line-length=120 --exclude=migrations` passes.
- `python3 manage.py check` passes.
- `python3 manage.py makemigrations --check --dry-run` passes with no changes detected.
- Direct Atlas probes returned `200` for the Westminster Standards home, WSC Q1, WLC Q1, and WCF chapter 1 routes.
