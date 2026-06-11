# Study Reformed

A Django web application for studying the great Reformed confessional standards — including the Westminster Standards, Three Forms of Unity, and related documents — with historical commentaries, scripture proofs, cross-references, and personal study tools.

## Features

- Browse Westminster, Three Forms of Unity, and related Reformed documents with topic/chapter navigation
- Read historical commentaries from Fisher, Flavel, Henry, Watson, Vincent, Ridgley, Shaw, Hodge, Ursinus, and others
- View scripture proof texts inline with each question, section, or chapter
- Compare doctrines across standards and thematic comparison sets
- Search question text, answer text, and proof-text references
- Browse a scripture index across loaded documents
- Save personal notes and text highlights as an authenticated user
- Use dark mode and print-friendly styles
- Support the site through Stripe-powered supporter memberships

## Tech Stack

- **Backend:** Django 4.2, Python 3.12
- **Database:** PostgreSQL in production, SQLite in local development
- **Frontend:** Bootstrap 5.3, vanilla JavaScript
- **Hosting:** Render via `render.yaml`
- **Static files:** WhiteNoise
- **Payments:** Stripe Checkout and webhooks

## Local Setup

```bash
git clone https://github.com/MartinGallagher-code/westminster.git
cd westminster
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createcachetable
```

`manage.py` defaults to `config.settings.development`, which uses SQLite and a development-only secret key fallback.

## Loading Data

For a full local dataset, run the same idempotent load sequence used by Render:

```bash
./build.sh
```

If you only need a smaller development dataset, run the relevant management commands manually. Most load commands skip automatically when their source data has not changed.

External fetch commands are intentionally manual because they call upstream services:

```bash
python manage.py fetch_watson --delay=0.3
python manage.py fetch_scripture --delay=0.3
```

## Running the App

```bash
python manage.py runserver
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov
```

Lint and migration checks:

```bash
flake8 catechism/ accounts/ config/ --max-line-length=120 --exclude=migrations
python manage.py makemigrations --check --dry-run
```

## Deployment

The project deploys to Render via `render.yaml`.

Python is pinned with `.python-version` so Render uses Python 3.12 even if the service falls back to Render's platform default.

Required production environment variables:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRODUCT_ID`
- `GOOGLE_ANALYTICS_ID` optional

`build.sh` installs dependencies, collects static assets, migrates the database, loads source data, rebuilds indexes/cross-references, and clears the cache.

## Project Workflow

- Record user-visible changes in `CHANGELOG.md`.
- Update `HANDOFF.md` before ending substantial work sessions.
- Keep future work in `TODO.md`; keep Stripe setup in `TODO_STRIPE.md`; keep BCO-specific notes in `TODO_PCA_BCO.md`.

## License

Public domain catechism data sourced from [Creeds.json](https://github.com/NonlinearFruit/Creeds.json). Additional source data is tracked in `data/` with project-specific loaders.
