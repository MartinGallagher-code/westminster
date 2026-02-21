#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Load Shorter Catechism data (idempotent - safe to run on every deploy)
python manage.py load_catechism
python manage.py load_fisher
python manage.py load_flavel
python manage.py load_henry
python manage.py load_watson
python manage.py load_whyte
python manage.py load_wallis
python manage.py load_vincent
python manage.py load_prooftexts

# Load Larger Catechism and commentary
python manage.py load_wlc
python manage.py load_ridgley
python manage.py load_prooftexts --catechism wlc

# Load Confession of Faith
python manage.py load_wcf

# Cross-references between WSC and WLC (legacy)
python manage.py load_crossrefs

# Generalized cross-references (all three standards)
python manage.py load_standard_crossrefs

# Scripture index
python manage.py build_scripture_index

# Comparison themes
python manage.py load_comparison_themes

# Scripture text fetching is slow (external API calls) - run manually via Render shell:
#   python manage.py fetch_scripture --delay=0.3
