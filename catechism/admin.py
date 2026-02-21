from django.contrib import admin
from .models import (
    Catechism, Topic, Question, CommentarySource, Commentary, FisherSubQuestion,
    ScripturePassage, CrossReference, StandardCrossReference,
    BibleBook, ScriptureIndex, ComparisonTheme, ComparisonEntry,
)


@admin.register(Catechism)
class CatechismAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'total_questions', 'year', 'document_type')
    prepopulated_fields = {'slug': ('abbreviation',)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'catechism', 'order', 'question_start', 'question_end')
    list_filter = ('catechism',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('number', 'catechism', 'question_text', 'topic')
    list_filter = ('catechism', 'topic')
    search_fields = ('question_text', 'answer_text')


@admin.register(CommentarySource)
class CommentarySourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'year')
    prepopulated_fields = {'slug': ('name',)}


class FisherSubQuestionInline(admin.TabularInline):
    model = FisherSubQuestion
    extra = 0


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ('question', 'source')
    list_filter = ('source',)
    inlines = [FisherSubQuestionInline]


@admin.register(ScripturePassage)
class ScripturePassageAdmin(admin.ModelAdmin):
    list_display = ('reference',)
    search_fields = ('reference', 'text')


@admin.register(CrossReference)
class CrossReferenceAdmin(admin.ModelAdmin):
    list_display = ('wsc_question', 'wlc_question')
    raw_id_fields = ('wsc_question', 'wlc_question')


@admin.register(StandardCrossReference)
class StandardCrossReferenceAdmin(admin.ModelAdmin):
    list_display = ('source_question', 'target_question')
    raw_id_fields = ('source_question', 'target_question')


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'book_number', 'testament')
    list_filter = ('testament',)


@admin.register(ScriptureIndex)
class ScriptureIndexAdmin(admin.ModelAdmin):
    list_display = ('reference', 'book', 'question')
    list_filter = ('book',)
    raw_id_fields = ('question',)


class ComparisonEntryInline(admin.TabularInline):
    model = ComparisonEntry
    extra = 0


@admin.register(ComparisonTheme)
class ComparisonThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ComparisonEntryInline]
