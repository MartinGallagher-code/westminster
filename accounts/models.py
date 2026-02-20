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
        return f"Note by {self.user.username} on Q{self.question.number}"
