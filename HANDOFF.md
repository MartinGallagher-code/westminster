# Handoff

## Current State

- Repository: `MartinGallagher-code/westminster`
- Local checkout: `/Users/martin/Documents/Study/westminster`
- App: Django 4.2 study site for Reformed standards, commentaries, proof texts, cross-references, notes/highlights, and supporter memberships.
- Deployment: Render via `render.yaml`, with production settings at `config.settings.production`.

## Most Recent Work

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

- Expand `data/westminster_ontology.json` with fuller question/chapter-to-ontology mappings as the Atlas exports become available.
- Consider adding a Study Reformed doctrine-map/index page over `OntologyLocus` and `OntologyAttribute`.
- Consider adding a generated PostgreSQL search vector column or indexes if search volume grows.
- Verify Render has `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` set.
- Set `WESTMINSTER_ATLAS_BASE_URL` if the Atlas later moves under `study.site`.
- Add BCO cross-references and comparison-theme coverage when ready.

## Validation Notes

- `python3 -m pytest -q` passes: 172 passed, 19 warnings.
- `python3 -m pytest catechism/tests/test_models.py::test_atlas_url_normalizes_public_subproject_paths catechism/tests/test_commands.py::test_load_westminster_ontology_smoke catechism/tests/test_views.py::TestQuestionDetailView::test_renders_ontology_tags -q` passes: 3 passed.
- `python3 -m flake8 catechism/ accounts/ config/ --max-line-length=120 --exclude=migrations` passes.
- `python3 manage.py check` passes.
- `python3 manage.py makemigrations --check --dry-run` passes with no changes detected.
- Direct Atlas probes returned `200` for the Westminster Standards home, WSC Q1, WLC Q1, and WCF chapter 1 routes.
