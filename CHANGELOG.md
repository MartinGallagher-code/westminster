# Changelog

All notable project changes should be recorded here. This project uses a simple
reverse-chronological changelog rather than formal release tags.

## 2026-07-02

### Fixed

- Fixed low-contrast Atlas text on the light theme. The crux outcome badges, the persona active-obedience override marker, the school override pill, and the "planned" works pill used the Atlas's original bright accent colours as text, which were nearly invisible on Study Reformed's light background. They now use theme-aware "ink" colours (dark on light, bright on dark) via `--ws-ink-*` variables.
- Fixed broken Atlas links from the "Ontology placement" doctrine-head chips (e.g. on `/wcf/sections/14`). The database's Confession-chapter heads (`eternal_decree`) and the Atlas's finer systematic heads (`the-eternal-decree`) use different slugs, so 25 of 33 head chips pointed at non-existent Atlas pages. `DoctrineHead.get_atlas_url` now links to the specific Atlas head page when one exists and otherwise falls back to the head's locus page, so a head chip never 404s.

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