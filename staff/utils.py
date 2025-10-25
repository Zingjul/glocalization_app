from .models import AuditLog

def log_action(request, action, target=None, description=None):
    """Create a simple audit log entry."""
    target_type = target.__class__.__name__ if target else None
    target_id = getattr(target, "id", None)
    AuditLog.objects.create(
        staff=request.user if request.user.is_authenticated else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        description=description or "",
    )
