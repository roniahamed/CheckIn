from rest_framework.permissions import BasePermission

class IsFormManager(BasePermission):
    message = "Access Denied: You must have the 'form' role to access this resource."
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'form' or (hasattr(request.user, 'is_superuser') and request.user.is_superuser)

class IsDoctor(BasePermission):
    message = "Access Denied: You must have the 'doctor' role to access this resource."
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'doctor' or (hasattr(request.user, 'is_superuser') and request.user.is_superuser)

class IsQueueManager(BasePermission):
    message = "Access Denied: You must have the 'queue' role to access this resource."
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'queue' or (hasattr(request.user, 'is_superuser') and request.user.is_superuser)
