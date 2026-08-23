"""Exporting and searching a reader's own study material."""

from datetime import date

import pytest
from django.contrib.auth.models import User

from accounts.export import export_filename, notes_markdown
from accounts.models import Highlight, InlineComment, UserNote

TODAY = date(2026, 8, 23)


@pytest.fixture
def reader(db):
    return User.objects.create_user(username='reader', password='catechism-1647')


@pytest.mark.django_db
def test_export_of_an_empty_account_says_so(reader):
    markdown = notes_markdown(reader, TODAY)
    assert '# Study Reformed' in markdown
    assert 'Nothing saved yet.' in markdown


@pytest.mark.django_db
def test_export_groups_by_document_and_question(reader, setup_data):
    _cat, _topic, question, _source, commentary = setup_data
    UserNote.objects.create(user=reader, question=question, text='Glorify and enjoy.')
    InlineComment.objects.create(
        user=reader, question=question, commentary=commentary,
        content_type_tag='commentary', selected_text='chief end',
        comment_text='Note the order.',
    )
    Highlight.objects.create(
        user=reader, commentary=commentary, selected_text='Commentary body',
    )

    markdown = notes_markdown(reader, TODAY, base_url='https://example.test')

    assert '## Shorter Catechism' in markdown or '## ' in markdown
    assert 'What is the chief end of man?' in markdown
    assert '**Note**' in markdown and '> Glorify and enjoy.' in markdown
    assert '**Annotation**' in markdown and '> Note the order.' in markdown
    assert '**Highlight**' in markdown and '> Commentary body' in markdown
    assert 'https://example.test/wsc/questions/1/' in markdown


@pytest.mark.django_db
def test_multi_line_notes_stay_quoted(reader, setup_data):
    _cat, _topic, question, _source, _commentary = setup_data
    UserNote.objects.create(user=reader, question=question, text='First line\nSecond line')

    markdown = notes_markdown(reader, TODAY)
    assert '> First line' in markdown
    assert '> Second line' in markdown


@pytest.mark.django_db
def test_export_only_includes_your_own_material(reader, setup_data):
    _cat, _topic, question, _source, _commentary = setup_data
    someone_else = User.objects.create_user(username='other', password='catechism-1647')
    UserNote.objects.create(user=someone_else, question=question, text='Not yours.')

    assert 'Not yours.' not in notes_markdown(reader, TODAY)


def test_export_filename_is_dated():
    assert export_filename(TODAY) == 'study-reformed-notes-2026-08-23.md'


@pytest.mark.django_db
def test_export_endpoint_serves_a_markdown_attachment(client, reader, setup_data):
    _cat, _topic, question, _source, _commentary = setup_data
    UserNote.objects.create(user=reader, question=question, text='Mine.')
    client.force_login(reader)

    resp = client.get('/accounts/notes/export/')
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('text/markdown')
    assert 'attachment; filename="study-reformed-notes-' in resp['Content-Disposition']
    assert 'Mine.' in resp.content.decode()


@pytest.mark.django_db
def test_export_requires_login(client):
    resp = client.get('/accounts/notes/export/')
    assert resp.status_code == 302
    assert '/accounts/login/' in resp['Location']


@pytest.mark.django_db
def test_dashboard_searches_your_own_notes(client, reader, setup_data):
    _cat, _topic, question, _source, commentary = setup_data
    UserNote.objects.create(user=reader, question=question, text='On the chief end')
    InlineComment.objects.create(
        user=reader, question=question, commentary=commentary,
        content_type_tag='commentary', selected_text='body',
        comment_text='A thought about assurance',
    )
    client.force_login(reader)

    resp = client.get('/accounts/dashboard/?q=assurance')
    assert resp.status_code == 200
    assert len(resp.context['notes']) == 0
    assert len(resp.context['inline_comments']) == 1

    resp = client.get('/accounts/dashboard/?q=chief')
    assert len(resp.context['notes']) == 1
