# Westminster Standards

A Django web application for studying the Westminster Standards (1647) — the Shorter Catechism (WSC), Larger Catechism (WLC), and Confession of Faith (WCF) — with historical commentaries, scripture proofs, cross-references, and personal study tools.

## Features

- Browse all three Westminster Standards with topic/chapter navigation
- Historical commentaries from Fisher, Flavel, Henry, Watson, Wallis, Vincent, Ridgley, Shaw, and Hodge
- ESV scripture proof texts inline with each question/section
- Cross-references between standards and thematic comparisons
- Full-text search across all standards
- Scripture index (every Bible book referenced)
- Personal notes and text highlighting (authenticated users)
- Dark mode with system preference detection
- Print-friendly styles

## Tech Stack

- **Backend:** Django 4.2, Python 3.12
- **Database:** PostgreSQL (production), SQLite (development)
- **Frontend:** Bootstrap 5.3, vanilla JavaScript
- **Hosting:** Render (free tier) via `render.yaml`
- **Static files:** WhiteNoise

## Local Setup

```bash
# Clone and create virtual environment
git clone https://github.com/your-username/westminster.git
cd westminster
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and load data
python manage.py migrate
python manage.py createcachetable
python manage.py load_catechism
python manage.py load_fisher
python manage.py load_flavel
python manage.py load_henry
python manage.py load_wallis
python manage.py load_vincent
python manage.py load_prooftexts
python manage.py load_wlc
python manage.py load_ridgley
python manage.py load_prooftexts --catechism wlc
python manage.py load_wcf
python manage.py load_shaw
python manage.py load_hodge
python manage.py load_crossrefs
python manage.py load_standard_crossrefs
python manage.py build_scripture_index
python manage.py load_comparison_themes

# Start development server
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

## Manual Data Commands

These fetch from external APIs and should be run manually:

```bash
# Fetch Watson commentary from CCEL
python manage.py fetch_watson --delay=0.3

# Fetch ESV scripture texts
python manage.py fetch_scripture --delay=0.3
```

## Deployment

The project deploys to Render via `render.yaml`. The `build.sh` script handles migrations, data loading, and cache setup automatically.

## License

Public domain catechism data sourced from [Creeds.json](https://github.com/NonlinearFruit/Creeds.json).
