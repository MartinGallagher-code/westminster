# Changelog

All notable project changes should be recorded here. This project uses a simple
reverse-chronological changelog rather than formal release tags.

## 2026-06-10

### Changed

- Added a project handoff file so future work has a clear status, next-step, and validation trail.
- Refreshed README setup instructions to match the current Django settings layout and deployment data-loading pipeline.
- Reworked the project TODO file into a forward-looking backlog instead of mixing completed implementation notes with active work.
- Switched search toward PostgreSQL full-text search in production, with the existing SQLite-friendly fallback retained for local development and tests.
- Expanded search matching so generated topic/theme search links can match topic names and individual meaningful terms instead of requiring exact long-phrase matches.
- Updated Atlas links to open as external links with `noopener` protection.
- Removed the checked-in duplicate `* 2.*` artifact set from the repository working tree.

### Fixed

- Added a build-only `SECRET_KEY` fallback in `build.sh` so Render deploy builds can run Django management commands even when generated secrets are unavailable during build.
- Added a repo-level `.python-version` pin so Render uses Python 3.12 instead of its current Python 3.14 default when service environment settings are not applied.
- Enforced the active document-tradition filter in the see-also preview API so filtered-out documents no longer preview via direct API calls.
- Aligned the preview-filter test expectations with the intended site-wide filtering behavior.
- Fixed generated topic-name searches returning empty results when the topic label did not appear verbatim in question or answer text.
- Moved real-looking secret-key configuration out of shared base settings and into environment/development-specific settings.
