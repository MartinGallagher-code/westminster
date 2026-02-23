import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# All-caps section headers in confessions (e.g., Second Helvetic Confession).
# Matches "CANONICAL SCRIPTURE." or "HERESIES." or "MAN IS NOT CAPABLE OF GOOD Per Se."
_HEADER_RE = re.compile(
    r"([A-Z][A-Z']+(?:[\s,]+[A-Z][A-Z']+)+(?:\s+[A-Za-z']+)*\."
    r"|[A-Z]{3,}\.)"
)


@register.filter
def get_item(dictionary, key):
    """Look up a dictionary value by key in templates: {{ mydict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


@register.filter
def format_confession_sections(text):
    """Format confession text with paragraph breaks and styled all-caps section headers."""
    if not text:
        return text

    parts = _HEADER_RE.split(text)
    html_parts = []

    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Captured header group — start a new paragraph with bold header
            html_parts.append(
                f'</p>\n<p><strong class="confession-section-header">'
                f'{escape(part)}</strong> '
            )
        else:
            # Regular text — escape and convert double newlines to paragraph breaks
            escaped = escape(part)
            paragraphs = [p.strip() for p in escaped.split('\n\n') if p.strip()]
            html_parts.append('</p>\n<p>'.join(paragraphs))

    html = '<p>' + ''.join(html_parts) + '</p>'
    html = re.sub(r'<p>\s*</p>\n?', '', html)
    return mark_safe(html)
