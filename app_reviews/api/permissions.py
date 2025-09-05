from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an review object to edit it.
    Assumes the model instance has an `reviewer` attribute.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.reviewer == request.user
        is_admin = request.user.is_staff or request.user.is_superuser
        return is_owner or is_admin