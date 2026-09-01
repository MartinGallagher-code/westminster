# Contributing

Thanks for looking. This is a small project maintained by one person, so the
most useful thing you can do before writing code is open an issue describing
what you have in mind.

## Getting set up

```bash
git clone https://github.com/MartinGallagher-code/westminster.git
cd westminster
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createcachetable
./scripts/load_data.sh          # ~1 minute; loads all fourteen documents
python manage.py runserver
```

`manage.py` defaults to `config.settings.development`, which uses SQLite and a
development-only secret key.

Two things about a freshly loaded database that surprise people:

- **Proof texts have no verse text.** `fetch_scripture` calls an upstream
  service and is deliberately manual, so the references render as links to the
  Scripture index rather than as passages. That is the expected state; run
  `python manage.py fetch_scripture --delay=0.3` if you need the text.
- **Search behaves differently from production.** The production search path is
  PostgreSQL-only, so a SQLite run exercises the substring fallback instead and
  five tests skip. Run against Postgres if you are touching search.

[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains how the pieces fit
together — the loading pipeline, the collections filter, the Atlas seam. It is
worth ten minutes before a first change.

## Before you open a pull request

Run what CI runs:

```bash
flake8 catechism/ accounts/ config/ --max-line-length=120 --exclude=migrations
python manage.py makemigrations --check --dry-run
pytest
```

If you touched loaders, data files, templates or URLs, also run the check that
looks at the loaded site rather than at factories:

```bash
python manage.py check_site_integrity
```

It catches a class of defect the unit suite cannot see — doctrine-head chips
pointing at pages that do not exist, sitemap URLs that 404, proof references
the parser can no longer read.

## What makes a change easy to accept

- **One change per pull request**, with a message that says what was wrong
  rather than only what was done.
- **A test that fails without the fix.** For anything that only shows up in the
  loaded corpus, a check in `check_site_integrity` is often the right home.
- **Comments that explain why.** The codebase leans this way deliberately:
  where something is surprising, the reason it is that way is written down next
  to it.
- **No new external assets.** Bootstrap, its icons and both typefaces are
  vendored under `static/vendor/` and served from this origin, so the site
  renders with CDNs unreachable and discloses no visitor IPs to third parties.
  A test enforces this.
- **Keep `{# ... #}` comments on one line.** Django renders a multi-line one
  verbatim into the page; use `{% comment %}` for anything longer. There is a
  test for this too.

## Corrections to the texts

Transcription errors are welcome and easy to act on. Please say which document,
which question or section, what it currently reads, and what the printed
edition has. The texts live in `data/`, and the loader that reads them skips
when its source hash is unchanged — so a data fix takes effect on the next
deploy without any code change.

Note that the texts are reproduced as published. Archaic spelling, capitalised
nouns and long sentences are not errors.

## Reporting a security issue

Please do not open a public issue. Email the maintainer instead.
