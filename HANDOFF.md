# Handoff

## Current State

- Repository: `MartinGallagher-code/westminster`
- Local checkout: `/Users/martin/Documents/Study/westminster`
- App: Django 4.2 study site for Reformed standards, commentaries, proof texts, cross-references, notes/highlights, and supporter memberships.
- Deployment: Render via `render.yaml`, with production settings at `config.settings.production`.

## Most Recent Work

- Added `CHANGELOG.md` and this `HANDOFF.md`.
- Updated `TODO.md` so it tracks only active/future work.
- Updated `README.md` to reflect the current settings module, clone URL, data load commands, and operational notes.
- Enforced active tradition filtering in `/api/question/<pk>/preview/`.
- Added PostgreSQL full-text search for production while preserving SQLite fallback behavior.
- Expanded search matching to include topic names and tokenized terms, which fixes generated topic/theme search links that previously returned empty results for long labels.
- Updated Atlas anchors to open as external links with `target="_blank"` and `rel="noopener noreferrer"`.
- Added a build-only `SECRET_KEY` placeholder in `build.sh` to fix Render builds where generated service secrets are not exposed during build.
- Added `.python-version` to pin Render/native Python selection to Python 3.12 when dashboard/blueprint environment variables are not applied.
- Removed duplicate Finder/iCloud-style `* 2.*` files from the working tree.
- Replaced the shared hardcoded Django secret with environment-based production settings and an explicit development-only fallback.

## Known Follow-Ups

- Run the full test suite before merging: `pytest`.
- Run lint and migration checks before merging: `flake8 catechism/ accounts/ config/ --max-line-length=120 --exclude=migrations` and `python manage.py makemigrations --check --dry-run`.
- Consider adding a generated PostgreSQL search vector column or indexes if search volume grows.
- Verify Render has `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `STRIPE_PRODUCT_ID`, and Stripe webhook variables set.
- Complete the external Stripe dashboard checklist in `TODO_STRIPE.md`.
- Add BCO cross-references and comparison-theme coverage when ready.

## Validation Notes

- `python3 -m pytest -q` passes: 162 passed, 19 warnings.
- `python3 -m pytest catechism/tests/test_views.py::TestSearchView catechism/tests/test_tradition_filter.py::TestSearchViewFilter -q` passes: 9 passed.
- `python3 -m flake8 catechism/ accounts/ config/ --max-line-length=120 --exclude=migrations` passes.
- `python3 manage.py check` passes.
- `python3 manage.py makemigrations --check --dry-run` passes with no changes detected.
- The preview API should return `404` for a question whose `catechism.tradition` is outside the active `docFilters` cookie.
- SQLite tests should continue using the fallback `icontains` search path.
- Direct Atlas probes returned `200` for the Westminster Standards home, WSC Q1, WLC Q1, and WCF chapter 1 routes.
- `env -u SECRET_KEY DJANGO_SETTINGS_MODULE=config.settings.production bash -c 'export SECRET_KEY="${SECRET_KEY:-django-insecure-build-only-placeholder}"; python3 manage.py check'` passes, matching the Render build fallback path.
