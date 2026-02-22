from django.db import models


class Catechism(models.Model):
    CATECHISM = 'catechism'
    CONFESSION = 'confession'
    DOCUMENT_TYPE_CHOICES = [
        (CATECHISM, 'Catechism'),
        (CONFESSION, 'Confession'),
    ]

    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    total_questions = models.PositiveIntegerField()
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPE_CHOICES, default=CATECHISM
    )

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return self.abbreviation

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:catechism_home', kwargs={'catechism_slug': self.slug})

    @property
    def is_confession(self):
        return self.document_type == self.CONFESSION

    @property
    def item_name(self):
        return 'Section' if self.is_confession else 'Question'

    @property
    def item_name_plural(self):
        return 'Sections' if self.is_confession else 'Questions'

    @property
    def item_prefix(self):
        return '§' if self.is_confession else 'Q'

    @property
    def topic_name(self):
        return 'Chapter' if self.is_confession else 'Topic'

    @property
    def topic_name_plural(self):
        return 'Chapters' if self.is_confession else 'Topics'

    def get_item_list_url(self):
        from django.urls import reverse
        name = 'catechism:section_list' if self.is_confession else 'catechism:question_list'
        return reverse(name, kwargs={'catechism_slug': self.slug})

    def get_topic_list_url(self):
        from django.urls import reverse
        name = 'catechism:chapter_list' if self.is_confession else 'catechism:topic_list'
        return reverse(name, kwargs={'catechism_slug': self.slug})


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

    @property
    def display_start(self):
        """Returns chapter.1 for confessions, plain start number for catechisms."""
        if self.catechism.is_confession:
            return f"{self.order}.1"
        return str(self.question_start)

    @property
    def display_end(self):
        """Returns chapter.N for confessions, plain end number for catechisms."""
        if self.catechism.is_confession:
            count = self.question_end - self.question_start + 1
            return f"{self.order}.{count}"
        return str(self.question_end)

    def get_absolute_url(self):
        from django.urls import reverse
        name = 'catechism:chapter_detail' if self.catechism.is_confession else 'catechism:topic_detail'
        return reverse(name, kwargs={
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
        prefix = self.catechism.item_prefix
        return f"{prefix}{self.number}: {self.question_text[:60]}"

    @property
    def display_number(self):
        """Returns chapter.section for confessions (e.g. '1.5'), plain number for catechisms."""
        if self.catechism.is_confession and self.topic:
            section = self.number - self.topic.question_start + 1
            return f"{self.topic.order}.{section}"
        return str(self.number)

    def get_absolute_url(self):
        from django.urls import reverse
        name = 'catechism:section_detail' if self.catechism.is_confession else 'catechism:question_detail'
        return reverse(name, kwargs={
            'catechism_slug': self.catechism.slug,
            'number': self.number,
        })

    def get_previous(self):
        if self.number <= 1:
            return None
        return Question.objects.filter(
            catechism=self.catechism, number=self.number - 1
        ).select_related('topic').first()

    def get_next(self):
        if self.number >= self.catechism.total_questions:
            return None
        return Question.objects.filter(
            catechism=self.catechism, number=self.number + 1
        ).select_related('topic').first()

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
        prefix = self.question.catechism.item_prefix
        return f"{self.source.name} on {prefix}{self.question.number}"


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


class StandardCrossReference(models.Model):
    source_question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='cross_refs_from'
    )
    target_question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='cross_refs_to'
    )

    class Meta:
        unique_together = ('source_question', 'target_question')
        ordering = ['source_question__catechism__abbreviation', 'source_question__number']

    def __str__(self):
        src = self.source_question
        tgt = self.target_question
        return (
            f"{src.catechism.abbreviation} {src.catechism.item_prefix}{src.number} → "
            f"{tgt.catechism.abbreviation} {tgt.catechism.item_prefix}{tgt.number}"
        )


class BibleBook(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    abbreviation = models.CharField(max_length=20)
    book_number = models.PositiveIntegerField(unique=True)
    testament = models.CharField(max_length=2, choices=[
        ('OT', 'Old Testament'),
        ('NT', 'New Testament'),
    ])

    class Meta:
        ordering = ['book_number']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:scripture_book', kwargs={'book_slug': self.slug})


class ScriptureIndex(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='scripture_index_entries'
    )
    book = models.ForeignKey(
        BibleBook, on_delete=models.CASCADE, related_name='index_entries'
    )
    reference = models.CharField(max_length=255)

    class Meta:
        ordering = ['book__book_number', 'question__catechism__abbreviation', 'question__number']
        unique_together = ('question', 'reference')

    def __str__(self):
        return f"{self.reference} → {self.question}"


class ComparisonTheme(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:compare_theme', kwargs={'theme_slug': self.slug})


class ComparisonEntry(models.Model):
    theme = models.ForeignKey(
        ComparisonTheme, on_delete=models.CASCADE, related_name='entries'
    )
    catechism = models.ForeignKey(
        Catechism, on_delete=models.CASCADE, related_name='comparison_entries'
    )
    question_start = models.PositiveIntegerField()
    question_end = models.PositiveIntegerField()

    class Meta:
        ordering = ['catechism__abbreviation']
        unique_together = ('theme', 'catechism')

    def __str__(self):
        return f"{self.theme.name} - {self.catechism.abbreviation}"

    def get_questions(self):
        return Question.objects.filter(
            catechism=self.catechism,
            number__gte=self.question_start,
            number__lte=self.question_end,
        ).select_related('topic')
