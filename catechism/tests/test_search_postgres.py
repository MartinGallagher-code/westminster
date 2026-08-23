"""Postgres-only search behaviour: the stored, indexed search vector.

Skipped on SQLite, which uses the ``icontains`` fallback. Run these against
Postgres with ``pytest --ds=<postgres settings module>``; CI does so in its own
job, because the production search path is Postgres-only and was previously
exercised by nothing.
"""

import pytest
from django.db import connection

from catechism.views import _search_questions

postgres_only = pytest.mark.skipif(
    connection.vendor != 'postgresql', reason='requires PostgreSQL',
)


@postgres_only
@pytest.mark.django_db
def test_the_search_vector_column_and_index_exist():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT is_generated FROM information_schema.columns
            WHERE table_name = 'catechism_question' AND column_name = 'search_vector'
        """)
        row = cursor.fetchone()
        assert row is not None, 'search_vector column is missing'
        assert row[0] == 'ALWAYS', 'search_vector should be a generated column'

        cursor.execute("""
            SELECT indexdef FROM pg_indexes
            WHERE tablename = 'catechism_question'
              AND indexname = 'catechism_question_search_vector_gin'
        """)
        assert cursor.fetchone(), 'GIN index on search_vector is missing'


@postgres_only
@pytest.mark.django_db
def test_search_matches_stemmed_words(catechism, question):
    question.question_text = 'What is justification?'
    question.answer_text = 'An act of free grace, wherein God pardons and judges.'
    question.save()

    # The English stemmer folds inflections together: judges/judge/judging all
    # stem to 'judg'. (It does not fold derivations — 'justification' stems to
    # 'justif' and 'justified' to 'justifi', so those do not match each other.)
    assert _search_questions('judge', ['westminster']).count() == 1
    assert _search_questions('judging', ['westminster']).count() == 1
    assert _search_questions('pardoned', ['westminster']).count() == 1
    assert _search_questions('perseverance', ['westminster']).count() == 0


@postgres_only
@pytest.mark.django_db
def test_the_generated_column_follows_edits(catechism, question):
    assert _search_questions('absquatulate', ['westminster']).count() == 0
    question.answer_text = f'{question.answer_text} Absquatulate.'
    question.save()
    # Maintained by the database itself, so no reindex step can be forgotten.
    assert _search_questions('absquatulate', ['westminster']).count() == 1


@postgres_only
@pytest.mark.django_db
def test_topic_names_still_match(catechism, topic, question):
    topic.name = 'Effectual Calling'
    topic.save()
    assert _search_questions('Effectual Calling', ['westminster']).count() >= 1


@postgres_only
@pytest.mark.django_db
def test_the_gin_index_is_usable_for_the_search_condition(catechism, question):
    """The index can serve the match operator the search actually uses.

    Asserted against the bare condition rather than the full query: on a
    two-row test table the planner will always prefer a sequential scan, so
    what is checkable here is that the index *applies* to `@@` — which is
    exactly what a previous shape broke, by ORing the match against a subquery
    on another table.
    """
    with connection.cursor() as cursor:
        cursor.execute('SET LOCAL enable_seqscan = off')
        cursor.execute("""
            EXPLAIN SELECT id FROM catechism_question
            WHERE search_vector @@ websearch_to_tsquery('english', %s)
        """, ['justification'])
        plan = '\n'.join(row[0] for row in cursor.fetchall())
    assert 'catechism_question_search_vector_gin' in plan, plan
