"""Search snippets and hit highlighting."""

import pytest

from catechism.search_text import highlight, highlighted_snippet, search_terms, snippet

ANSWER = (
    "Assurance of grace and salvation not being of the essence of faith, a true "
    "believer may wait long, and conflict with many difficulties, before he be "
    "partaker of it."
)


def test_search_terms_drops_stop_words_and_short_words():
    assert search_terms('of the Lord and faith') == ["lord", "faith"]
    assert search_terms('') == []


def test_snippet_centres_on_the_first_match():
    result = snippet(ANSWER, 'believer', radius_words=4)
    assert 'believer' in result
    assert result.startswith('…') and result.endswith('…')
    # The opening words are not what is shown — that was the old behaviour.
    assert not result.startswith('Assurance of grace')


def test_snippet_falls_back_to_the_opening_words_when_nothing_matches():
    result = snippet(ANSWER, 'zzzz', radius_words=5)
    assert result.startswith('Assurance of grace')


def test_snippet_never_splits_the_word_it_matched():
    # 'faith' matches at the start of 'faith,' — the rest of the word must
    # stay attached rather than being pushed into the tail.
    assert 'faith,' in snippet(ANSWER, 'faith', radius_words=4)


def test_snippet_handles_empty_input():
    assert snippet('', 'faith') == ''
    assert snippet(None, 'faith') == ''


def test_highlight_marks_terms_with_its_own_class():
    result = str(highlight('Assurance of faith', 'assurance'))
    assert '<mark class="search-hit">Assurance</mark>' in result


def test_highlight_escapes_markup_in_the_source_text():
    result = str(highlight('faith <script>alert(1)</script>', 'faith'))
    assert '<script>' not in result
    assert '&lt;script&gt;' in result


def test_highlight_escapes_markup_in_the_query():
    result = str(highlight('a faithful saying', '<img src=x onerror=1>'))
    assert '<img' not in result


def test_highlight_matches_at_word_start_only():
    # 'sin' should not light up 'business'.
    result = str(highlight('the business of sin', 'sin'))
    assert result.count('<mark') == 1
    assert '<mark class="search-hit">sin</mark>' in result


def test_highlighted_snippet_combines_both():
    result = str(highlighted_snippet(ANSWER, 'believer', radius_words=4))
    assert '<mark class="search-hit">believer</mark>' in result


@pytest.mark.django_db
def test_search_results_show_the_matching_phrase(client, question):
    question.answer_text = ANSWER
    question.question_text = 'What is assurance?'
    question.save()

    resp = client.get('/search/?q=believer')
    body = resp.content.decode()
    assert '<mark class="search-hit">believer</mark>' in body
