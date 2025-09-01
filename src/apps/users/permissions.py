from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    """
    Admin can do everything. Non-admins can retrieve/update their own user.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
