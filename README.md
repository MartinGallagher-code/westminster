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
- Support the site through Buy Me a Coffee

## Tech Stack

- **Backend:** Django 4.2, Python 3.12
- **Database:** PostgreSQL in production, SQLite in local development
- **Frontend:** Bootstrap 5.3, vanilla JavaScript (vendored under `static/vendor/`, no CDN)
- **Hosting:** Render via `render.yaml`
- **Static files:** WhiteNoise
- **Donations:** Buy Me a Coffee (external link)

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

External fetch commands are intentionally manual because they call upstream
services. Until `fetch_scripture` is run the database holds no verse text, so
proof texts render as links into the Scripture index rather than as passages —
that is the expected state of a freshly loaded database, not a fault:

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

Operational procedures — backups, restores, health checks, monitoring — are in
[`docs/OPERATIONS.md`](docs/OPERATIONS.md).

The project deploys to Render via `render.yaml`.

Python is pinned with `.python-version` so Render uses Python 3.12 even if the service falls back to Render's platform default.

Required production environment variables:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `GOOGLE_ANALYTICS_ID` optional
- `SENTRY_DSN` optional — error monitoring; unset disables it
- `SENTRY_TRACES_SAMPLE_RATE` optional, defaults to `0.05`

`build.sh` installs dependencies, collects static assets, migrates the database, loads source data, rebuilds indexes/cross-references, and clears the cache.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the project is put
  together: the apps, the data model, the loading pipeline, the collections
  filter, the Atlas seam, and the conventions worth knowing before a first
  change.
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md) — backups, restores, health
  checks, monitoring.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — setup, what to run before a pull
  request, and how to report a transcription error.
- [`westminster_standards/README.md`](westminster_standards/README.md) — the
  Atlas app.

## Project Workflow

- Record user-visible changes in `CHANGELOG.md`.
- Update `HANDOFF.md` before ending substantial work sessions.
- Keep future work in `TODO.md`; keep BCO-specific notes in `TODO_PCA_BCO.md`.

## License

The code is MIT-licensed — see [`LICENSE`](LICENSE).

The confessional and commentary texts are separate from the code and are all in
the public domain. Public-domain catechism data is sourced from
[Creeds.json](https://github.com/NonlinearFruit/Creeds.json); the 1689 proof
texts come from the CC0-licensed [lwalen/lbcf](https://github.com/lwalen/lbcf)
repository. Additional source data is tracked in `data/` with project-specific
loaders.

Vendored front-end assets keep their own licences under `static/vendor/`:
Bootstrap and Bootstrap Icons under MIT, and both typefaces under the SIL Open
Font License.
