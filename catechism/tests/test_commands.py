import pytest
from django.core.management import call_command

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
