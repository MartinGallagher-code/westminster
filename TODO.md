# TODO — Next Steps

## Product

1. **Configurable comparison page**
   - Let users configure which documents to compare side-by-side on a topic.
   - Consider presets such as “Westminster family” and “Continental Reformed”.
   - Support a custom selector for picking documents manually.

2. **BCO enrichment**
   - Add cross-references from the PCA Book of Church Order to WCF, WLC, and WSC where appropriate.
   - Strip General Assembly action-date footnotes if they cause display issues.
   - Add BCO material to comparison themes if it proves useful.

3. **Search refinement**
   - Add PostgreSQL search indexes if production search becomes slow.
   - Consider result snippets/highlighting once full-text ranking is stable.

## Operations

1. **Stripe supporter membership**
   - Complete `TODO_STRIPE.md`.
   - Confirm Render uses `STRIPE_PRODUCT_ID`, not a stale price-only configuration.
   - Test checkout, webhook handling, supporter badge display, and customer portal redirects.

2. **BCO update monitoring**
   - Periodically run `python manage.py check_bco_update`.
   - Update `data/pca_bco/version.json` when the PCA publishes a new edition.

3. **Release hygiene**
   - Update `CHANGELOG.md` for user-visible changes.
   - Update `HANDOFF.md` before ending substantial work sessions.
   - Keep completed implementation plans out of this file unless they become new follow-up work.
