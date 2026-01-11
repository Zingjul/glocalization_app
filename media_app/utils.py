# media_app/utils.py
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


def get_video_duration(uploaded_file):
    """
    Get video duration in seconds from an uploaded file.
    Returns None if unable to determine duration.
    """
    try:
        from moviepy.editor import VideoFileClip
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Get duration
        try:
            clip = VideoFileClip(tmp_file_path)
            duration = clip.duration
            clip.close()
            return duration
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            # Reset file pointer for later use
            uploaded_file.seek(0)
                
    except ImportError:
        logger.warning("moviepy not installed. Video duration validation skipped.")
        return None
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return None


def validate_video_duration(uploaded_file, max_duration_seconds=90):
    """
    Validate that video duration doesn't exceed max_duration_seconds.
    Returns tuple: (is_valid, duration, error_message)
    
    Args:
        uploaded_file: Django UploadedFile object
        max_duration_seconds: Maximum allowed duration (default: 90 = 1:30)
    
    Returns:
        (is_valid: bool, duration: float or None, error_message: str or None)
    """
    duration = get_video_duration(uploaded_file)
    
    if duration is None:
        # Couldn't determine duration - allow upload but log warning
        logger.warning("Could not determine video duration, allowing upload")
        return True, None, None
    
    if duration > max_duration_seconds:
        minutes = int(max_duration_seconds // 60)
        seconds = int(max_duration_seconds % 60)
        actual_min = int(duration // 60)
        actual_sec = int(duration % 60)
        error_msg = f"Video is {actual_min}:{actual_sec:02d} but max allowed is {minutes}:{seconds:02d}"
        return False, duration, error_msg
    
    return True, duration, None


def format_duration(seconds):
    """Format seconds as M:SS string."""
    if seconds is None:
        return "Unknown"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"