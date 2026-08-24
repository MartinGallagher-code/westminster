"""One search box: suggestions across the standards, the Atlas, and positions."""

import json

import pytest

from .conftest import BibleBookFactory


@pytest.mark.django_db
def test_a_short_query_suggests_nothing(client):
    data = json.loads(client.get('/api/suggest/?q=a').content)
    assert data['groups'] == []


@pytest.mark.django_db
def test_suggestions_reach_the_atlas_layers(client):
    """The point of the change: a reader had to know the Atlas existed."""
    data = json.loads(client.get('/api/suggest/?q=atonement').content)
    labels = [group['label'] for group in data['groups']]

    assert 'Cruxes' in labels
    assert 'Divines' in labels
    urls = [item['url'] for group in data['groups'] for item in group['items']]
    assert any(url.startswith('/atlas/') for url in urls)


@pytest.mark.django_db
def test_suggestions_include_the_standards_text(client, catechism, topic, question):
    question.question_text = 'What is the chief end of man?'
    question.save()

    data = json.loads(client.get('/api/suggest/?q=chief').content)
    labels = [group['label'] for group in data['groups']]
    assert 'In the standards' in labels


@pytest.mark.django_db
def test_positions_are_suggested_with_their_definitions(client):
    data = json.loads(client.get('/api/suggest/?q=Supralapsarian').content)
    positions = [g for g in data['groups'] if g['label'] == 'Positions']
    assert positions
    assert positions[0]['items'][0]['detail']


@pytest.mark.django_db
def test_a_scripture_reference_is_offered_as_a_jump(client):
    BibleBookFactory(name='Romans', abbreviation='Rom', slug='romans',
                     book_number=45, testament='NT')

    data = json.loads(client.get('/api/suggest/?q=Rom+8:30').content)
    groups = {group['label']: group for group in data['groups']}
    assert 'Scripture' in groups
    assert groups['Scripture']['items'][0]['url'].startswith('/scripture/romans/')


@pytest.mark.django_db
def test_every_response_offers_the_full_search(client):
    data = json.loads(client.get('/api/suggest/?q=faith').content)
    assert data['search_url'].startswith('/search/?q=')


@pytest.mark.django_db
def test_the_navbar_loads_the_typeahead_and_shortcuts(client):
    body = client.get('/').content.decode()
    assert 'js/suggest.js' in body
    assert 'js/shortcuts.js' in body
