#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Render does not always expose generated secrets during build. Django only
# needs a stable placeholder for build-time management commands; runtime still
# requires the real SECRET_KEY from the service environment.
export SECRET_KEY="${SECRET_KEY:-django-insecure-build-only-placeholder}"

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createcachetable

# Load every dataset (shared with the CI data-integrity job)
./scripts/load_data.sh

# These commands fetch from external APIs - run manually via Render shell:
#   python manage.py fetch_watson --delay=0.3
#   python manage.py fetch_scripture --delay=0.3
