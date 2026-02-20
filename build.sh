#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Load catechism data (idempotent - safe to run on every deploy)
python manage.py load_catechism
python manage.py load_fisher
python manage.py load_flavel
python manage.py load_henry
python manage.py load_watson
python manage.py load_whyte
python manage.py load_boston
python manage.py load_beattie
python manage.py load_wallis
python manage.py load_vincent
python manage.py load_prooftexts

# Load Larger Catechism and commentary
python manage.py load_wlc
python manage.py load_ridgley

python manage.py fetch_scripture --delay=0.3
