from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    """Only allows the post's author to modify it."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
