from django.contrib import admin
from .models import Topic, Question, CommentarySource, Commentary, FisherSubQuestion


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'question_start', 'question_end')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('number', 'question_text', 'topic')
    list_filter = ('topic',)
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
