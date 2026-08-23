"""Page-level accessibility affordances that are easy to regress."""

import pytest


@pytest.mark.django_db
def test_skip_link_targets_a_real_main_landmark(client):
    body = client.get('/').content.decode()

    assert 'href="#main-content"' in body
    assert 'Skip to main content' in body
    # The target must be a landmark that can take focus, not a bare div.
    assert '<main class=' in body
    assert 'id="main-content" tabindex="-1"' in body


@pytest.mark.django_db
def test_collection_toggles_expose_their_pressed_state(client):
    body = client.get('/').content.decode()

    assert body.count('tradition-toggle') >= 3
    assert 'aria-pressed' in body


@pytest.mark.django_db
def test_locus_chips_use_a_custom_property_not_a_fixed_colour(client, confession):
    """The eight Atlas accents are pastels chosen against a dark ground.

    Passing them through ``--locus-color`` lets the stylesheet darken them for
    the light theme instead of painting an unreadable hex directly.
    """
    from catechism.models import Topic

    Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture',
        slug='of-the-holy-scripture', order=1, question_start=1, question_end=10,
    )
    body = client.get('/wcf/chapters/of-the-holy-scripture/').content.decode()

    assert '--locus-color:' in body
    assert 'border-left-color: #' not in body
