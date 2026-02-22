import json

import pytest
from django.test import Client
from django.contrib.auth.models import User

from accounts.models import UserNote
from .conftest import UserNoteFactory, HighlightFactory


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestSignupView:
    def test_get(self, client):
        resp = client.get('/accounts/signup/')
        assert resp.status_code == 200

    def test_post_valid(self, client):
        resp = client.post('/accounts/signup/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Str0ngP@ss!',
            'password2': 'Str0ngP@ss!',
        })
        assert resp.status_code == 302
        assert User.objects.filter(username='newuser').exists()

    def test_post_invalid(self, client):
        resp = client.post('/accounts/signup/', {
            'username': '',
            'email': 'bad',
            'password1': '123',
            'password2': '456',
        })
        assert resp.status_code == 200
        assert not User.objects.filter(username='').exists()


@pytest.mark.django_db
class TestLoginView:
    def test_get(self, client):
        resp = client.get('/accounts/login/')
        assert resp.status_code == 200

    def test_post_valid(self, client, user):
        resp = client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        assert resp.status_code == 302

    def test_post_invalid(self, client, user):
        resp = client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        assert resp.status_code == 200


@pytest.mark.django_db
class TestDashboardView:
    def test_requires_login(self, client):
        resp = client.get('/accounts/dashboard/')
        assert resp.status_code == 302
        assert '/accounts/login/' in resp.url

    def test_shows_notes(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        UserNoteFactory(user=user, question=q1, text='My note')
        resp = authenticated_client.get('/accounts/dashboard/')
        assert resp.status_code == 200
        assert len(resp.context['notes']) == 1


@pytest.mark.django_db
class TestNoteSaveView:
    def test_requires_login(self, client, setup_data):
        cat, topic, q1, source, commentary = setup_data
        resp = client.post(f'/accounts/notes/save/{q1.pk}/', {'text': 'hello'})
        assert resp.status_code == 302
        assert '/accounts/login/' in resp.url

    def test_creates_note(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        resp = authenticated_client.post(f'/accounts/notes/save/{q1.pk}/', {'text': 'My note'})
        assert resp.status_code == 302
        assert UserNote.objects.filter(user=user, question=q1).exists()

    def test_updates_existing(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        UserNoteFactory(user=user, question=q1, text='Old note')
        authenticated_client.post(f'/accounts/notes/save/{q1.pk}/', {'text': 'Updated'})
        note = UserNote.objects.get(user=user, question=q1)
        assert note.text == 'Updated'


@pytest.mark.django_db
class TestNoteDeleteView:
    def test_delete_own(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        note = UserNoteFactory(user=user, question=q1)
        resp = authenticated_client.post(f'/accounts/notes/{note.pk}/delete/')
        assert resp.status_code == 302
        assert not UserNote.objects.filter(pk=note.pk).exists()

    def test_delete_other_user_denied(self, authenticated_client, other_user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        note = UserNoteFactory(user=other_user, question=q1)
        resp = authenticated_client.post(f'/accounts/notes/{note.pk}/delete/')
        assert resp.status_code == 404
        assert UserNote.objects.filter(pk=note.pk).exists()


@pytest.mark.django_db
class TestHighlightListCreateView:
    def test_get(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        HighlightFactory(user=user, commentary=commentary, selected_text='test')
        resp = authenticated_client.get(
            f'/accounts/highlights/?commentary_id={commentary.pk}'
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert len(data['highlights']) == 1

    def test_create_post(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        resp = authenticated_client.post(
            '/accounts/highlights/',
            data=json.dumps({
                'commentary_id': commentary.pk,
                'selected_text': 'body text',
                'occurrence_index': 0,
            }),
            content_type='application/json',
        )
        assert resp.status_code == 201
        data = json.loads(resp.content)
        assert data['created'] is True

    def test_create_missing_fields(self, authenticated_client, setup_data):
        resp = authenticated_client.post(
            '/accounts/highlights/',
            data=json.dumps({'commentary_id': None}),
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_requires_login(self, client):
        resp = client.get('/accounts/highlights/')
        assert resp.status_code == 302


@pytest.mark.django_db
class TestHighlightDeleteView:
    def test_delete_own(self, authenticated_client, user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        h = HighlightFactory(user=user, commentary=commentary)
        resp = authenticated_client.delete(f'/accounts/highlights/{h.pk}/delete/')
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data['deleted'] is True

    def test_delete_other_user_404(self, authenticated_client, other_user, setup_data):
        cat, topic, q1, source, commentary = setup_data
        h = HighlightFactory(user=other_user, commentary=commentary)
        resp = authenticated_client.delete(f'/accounts/highlights/{h.pk}/delete/')
        assert resp.status_code == 404
