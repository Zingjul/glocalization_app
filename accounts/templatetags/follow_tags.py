# accounts/templatetags/follow_tags.py

from django import template
from django.contrib.auth import get_user_model

register = template.Library()

User = get_user_model()


@register.inclusion_tag('accounts/follow_button.html', takes_context=True)
def follow_button(context, target_user, show_count=False, size='medium', variant='primary'):
    """
    Render a follow button for a user.
    
    Usage in templates:
        {% load follow_tags %}
        {% follow_button some_user %}
        {% follow_button post.author size="small" show_count=True %}
    """
    # Import here to avoid circular imports
    from accounts.models import Follow
    
    request = context.get('request')
    is_following_user = False
    is_self = False
    is_authenticated = False
    follower_count = 0
    target_user_id = None
    target_username = ''
    
    # Get target user info safely
    if target_user:
        if hasattr(target_user, 'id') and target_user.id:
            target_user_id = target_user.id
        if hasattr(target_user, 'username'):
            target_username = target_user.username
        if hasattr(target_user, 'follower_count'):
            follower_count = target_user.follower_count or 0
    
    # Check authentication and follow status
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        is_authenticated = True
        
        if target_user_id:
            # Same user check
            if request.user.id == target_user_id:
                is_self = True
            else:
                # Check if following
                try:
                    is_following_user = Follow.objects.filter(
                        follower_id=request.user.id,
                        following_id=target_user_id
                    ).exists()
                except Exception:
                    is_following_user = False
    
    return {
        'request': request,
        'target_user': target_user,
        'target_user_id': target_user_id,
        'target_username': target_username,
        'is_following': is_following_user,
        'is_self': is_self,
        'is_authenticated': is_authenticated,
        'show_count': show_count,
        'size': size,
        'variant': variant,
        'follower_count': follower_count,
    }