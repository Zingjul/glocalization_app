# posts/templatetags/__init__.py (create if doesn't exist)

# posts/templatetags/post_filters.py
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape, urlize
import re

register = template.Library()

@register.filter(name='format_post_content')
def format_post_content(text):
    """
    Custom filter that:
    1. Preserves line breaks and paragraphs
    2. Makes URLs clickable
    3. Preserves basic formatting
    4. Optionally supports basic markdown-like syntax
    """
    if not text:
        return ''
    
    # First escape HTML to prevent XSS
    text = escape(text)
    
    # Convert URLs to clickable links (with target="_blank")
    text = urlize(text, nofollow=True, autoescape=False)
    
    # Add target="_blank" to all links for external opening
    text = text.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ')
    
    # Preserve paragraphs (double line breaks)
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        if paragraph.strip():
            # Convert single line breaks to <br> within paragraphs
            paragraph = paragraph.replace('\n', '<br>')
            formatted_paragraphs.append(f'<p>{paragraph}</p>')
    
    result = ''.join(formatted_paragraphs)
    
    # If no paragraphs were created, just handle line breaks
    if not formatted_paragraphs:
        result = text.replace('\n', '<br>')
    
    return mark_safe(result)

@register.filter(name='format_with_markdown')
def format_with_markdown(text):
    """
    Enhanced formatter with basic markdown support
    """
    if not text:
        return ''
    
    # Escape HTML first
    text = escape(text)
    
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    
    # Make URLs clickable
    text = urlize(text, nofollow=True, autoescape=False)
    text = text.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ')
    
    # Handle lists (lines starting with - or *)
    lines = text.split('\n')
    in_list = False
    formatted_lines = []
    list_items = []
    
    for line in lines:
        if line.strip().startswith(('- ', '* ', '• ')):
            if not in_list:
                in_list = True
                list_items = []
            list_items.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                formatted_lines.append(f'<ul>{"".join(list_items)}</ul>')
                in_list = False
                list_items = []
            formatted_lines.append(line)
    
    # Close any open list
    if in_list:
        formatted_lines.append(f'<ul>{"".join(list_items)}</ul>')
    
    text = '\n'.join(formatted_lines)
    
    # Handle paragraphs
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        if paragraph.strip() and not paragraph.strip().startswith('<ul>'):
            paragraph = paragraph.replace('\n', '<br>')
            formatted_paragraphs.append(f'<p>{paragraph}</p>')
        elif paragraph.strip():
            formatted_paragraphs.append(paragraph)
    
    result = ''.join(formatted_paragraphs)
    
    return mark_safe(result)

@register.filter(name='truncate_formatted')
def truncate_formatted(text, length=200):
    """
    Truncate text while preserving some formatting
    """
    if not text:
        return ''
    
    # Remove HTML tags for counting
    plain_text = re.sub('<.*?>', '', text)
    
    if len(plain_text) <= length:
        return format_post_content(text)
    
    # Truncate plain text
    truncated = plain_text[:length].rsplit(' ', 1)[0] + '...'
    
    # Apply basic formatting to truncated text
    return format_post_content(truncated)