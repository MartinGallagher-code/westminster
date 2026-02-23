from django.contrib import admin
from .models import UserNote, Highlight, InlineComment, SupporterSubscription


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


@admin.register(InlineComment)
class InlineCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'content_type_tag', 'comment_preview', 'created_at')
    list_filter = ('user', 'content_type_tag')
    raw_id_fields = ('question', 'commentary')

    def comment_preview(self, obj):
        return obj.comment_text[:80] + '...' if len(obj.comment_text) > 80 else obj.comment_text
    comment_preview.short_description = 'Comment'


@admin.register(SupporterSubscription)
class SupporterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'current_period_end', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email', 'stripe_customer_id')
    readonly_fields = (
        'stripe_customer_id', 'stripe_subscription_id',
        'created_at', 'updated_at',
    )
