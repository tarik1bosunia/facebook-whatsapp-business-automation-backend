from rest_framework.permissions import BasePermission, SAFE_METHODS
from .enums import Roles

class IsAuthenticatedAndVerified(BasePermission):
    """
    Allows access only to authenticated users with verified email.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified
        )


class IsAuthenticatedAndVerifiedSuperAdmin(BasePermission):
    """
    Allows access only to authenticated SuperAdmin users with verified email.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified and
            request.user.role == Roles.SUPERADMIN
        )
    
class IsAuthenticatedAndVerifiedBusinessman(BasePermission):
    """
    Allows access only to authenticated Businessman users with verified email.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified and
            request.user.role == Roles.BUSINESSMAN
        )  


class IsSuperAdminOrReadOnlyBusinessmanVerified(BasePermission):
    """
    Allows access authenticated verified superadmin users with verified email and 
    authenticated verified Businessman for readonly
    """
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        
        if not request.user.is_email_verified:
            return False
        
        if request.user.role == Roles.SUPERADMIN:
            return True
        
        if request.method in SAFE_METHODS and request.user.role == Roles.BUSINESSMAN:
            return True
        return False

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == Roles.SUPERADMIN
        )

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
