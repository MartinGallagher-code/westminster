"""Add a stored, indexed search vector for Postgres.

The Postgres branch of the search built its ``tsvector`` on the fly, so every
query recomputed it for every row and no index could help. This adds a
generated column, maintained by the database itself, with a GIN index over it.

Postgres-only by design: the project runs on SQLite for local development and
tests, where the search falls back to ``icontains``. The column is created
with raw SQL rather than a model field so the SQLite schema stays valid — a
``SearchVectorField`` in the model would make every SQLite migration fail.
"""

from django.db import migrations

SEARCH_VECTOR_SQL = """
ALTER TABLE catechism_question
    ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(question_text, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(answer_text, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(proof_texts, '')), 'C')
    ) STORED;

CREATE INDEX catechism_question_search_vector_gin
    ON catechism_question USING GIN (search_vector);
"""

REVERSE_SQL = """
DROP INDEX IF EXISTS catechism_question_search_vector_gin;
ALTER TABLE catechism_question DROP COLUMN IF EXISTS search_vector;
"""

# Topic names are matched with a subquery against this table, so give that
# lookup an index too.
TOPIC_NAME_SQL = """
CREATE INDEX IF NOT EXISTS catechism_topic_name_lower
    ON catechism_topic (lower(name));
"""

TOPIC_NAME_REVERSE_SQL = """
DROP INDEX IF EXISTS catechism_topic_name_lower;
"""


def add_search_vector(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SEARCH_VECTOR_SQL)
    schema_editor.execute(TOPIC_NAME_SQL)


def drop_search_vector(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(REVERSE_SQL)
    schema_editor.execute(TOPIC_NAME_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0022_add_reformed_confessions_tradition'),
    ]

    operations = [
        migrations.RunPython(add_search_vector, drop_search_vector),
    ]
