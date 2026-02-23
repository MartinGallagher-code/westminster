import pytest
from django.core.management import call_command

from catechism.management.commands.fetch_scripture import (
    expand_references,
    parse_reference,
)
from catechism.models import Catechism, Question


@pytest.mark.django_db
def test_load_catechism_smoke():
    """Smoke test: load_catechism reads the data file and creates the WSC."""
    call_command('load_catechism')
    assert Catechism.objects.filter(slug='wsc').exists()


@pytest.mark.django_db
def test_cleanup_stale_sources_no_error():
    """cleanup_stale_sources runs without error even with no data."""
    call_command('cleanup_stale_sources')


# --- Tier 1 confessions ---


@pytest.mark.django_db
def test_load_scots_smoke():
    """Smoke test: load_scots reads the data file and creates the Scots Confession."""
    call_command('load_scots')
    assert Catechism.objects.filter(slug='scots').exists()


@pytest.mark.django_db
def test_load_scots_article_count():
    """Verify the Scots Confession loads 25 articles."""
    call_command('load_scots')
    cat = Catechism.objects.get(slug='scots')
    assert cat.questions.count() == 25


@pytest.mark.django_db
def test_load_irish_smoke():
    """Smoke test: load_irish reads the data file and creates the Irish Articles."""
    call_command('load_irish')
    assert Catechism.objects.filter(slug='irish').exists()


@pytest.mark.django_db
def test_load_irish_article_count():
    """Verify the Irish Articles loads 104 articles."""
    call_command('load_irish')
    cat = Catechism.objects.get(slug='irish')
    assert cat.questions.count() == 104


@pytest.mark.django_db
def test_load_second_helvetic_smoke():
    """Smoke test: load_second_helvetic creates the Second Helvetic Confession."""
    call_command('load_second_helvetic')
    assert Catechism.objects.filter(slug='second-helvetic').exists()


@pytest.mark.django_db
def test_load_second_helvetic_chapter_count():
    """Verify the Second Helvetic Confession loads 30 chapters."""
    call_command('load_second_helvetic')
    cat = Catechism.objects.get(slug='second-helvetic')
    assert cat.questions.count() == 30


@pytest.mark.django_db
def test_load_savoy_smoke():
    """Smoke test: load_savoy reads the data file and creates the Savoy Declaration."""
    call_command('load_savoy')
    assert Catechism.objects.filter(slug='savoy').exists()


@pytest.mark.django_db
def test_load_savoy_section_count():
    """Verify the Savoy Declaration loads the expected number of sections."""
    call_command('load_savoy')
    cat = Catechism.objects.get(slug='savoy')
    assert cat.questions.count() == cat.total_questions


@pytest.mark.django_db
def test_load_savoy_idempotent():
    """Verify loading Savoy twice does not duplicate records."""
    call_command('load_savoy')
    count1 = Question.objects.filter(catechism__slug='savoy').count()
    call_command('load_savoy')
    count2 = Question.objects.filter(catechism__slug='savoy').count()
    assert count1 == count2


# --- parse_reference unit tests ---


class TestParseReference:
    """Unit tests for parse_reference (no DB required)."""

    def test_standard_reference(self):
        assert parse_reference('1 Cor. 10:31') == (46, 10, [31])

    def test_verse_range(self):
        assert parse_reference('Ps. 73:25-28') == (19, 73, [25, 26, 27, 28])

    def test_comma_separated_verses(self):
        assert parse_reference('Rom. 4:3, 6, 16') == (45, 4, [3, 6, 16])

    def test_whole_chapter(self):
        assert parse_reference('Gen. 1') == (1, 1, None)

    def test_single_chapter_book(self):
        assert parse_reference('Jude 6') == (65, 1, [6])

    def test_single_chapter_book_multiple_verses(self):
        assert parse_reference('Jude 6, 7') == (65, 1, [6, 7])

    def test_roman_numeral_prefix(self):
        assert parse_reference('II Tim. 3:16') == (55, 3, [16])

    def test_continuation_reference(self):
        assert parse_reference('15:4', last_book_num=46) == (46, 15, [4])

    # --- New abbreviation tests ---

    def test_eccles_abbreviation(self):
        assert parse_reference('Eccles. 7:29') == (21, 7, [29])

    def test_eccles_comma_verses(self):
        assert parse_reference('Eccles. 5:4, 5') == (21, 5, [4, 5])

    def test_jam_abbreviation(self):
        assert parse_reference('Jam. 1:13, 17') == (59, 1, [13, 17])

    def test_tit_abbreviation(self):
        assert parse_reference('Tit. 1:15') == (56, 1, [15])

    def test_ephes_abbreviation(self):
        assert parse_reference('Ephes. 2:3') == (49, 2, [3])

    def test_numb_abbreviation(self):
        assert parse_reference('Numb. 30:5, 8, 12, 13') == (4, 30, [5, 8, 12, 13])

    # --- Song of Solomon ---

    def test_song_of_solomon(self):
        assert parse_reference('Song of Solomon 1:4') == (22, 1, [4])

    def test_song_of_solomon_comma_verses(self):
        assert parse_reference('Song of Solomon 5:2, 3, 6') == (22, 5, [2, 3, 6])

    # --- Em-dash / en-dash normalization ---

    def test_en_dash_verse_range(self):
        assert parse_reference('Heb. 10:5\u201310') == (58, 10, [5, 6, 7, 8, 9, 10])

    def test_em_dash_verse_range(self):
        assert parse_reference('Lev. 26:1\u201414') == (3, 26, list(range(1, 15)))


# --- expand_references unit tests ---


class TestExpandReferences:
    """Unit tests for expand_references (no DB required)."""

    def test_simple_passthrough(self):
        assert expand_references('Rom. 8:28') == ['Rom. 8:28']

    def test_with_connector(self):
        assert expand_references('Heb. 12:25 with 2 Cor. 13:3') == [
            'Heb. 12:25', '2 Cor. 13:3'
        ]

    def test_and_connector(self):
        result = expand_references('Acts 17:26 and 1 Cor. 15:21')
        assert result == ['Acts 17:26', '1 Cor. 15:21']

    def test_ampersand_connector(self):
        result = expand_references('Gen. 1:27, 28 & Gen. 2:16, 17')
        assert result == ['Gen. 1:27, 28', 'Gen. 2:16, 17']

    def test_mixed_connectors(self):
        ref = 'Gen. 1:27, 28 & Gen. 2:16, 17 and Acts 17:26 with Rom. 5:12'
        result = expand_references(ref)
        assert result == [
            'Gen. 1:27, 28', 'Gen. 2:16, 17', 'Acts 17:26', 'Rom. 5:12'
        ]

    def test_throughout(self):
        assert expand_references('Ps. 73 throughout') == ['Ps. 73']

    def test_chap_suffix(self):
        assert expand_references('Gen. 1 chap.') == ['Gen. 1']

    def test_chapters_suffix(self):
        result = expand_references('Heb. 8, 9, 10 chapters')
        assert result == ['Heb. 8', 'Heb. 9', 'Heb. 10']

    def test_chaps_suffix(self):
        result = expand_references('2 Chron. 29, 30 chaps.')
        assert result == ['2 Chron. 29', '2 Chron. 30']

    def test_chapter_range(self):
        assert expand_references('Gen. 1-2') == ['Gen. 1', 'Gen. 2']

    def test_chapter_range_en_dash(self):
        assert expand_references('Job 38\u201341') == ['Job 38', 'Job 39', 'Job 40', 'Job 41']

    def test_comma_separated_chapters(self):
        assert expand_references('Rev. 2, 3') == ['Rev. 2', 'Rev. 3']

    def test_cross_reference_range(self):
        result = expand_references('2 Cor. 8-2 Cor. 9')
        assert result == ['2 Cor. 8', '2 Cor. 9']

    def test_to_the_end(self):
        result = expand_references('Mark 14:66 to the end')
        assert result == ['Mark 14:66-200']

    def test_to_the_end_with_connector(self):
        result = expand_references('1 Cor. 11:27 to the end, with Jude 23')
        assert result == ['1 Cor. 11:27-200', 'Jude 23']

    def test_comma_before_and(self):
        result = expand_references('2 John 10, 11, and 2 Thess. 3:14')
        assert result == ['2 John 10, 11', '2 Thess. 3:14']

    def test_song_of_solomon_normalization(self):
        result = expand_references('Song of Solomon 1:4')
        assert result == ['Song 1:4']

    def test_single_chapter_book_not_expanded_as_chapters(self):
        """Jude 6, 7 should NOT be expanded as chapters 6 and 7."""
        result = expand_references('Jude 6, 7')
        assert result == ['Jude 6, 7']
