from rest_framework import permissions

class IsSuperUserOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow superusers or staff members to access the create functionality.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
        return True
