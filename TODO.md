# TODO — Next Steps

## Product

1. **Configurable comparison page** — _custom selector and presets implemented_
   - Done: custom document selector plus "Westminster Standards" and "Three Forms of Unity" presets.
   - Follow-up: consider per-topic deep-linking and saved/shareable custom comparisons.

2. **BCO enrichment** — _cross-references implemented_
   - Done: cross-references from the PCA Book of Church Order to WCF, WLC, and WSC (`load_bco_crossrefs`).
   - Strip General Assembly action-date footnotes if they cause display issues.
   - Add BCO material to comparison themes if it proves useful.
   - Expand the editorial cross-reference map to additional BCO chapters as needed.

3. **Search refinement**
   - Add PostgreSQL search indexes if production search becomes slow.
   - Consider result snippets/highlighting once full-text ranking is stable.

## Operations

1. **Support / donations**
   - The support page links out to Buy Me a Coffee (`buymeacoffee.com/martingallagher`).
   - Update the link in `templates/accounts/support.html` if the username changes.

2. **BCO update monitoring**
   - Periodically run `python manage.py check_bco_update`.
   - Update `data/pca_bco/version.json` when the PCA publishes a new edition.

3. **Release hygiene**
   - Update `CHANGELOG.md` for user-visible changes.
   - Update `HANDOFF.md` before ending substantial work sessions.
   - Keep completed implementation plans out of this file unless they become new follow-up work.
