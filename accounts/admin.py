from django.contrib import admin
from .models import UserNote, Highlight


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'updated_at')
    list_filter = ('user',)
    search_fields = ('text',)


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'commentary', 'text_preview', 'created_at')
    list_filter = ('user',)
    raw_id_fields = ('commentary',)

    def text_preview(self, obj):
        return obj.selected_text[:80] + '...' if len(obj.selected_text) > 80 else obj.selected_text
    text_preview.short_description = 'Text'
