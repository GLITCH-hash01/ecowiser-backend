from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.role =='Owner')

class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access an object.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.role == 'Admin')

class IsMember(BasePermission):
    """
    Custom permission to only allow members to access an object.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.role == 'Member')


class AdminOwnerPrivilages(BasePermission):
    """
    Custom permission to allow either Admin or Owner to access an object.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and obj.tenant == request.user.tenant and (request.user.role == 'Admin' or request.user.role == 'Owner'))

class IsAdminorOwner(BasePermission):
    """
    Custom permission to allow either Admin or Owner to access an object.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.role == 'Admin' or request.user.role == 'Owner'))
    
class ProjectBelongsToTenant(BasePermission):
    """
    Custom permission to check if a project belongs to the user's tenant.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user.tenant and obj.tenant == request.user.tenant)

class MediaBelongsToTenant(BasePermission):
    """
    Custom permission to check if a media resource belongs to the user's tenant.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user.tenant and obj.project.tenant == request.user.tenant)