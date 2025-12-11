# person/templatetags/profile_tags.py
from django import template
from django.utils.html import format_html
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.simple_tag
def profile_picture(user, size=48, css_class="feed-card-avatar"):
    """
    Display user profile picture with fallback
    Usage: {% profile_picture post.author %}
    """
    if not user:
        logger.debug("No user provided to profile_picture tag")
        return ""
    
    # Try to get the profile
    profile = getattr(user, 'profile', None)
    
    if profile:
        # FIRST: Check the direct ImageField (person_profile_picture)
        if profile.person_profile_picture:
            logger.debug(f"Found person_profile_picture for user {user.username}")
            return format_html(
                '<img src="{}" alt="{}" class="{}" width="{}" height="{}" loading="lazy">',
                profile.person_profile_picture.url,
                profile.business_name or user.username,
                css_class,
                size,
                size
            )
        
        # SECOND: Check media_files through GenericRelation
        try:
            profile_pic = profile.media_files.filter(file_type='image').first()
            if profile_pic:
                logger.debug(f"Found media_file profile picture for user {user.username}")
                return format_html(
                    '<img src="{}" alt="{}" class="{}" width="{}" height="{}" loading="lazy">',
                    profile_pic.file.url,
                    profile.business_name or user.username,
                    css_class,
                    size,
                    size
                )
        except Exception as e:
            logger.error(f"Error accessing media_files for user {user.username}: {e}")
    
    # FALLBACK: Use UI Avatars service
    username = user.username if user else "User"
    bg_color = "667eea"  # You can make this dynamic based on user ID
    
    avatar_url = f"https://ui-avatars.com/api/?name={username}&background={bg_color}&color=fff&size={size}"
    
    logger.debug(f"Using fallback avatar for user {username}")
    
    return format_html(
        '<img src="{}" alt="{}" class="{}" width="{}" height="{}" loading="lazy">',
        avatar_url,
        username,
        css_class,
        size,
        size
    )

@register.simple_tag
def debug_profile(user):
    """Debug tag to check what's available for a user's profile"""
    if not user:
        return "No user"
    
    profile = getattr(user, 'profile', None)
    if not profile:
        return f"User {user.username} has no profile"
    
    debug_info = []
    debug_info.append(f"User: {user.username}")
    debug_info.append(f"Profile exists: Yes")
    debug_info.append(f"person_profile_picture: {bool(profile.person_profile_picture)}")
    
    try:
        media_count = profile.media_files.filter(file_type='image').count()
        debug_info.append(f"Media files (images): {media_count}")
    except:
        debug_info.append("Media files: Error accessing")
    
    return " | ".join(debug_info)