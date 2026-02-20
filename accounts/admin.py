from django.contrib import admin
from .models import UserNote


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'updated_at')
    list_filter = ('user',)
    search_fields = ('text',)
