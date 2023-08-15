from rest_framework import permissions

class isAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.account.portfolio.user == request.user