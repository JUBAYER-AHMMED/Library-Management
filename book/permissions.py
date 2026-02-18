from rest_framework.permissions import BasePermission

class IsLibrarian(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Librarian").exists()

class IsMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Member").exists()
    
    