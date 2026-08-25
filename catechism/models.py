from django.db import models
from django.db.models.signals import post_delete, post_migrate, post_save


class Catechism(models.Model):
    CATECHISM = 'catechism'
    CONFESSION = 'confession'
    SYSTEMATIC_THEOLOGY = 'systematic_theology'
    DOCUMENT_TYPE_CHOICES = [
        (CATECHISM, 'Catechism'),
        (CONFESSION, 'Confession'),
        (SYSTEMATIC_THEOLOGY, 'Systematic Theology'),
    ]

    WESTMINSTER = 'westminster'
    THREE_FORMS_OF_UNITY = 'three_forms_of_unity'
    REFORMED_CONFESSIONS = 'reformed_confessions'
    OTHER = 'other'
    TRADITION_CHOICES = [
        (WESTMINSTER, 'Westminster Standards'),
        (THREE_FORMS_OF_UNITY, 'Three Forms of Unity'),
        (REFORMED_CONFESSIONS, 'Reformed Confessions'),
        (OTHER, 'Other'),
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
    tradition = models.CharField(
        max_length=30, choices=TRADITION_CHOICES, default=OTHER
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
    def is_systematic_theology(self):
        return self.document_type == self.SYSTEMATIC_THEOLOGY

    @property
    def is_prose_document(self):
        """True for confessions and systematic theologies (prose chapters, not Q&A)."""
        return self.is_confession or self.is_systematic_theology

    @property
    def item_name(self):
        if self.is_confession:
            return 'Section'
        if self.is_systematic_theology:
            return 'Chapter'
        return 'Question'

    @property
    def item_name_plural(self):
        if self.is_confession:
            return 'Sections'
        if self.is_systematic_theology:
            return 'Chapters'
        return 'Questions'

    @property
    def item_prefix(self):
        return '' if self.is_prose_document else 'Q'

    @property
    def topic_name(self):
        if self.is_confession:
            return 'Chapter'
        if self.is_systematic_theology:
            return 'Book'
        return 'Topic'

    @property
    def topic_name_plural(self):
        if self.is_confession:
            return 'Chapters'
        if self.is_systematic_theology:
            return 'Books'
        return 'Topics'

    def get_item_list_url(self):
        return self.get_absolute_url()

    def get_topic_list_url(self):
        return self.get_absolute_url()


# Every rendered row asks its document a question. ``Question
# .get_absolute_url`` needs the slug and the document type to pick a route,
# and ``display_number`` needs the type again — so a queryset that had not
# said ``select_related('catechism')`` cost one query per row. A single
# Larger Catechism question page issued 204 of them, all identical, and the
# document home pages were as bad. The call sites are templates all over the
# site, so a select_related here and there would leave the next one to
# reintroduce it.
#
# There are only ever a dozen or so documents, so they are held in a
# process-level map and rebuilt whenever one is saved or deleted — the same
# approach Django takes for content types.
_DOCUMENTS = None


def _document_map():
    global _DOCUMENTS
    if _DOCUMENTS is None:
        _DOCUMENTS = {
            row['id']: row
            for row in Catechism.objects.values('id', 'slug', 'document_type')
        }
    return _DOCUMENTS


def _forget_documents(**kwargs):
    """Drop the map. Connected to Catechism saves, deletes and migrations."""
    global _DOCUMENTS
    _DOCUMENTS = None


class DocumentFacts:
    """The little a row needs to know about the document it belongs to."""

    __slots__ = ('slug', 'document_type')

    def __init__(self, slug, document_type):
        self.slug = slug
        self.document_type = document_type

    @property
    def is_confession(self):
        return self.document_type == Catechism.CONFESSION

    @property
    def is_systematic_theology(self):
        return self.document_type == Catechism.SYSTEMATIC_THEOLOGY

    @property
    def is_prose_document(self):
        return self.is_confession or self.is_systematic_theology


class BelongsToDocument:
    """Mixin giving a row its document's slug and type without a query.

    Prefers an already-loaded related object, so nothing changes for a
    queryset that did select_related; falls back to fetching the row when the
    map has no entry for it, which keeps the answer correct even if a document
    was created in a way that fires no signal.
    """

    @property
    def document(self):
        loaded = self._state.fields_cache.get('catechism')
        if loaded is not None:
            return loaded
        entry = _document_map().get(self.catechism_id)
        if entry is None:
            _forget_documents()
            entry = _document_map().get(self.catechism_id)
        if entry is None:
            return self.catechism
        return DocumentFacts(entry['slug'], entry['document_type'])


class Topic(BelongsToDocument, models.Model):
    catechism = models.ForeignKey(
        Catechism, on_delete=models.CASCADE, related_name='topics'
    )
    name = models.CharField(max_length=200)
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
        """Returns order.1 for prose documents (confessions/sys theologies), plain start for catechisms."""
        if self.document.is_prose_document:
            return f"{self.order}.1"
        return str(self.question_start)

    @property
    def display_end(self):
        """Returns order.N for prose documents (confessions/sys theologies), plain end for catechisms."""
        if self.document.is_prose_document:
            count = self.question_end - self.question_start + 1
            return f"{self.order}.{count}"
        return str(self.question_end)

    def get_absolute_url(self):
        from django.urls import reverse
        document = self.document
        name = 'catechism:chapter_detail' if document.is_confession else 'catechism:topic_detail'
        return reverse(name, kwargs={
            'catechism_slug': document.slug,
            'slug': self.slug,
        })


class Question(BelongsToDocument, models.Model):
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
        """Returns book/chapter.item for prose documents (e.g. '1.5'), plain number for catechisms."""
        if self.document.is_prose_document and self.topic:
            section = self.number - self.topic.question_start + 1
            return f"{self.topic.order}.{section}"
        return str(self.number)

    def get_absolute_url(self):
        from django.urls import reverse
        document = self.document
        name = 'catechism:section_detail' if document.is_confession else 'catechism:question_detail'
        return reverse(name, kwargs={
            'catechism_slug': document.slug,
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


class ComparisonSet(models.Model):
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
        return reverse('catechism:compare_set', kwargs={'set_slug': self.slug})


class ComparisonTheme(models.Model):
    comparison_set = models.ForeignKey(
        ComparisonSet, on_delete=models.CASCADE, related_name='themes',
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    locus = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('comparison_set', 'slug')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catechism:compare_set_theme', kwargs={
            'set_slug': self.comparison_set.slug,
            'theme_slug': self.slug,
        })

    def atlas_locus(self):
        """The nearest Westminster Standards Atlas locus for this theme's
        classical locus, or None. See catechism.atlas.comparison_locus_atlas."""
        from .atlas import comparison_locus_atlas
        return comparison_locus_atlas(self.locus)


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
        # The comparison pages print each section's document alongside it, so
        # the document comes too: without it the parallel reading spent a
        # query per cell naming the edition it had just fetched.
        return Question.objects.filter(
            catechism=self.catechism,
            number__gte=self.question_start,
            number__lte=self.question_end,
        ).select_related('topic', 'catechism')


class OntologyLocus(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=8, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    overview = models.TextField(blank=True)
    color = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)
    atlas_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_atlas_url(self):
        from .atlas import atlas_url
        return atlas_url(self.atlas_path)


class OntologyAttribute(models.Model):
    locus = models.ForeignKey(
        OntologyLocus, on_delete=models.CASCADE, related_name='attributes'
    )
    slug = models.SlugField()
    name = models.CharField(max_length=150)
    baseline_label = models.CharField(max_length=200, blank=True)
    baseline_slug = models.SlugField(blank=True)
    baseline_description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    atlas_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['locus__order', 'order', 'name']
        unique_together = ('locus', 'slug')

    def __str__(self):
        return f"{self.locus.name}: {self.name}"

    def get_atlas_url(self):
        from .atlas import atlas_url
        return atlas_url(self.atlas_path)


class DoctrineHead(models.Model):
    locus = models.ForeignKey(
        OntologyLocus, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctrine_heads'
    )
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    atlas_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['locus__order', 'order', 'name']

    def __str__(self):
        return self.name

    def get_atlas_url(self):
        from .atlas import atlas_url
        return atlas_url(self.atlas_path)


class QuestionOntologyTag(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='ontology_tags'
    )
    attribute = models.ForeignKey(
        OntologyAttribute, on_delete=models.CASCADE, related_name='question_tags'
    )
    is_representative = models.BooleanField(default=False)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['attribute__locus__order', 'attribute__order']
        unique_together = ('question', 'attribute')

    def __str__(self):
        return f"{self.question} -> {self.attribute}"


class QuestionDoctrineHead(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='doctrine_head_links'
    )
    doctrine_head = models.ForeignKey(
        DoctrineHead, on_delete=models.CASCADE, related_name='question_links'
    )

    class Meta:
        ordering = ['doctrine_head__locus__order', 'doctrine_head__order']
        unique_together = ('question', 'doctrine_head')

    def __str__(self):
        return f"{self.question} -> {self.doctrine_head}"


class DataVersion(models.Model):
    """Tracks the hash of source data files to skip unchanged loads on deploy."""
    name = models.CharField(max_length=100, unique=True)
    data_hash = models.CharField(max_length=64)
    loaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.data_hash[:8]}…)"


# The document map above is only safe because it is dropped whenever the set
# of documents could have changed: a save, a delete, or a migration (which is
# how the test database and a fresh deploy get their rows).
post_save.connect(_forget_documents, sender=Catechism)
post_delete.connect(_forget_documents, sender=Catechism)
post_migrate.connect(_forget_documents)
