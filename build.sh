#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createcachetable

# Load data (each command skips automatically if source data unchanged)
python manage.py load_catechism
python manage.py load_fisher
python manage.py load_flavel
python manage.py load_henry
python manage.py load_watson
python manage.py load_wallis
python manage.py load_vincent
python manage.py load_prooftexts

# Load Larger Catechism and commentary
python manage.py load_wlc
python manage.py load_ridgley
python manage.py load_prooftexts --catechism wlc

# Load Confession of Faith and commentaries
python manage.py load_wcf
python manage.py load_shaw
python manage.py load_hodge

# Remove stale commentary sources not loaded by any command above
python manage.py cleanup_stale_sources

# Cross-references between WSC and WLC (legacy)
python manage.py load_crossrefs

# Generalized cross-references (all three standards)
python manage.py load_standard_crossrefs

# Scripture index
python manage.py build_scripture_index

# Comparison themes
python manage.py load_comparison_themes

# Clear cache after data load to ensure fresh content
python manage.py clear_cache

# These commands fetch from external APIs - run manually via Render shell:
#   python manage.py fetch_watson --delay=0.3
#   python manage.py fetch_scripture --delay=0.3
