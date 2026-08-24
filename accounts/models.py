from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from . import scheduling


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    is_blocked = models.BooleanField(default=False)

    # Memorisation practice. A streak is the one number that reliably brings
    # someone back tomorrow, and it costs two fields to keep.
    review_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_review_on = models.DateField(null=True, blank=True)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile for {self.user.username}"

    def record_review(self, today=None):
        """Count one review and keep the daily streak.

        A streak counts consecutive *days* on which something was reviewed,
        not reviews — twenty in one sitting is one day's practice.
        """
        today = today or timezone.localdate()
        if self.last_review_on != today:
            if self.last_review_on == today - timedelta(days=1):
                self.review_streak += 1
            else:
                self.review_streak = 1
            self.last_review_on = today
        self.longest_streak = max(self.longest_streak, self.review_streak)
        self.total_reviews += 1
        self.save(update_fields=[
            'review_streak', 'longest_streak', 'last_review_on', 'total_reviews',
        ])
        return self


@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


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


class InlineComment(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('question', 'Question Text'),
        ('answer', 'Answer Text'),
        ('commentary', 'Commentary'),
        ('scripture', 'Scripture Proofs'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inline_comments'
    )
    question = models.ForeignKey(
        'catechism.Question',
        on_delete=models.CASCADE,
        related_name='inline_comments'
    )
    commentary = models.ForeignKey(
        'catechism.Commentary',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inline_comments'
    )
    content_type_tag = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    selected_text = models.TextField()
    occurrence_index = models.PositiveIntegerField(default=0)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.comment_text[:50] + '...' if len(self.comment_text) > 50 else self.comment_text
        return f"Comment by {self.user.username}: {preview}"


class MemorizationCard(models.Model):
    """One catechism answer a reader is committing to memory.

    The Standards were written to be memorised, so the review schedule is the
    natural companion to the text. Scheduling itself lives in
    ``accounts.scheduling``; this model only stores the card's state.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memorization_cards',
    )
    question = models.ForeignKey(
        'catechism.Question',
        on_delete=models.CASCADE,
        related_name='memorization_cards',
    )
    repetitions = models.PositiveIntegerField(default=0)
    interval_days = models.PositiveIntegerField(default=0)
    ease = models.FloatField(default=scheduling.DEFAULT_EASE)
    due_on = models.DateField(default=timezone.localdate, db_index=True)
    lapses = models.PositiveIntegerField(default=0)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_on', 'question__catechism__abbreviation', 'question__number']
        unique_together = ('user', 'question')

    def __str__(self):
        prefix = self.question.catechism.item_prefix
        return f"{self.user.username}: {prefix}{self.question.number} due {self.due_on}"

    @property
    def is_mature(self):
        """Recalled at three weeks or more — treated as known, not learning."""
        return self.interval_days >= scheduling.MATURE_INTERVAL_DAYS

    @property
    def is_new(self):
        return self.repetitions == 0 and self.last_reviewed_at is None

    def is_due(self, today=None):
        return self.due_on <= (today or timezone.localdate())

    def apply_review(self, grade, today=None):
        """Record a review outcome and save the new schedule."""
        today = today or timezone.localdate()
        if grade == scheduling.AGAIN and not self.is_new:
            self.lapses += 1
        self.repetitions, self.interval_days, self.ease, self.due_on = scheduling.review(
            self.repetitions, self.interval_days, self.ease, grade, today,
        )
        self.last_reviewed_at = timezone.now()
        self.save(update_fields=[
            'repetitions', 'interval_days', 'ease', 'due_on', 'lapses',
            'last_reviewed_at',
        ])
        return self


class ReadingPosition(models.Model):
    """Where a reader last was in each document.

    One row per reader per document, updated as they read, so returning to a
    long confession does not mean hunting for the chapter they left off in.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_positions',
    )
    catechism = models.ForeignKey(
        'catechism.Catechism',
        on_delete=models.CASCADE,
        related_name='reading_positions',
    )
    question = models.ForeignKey(
        'catechism.Question',
        on_delete=models.CASCADE,
        related_name='reading_positions',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('user', 'catechism')

    def __str__(self):
        prefix = self.question.catechism.item_prefix
        return f"{self.user.username} at {prefix}{self.question.number}"

    @classmethod
    def remember(cls, user, question):
        """Record that this reader is here now."""
        if not user.is_authenticated:
            return None
        position, _ = cls.objects.update_or_create(
            user=user, catechism=question.catechism,
            defaults={'question': question},
        )
        return position


class ReviewDay(models.Model):
    """How much was practised on a given day.

    A streak says whether you turned up; this says how much you did, which is
    what makes a year of practice visible as a shape rather than a number.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_days',
    )
    day = models.DateField(db_index=True)
    reviews = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-day']
        unique_together = ('user', 'day')

    def __str__(self):
        return f"{self.user.username} {self.day}: {self.reviews}"

    @classmethod
    def record(cls, user, today=None):
        today = today or timezone.localdate()
        day, created = cls.objects.get_or_create(user=user, day=today, defaults={'reviews': 1})
        if not created:
            cls.objects.filter(pk=day.pk).update(reviews=models.F('reviews') + 1)
            day.refresh_from_db(fields=['reviews'])
        return day
