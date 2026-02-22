import pytest
from accounts.forms import SignupForm, NoteForm


@pytest.mark.django_db
class TestSignupForm:
    def test_valid(self):
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Str0ngP@ss!',
            'password2': 'Str0ngP@ss!',
        })
        assert form.is_valid()

    def test_missing_email(self):
        form = SignupForm(data={
            'username': 'newuser',
            'email': '',
            'password1': 'Str0ngP@ss!',
            'password2': 'Str0ngP@ss!',
        })
        assert not form.is_valid()
        assert 'email' in form.errors


class TestNoteForm:
    def test_valid(self):
        form = NoteForm(data={'text': 'A note about this question.'})
        assert form.is_valid()

    def test_empty(self):
        form = NoteForm(data={'text': ''})
        assert not form.is_valid()
        assert 'text' in form.errors
