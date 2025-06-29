from rest_framework.permissions import BasePermission, SAFE_METHODS
from .enums import Roles

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.SUPERADMIN

class IsBusinessman(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.BUSINESSMAN


class IsSuperAdminOrReadOnlyBusinessman(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role == Roles.SUPERADMIN:
            return True
        
        if request.method in SAFE_METHODS and request.user.role == Roles.BUSINESSMAN:
            return True
        
        return False
