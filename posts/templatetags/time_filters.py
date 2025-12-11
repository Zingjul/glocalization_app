import datetime
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def short_time(value):
    """
    Returns a short, compressed humanized string for the duration.
    Example: 10 seconds ago -> 10s, 2 hours ago -> 2h, 3 days ago -> 3d.
    """
    if not value:
        return ""

    # Ensure we are comparing timezone-aware datetime objects
    if timezone.is_aware(value):
        now = timezone.now()
    else:
        now = datetime.datetime.now()
        
    # Handle future dates gracefully, though typically posts are in the past
    if value > now:
        return "Now"
        
    delta = now - value

    # Define the compressed time units (s, m, h, d, w, y)
    
    # Years
    years = delta.days // 365
    if years >= 1:
        return f"{years}y"
        
    # Weeks
    weeks = delta.days // 7
    if weeks >= 1:
        return f"{weeks}w"
        
    # Days
    days = delta.days
    if days >= 1:
        return f"{days}d"

    # Hours
    hours = delta.seconds // 3600
    if hours >= 1:
        return f"{hours}h"

    # Minutes
    minutes = delta.seconds // 60
    if minutes >= 1:
        return f"{minutes}m"

    # Seconds
    seconds = delta.seconds
    if seconds >= 1:
        return f"{seconds}s"

    # Default for times less than 1 second
    return "1s"