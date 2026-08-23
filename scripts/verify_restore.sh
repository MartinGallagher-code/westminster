#!/usr/bin/env bash
# Verify a restored database is complete and serviceable.
#
# Usage:
#   DATABASE_URL=postgres://user:pass@host:5432/dbname ./scripts/verify_restore.sh
#
# Run this against every restore, not just the ones done in anger — a backup
# nobody has restored is a hypothesis, not a backup. It checks three things a
# successful-looking pg_restore can still get wrong: that the schema matches
# the code, that the data is all there, and that the pages actually render.
set -o errexit
set -o pipefail

if [ -z "${DATABASE_URL:-}" ]; then
    echo "DATABASE_URL is not set." >&2
    exit 2
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.ci_postgres}"
export SECRET_KEY="${SECRET_KEY:-django-insecure-restore-verification-only}"

echo "→ Schema matches the code"
python manage.py migrate --check

echo "→ Django system checks"
python manage.py check

echo "→ Row counts"
python manage.py shell -c "
from catechism.models import Catechism, Question, Commentary, ScriptureIndex
from accounts.models import UserNote, Highlight, InlineComment, MemorizationCard
for model in (Catechism, Question, Commentary, ScriptureIndex,
              UserNote, Highlight, InlineComment, MemorizationCard):
    print(f'  {model.__name__:20} {model.objects.count():>8}')
"

echo "→ Data integrity and page rendering"
python manage.py check_site_integrity

echo "Restore verified."
