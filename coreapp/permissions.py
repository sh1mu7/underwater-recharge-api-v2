from rest_framework.permissions import BasePermission
from .roles import UserRoles


class IsUser(BasePermission):
    """
    Allows access only Customer
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRoles.USER)
