from django.db import models


class Catechism(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    total_questions = models.PositiveIntegerField()

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return self.abbreviation

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:catechism_home', kwargs={'catechism_slug': self.slug})


class Topic(models.Model):
    catechism = models.ForeignKey(
        Catechism, on_delete=models.CASCADE, related_name='topics'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    question_start = models.PositiveIntegerField()
    question_end = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = [('catechism', 'slug'), ('catechism', 'order')]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:topic_detail', kwargs={
            'catechism_slug': self.catechism.slug,
            'slug': self.slug,
        })


class Question(models.Model):
    catechism = models.ForeignKey(
        Catechism, on_delete=models.CASCADE, related_name='questions'
    )
    number = models.PositiveIntegerField(db_index=True)
    question_text = models.TextField()
    answer_text = models.TextField()
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='questions'
    )
    proof_texts = models.TextField(
        blank=True,
        help_text="Semicolon-separated Scripture references"
    )

    class Meta:
        ordering = ['number']
        unique_together = [('catechism', 'number')]

    def __str__(self):
        return f"Q{self.number}: {self.question_text[:60]}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:question_detail', kwargs={
            'catechism_slug': self.catechism.slug,
            'number': self.number,
        })

    def get_previous(self):
        if self.number <= 1:
            return None
        return Question.objects.filter(
            catechism=self.catechism, number=self.number - 1
        ).first()

    def get_next(self):
        if self.number >= self.catechism.total_questions:
            return None
        return Question.objects.filter(
            catechism=self.catechism, number=self.number + 1
        ).first()

    def get_proof_text_list(self):
        if not self.proof_texts:
            return []
        return [ref.strip() for ref in self.proof_texts.split(';') if ref.strip()]


class CommentarySource(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=200)
    year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Commentary(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='commentaries'
    )
    source = models.ForeignKey(
        CommentarySource, on_delete=models.CASCADE, related_name='entries'
    )
    body = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "commentaries"
        unique_together = ('question', 'source')
        ordering = ['source__slug']

    def __str__(self):
        return f"{self.source.name} on Q{self.question.number}"


class FisherSubQuestion(models.Model):
    commentary = models.ForeignKey(
        Commentary, on_delete=models.CASCADE, related_name='sub_questions'
    )
    number = models.PositiveIntegerField()
    question_text = models.TextField()
    answer_text = models.TextField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Q{self.commentary.question.number}.{self.number}"


class ScripturePassage(models.Model):
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    text = models.TextField()

    class Meta:
        ordering = ['reference']

    def __str__(self):
        return self.reference


class CrossReference(models.Model):
    wsc_question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='wlc_cross_refs'
    )
    wlc_question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='wsc_cross_refs'
    )

    class Meta:
        unique_together = ('wsc_question', 'wlc_question')
        ordering = ['wsc_question__number', 'wlc_question__number']

    def __str__(self):
        return f"WSC Q{self.wsc_question.number} ↔ WLC Q{self.wlc_question.number}"
