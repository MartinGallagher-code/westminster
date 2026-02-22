import pytest
from django.core.management import call_command

from catechism.models import Catechism


@pytest.mark.django_db
def test_load_catechism_smoke():
    """Smoke test: load_catechism reads the data file and creates the WSC."""
    call_command('load_catechism')
    assert Catechism.objects.filter(slug='wsc').exists()


@pytest.mark.django_db
def test_cleanup_stale_sources_no_error():
    """cleanup_stale_sources runs without error even with no data."""
    call_command('cleanup_stale_sources')
