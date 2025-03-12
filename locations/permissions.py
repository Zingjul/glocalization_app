from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows admin users to create, update, and delete, and read-only for others.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff