from django.conf import settings
from django.db import models


class UserNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    question = models.ForeignKey(
        'catechism.Question',
        on_delete=models.CASCADE,
        related_name='user_notes'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('user', 'question')

    def __str__(self):
        prefix = self.question.catechism.item_prefix
        return f"Note by {self.user.username} on {prefix}{self.question.number}"


class Highlight(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='highlights'
    )
    commentary = models.ForeignKey(
        'catechism.Commentary',
        on_delete=models.CASCADE,
        related_name='highlights'
    )
    selected_text = models.TextField()
    occurrence_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ('user', 'commentary', 'selected_text', 'occurrence_index')

    def __str__(self):
        preview = self.selected_text[:50] + '...' if len(self.selected_text) > 50 else self.selected_text
        return f"Highlight by {self.user.username}: {preview}"
