from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsActiveAndNotSuspended(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active and not request.user.is_suspended
