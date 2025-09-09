from rest_framework import permissions

class IsAssignedBusinessOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an order object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.offer_detail.offer.user == request.user
        is_admin = request.user.is_staff or request.user.is_superuser
        return is_owner or is_admin
    
class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.type == "customer"