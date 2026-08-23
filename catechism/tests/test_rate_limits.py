"""Rate limits on the endpoints worth abusing."""

import pytest
from django.core.cache import cache
from django.test import Client, override_settings


@pytest.fixture(autouse=True)
def clear_rate_limit_cache():
    cache.clear()
    yield
    cache.clear()


@override_settings(RATELIMIT_ENABLE=True)
@pytest.mark.django_db
def test_search_is_throttled_per_ip(catechism):
    client = Client()
    # Well under the limit: still fine.
    for _ in range(5):
        assert client.get('/search/?q=faith').status_code == 200


@override_settings(RATELIMIT_ENABLE=True)
@pytest.mark.django_db
def test_search_blocks_a_flood(catechism):
    client = Client()
    statuses = {client.get(f'/search/?q=faith{n}').status_code for n in range(130)}
    assert 403 in statuses, 'a 130-request burst should trip the 120/m limit'


@override_settings(RATELIMIT_ENABLE=True)
@pytest.mark.django_db
def test_password_reset_post_is_throttled():
    client = Client()
    statuses = [
        client.post('/accounts/password-reset/', {'email': 'someone@example.test'}).status_code
        for _ in range(8)
    ]
    assert 403 in statuses, 'password reset should throttle repeated POSTs'


@override_settings(RATELIMIT_ENABLE=True)
@pytest.mark.django_db
def test_reading_pages_are_not_throttled(catechism, question):
    client = Client()
    statuses = {client.get('/wsc/questions/1/').status_code for _ in range(30)}
    assert statuses == {200}


@pytest.mark.django_db
def test_password_reset_flow_reverses_its_own_namespace():
    """Regression: Django's PasswordResetView defaults to the un-namespaced
    'password_reset_done', which does not exist here — submitting the form
    raised NoReverseMatch instead of redirecting."""
    client = Client()
    resp = client.post('/accounts/password-reset/', {'email': 'someone@example.test'})
    assert resp.status_code == 302
    assert resp['Location'] == '/accounts/password-reset/done/'
