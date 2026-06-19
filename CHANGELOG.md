# Changelog

All notable project changes should be recorded here. This project uses a simple
reverse-chronological changelog rather than formal release tags.

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