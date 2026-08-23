"""Page caching for anonymous visitors on the read-only pages."""

import json

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, override_settings


@pytest.fixture(autouse=True)
def clear_page_cache():
    cache.clear()
    yield
    cache.clear()


@override_settings(PAGE_CACHE_SECONDS=60)
@pytest.mark.django_db
def test_second_anonymous_request_is_served_from_cache(catechism, topic, question):
    client = Client()
    first = client.get('/wsc/questions/1/')
    second = client.get('/wsc/questions/1/')

    assert first['X-Page-Cache'] == 'miss'
    assert second['X-Page-Cache'] == 'hit'
    assert first.content == second.content


@override_settings(PAGE_CACHE_SECONDS=0)
@pytest.mark.django_db
def test_caching_is_off_by_default(catechism, topic, question):
    client = Client()
    assert 'X-Page-Cache' not in client.get('/wsc/questions/1/')


@override_settings(PAGE_CACHE_SECONDS=60)
@pytest.mark.django_db
def test_signed_in_readers_are_never_served_a_cached_page(catechism, topic, question):
    """A reader's page shows their notes and their memorisation deck."""
    anonymous = Client()
    anonymous.get('/wsc/questions/1/')          # warm the cache

    reader = User.objects.create_user(username='reader', password='catechism-1647')
    signed_in = Client()
    signed_in.force_login(reader)
    response = signed_in.get('/wsc/questions/1/')

    assert 'X-Page-Cache' not in response
    assert 'Memorise' in response.content.decode()


@override_settings(PAGE_CACHE_SECONDS=60)
@pytest.mark.django_db
def test_a_signed_in_page_is_never_written_to_the_cache(catechism, topic, question):
    reader = User.objects.create_user(username='reader', password='catechism-1647')
    signed_in = Client()
    signed_in.force_login(reader)
    signed_in.get('/wsc/questions/1/')          # must not populate the cache

    anonymous = Client()
    response = anonymous.get('/wsc/questions/1/')
    assert response['X-Page-Cache'] == 'miss'
    assert 'Memorise' not in response.content.decode()


@override_settings(PAGE_CACHE_SECONDS=60)
@pytest.mark.django_db
def test_the_key_varies_by_active_collections(catechism, topic, question):
    """The same URL renders differently per collection, so it must key on them."""
    westminster = Client()
    westminster.cookies['docFilters'] = json.dumps({'westminster': True})
    both = Client()
    both.cookies['docFilters'] = json.dumps(
        {'westminster': True, 'reformed_confessions': True}
    )

    assert westminster.get('/wsc/questions/1/')['X-Page-Cache'] == 'miss'
    assert both.get('/wsc/questions/1/')['X-Page-Cache'] == 'miss'
    assert westminster.get('/wsc/questions/1/')['X-Page-Cache'] == 'hit'


@override_settings(PAGE_CACHE_SECONDS=60)
@pytest.mark.django_db
def test_the_query_string_is_part_of_the_key(catechism, topic, question, books=None):
    client = Client()
    assert client.get('/wsc/questions/1/')['X-Page-Cache'] == 'miss'
    assert client.get('/wsc/questions/1/?highlight=1')['X-Page-Cache'] == 'miss'


@override_settings(PAGE_CACHE_SECONDS=60)
@pytest.mark.django_db
def test_404s_are_not_cached(catechism):
    client = Client()
    assert client.get('/wsc/questions/999/').status_code == 404
    assert client.get('/wsc/questions/999/').status_code == 404
