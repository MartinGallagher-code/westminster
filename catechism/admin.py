from django.contrib import admin
from .models import Catechism, Topic, Question, CommentarySource, Commentary, FisherSubQuestion, ScripturePassage


@admin.register(Catechism)
class CatechismAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'total_questions', 'year')
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
