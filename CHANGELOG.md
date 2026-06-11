# Changelog

All notable project changes should be recorded here. This project uses a simple
reverse-chronological changelog rather than formal release tags.

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