from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission pour les administrateurs"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'admin')


class IsRH(permissions.BasePermission):
    """Permission pour les RH"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['rh', 'admin'])


class IsManager(permissions.BasePermission):
    """Permission pour les managers"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['manager', 'rh', 'admin'])


class IsEmployee(permissions.BasePermission):
    """Permission pour les employés"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['employee', 'manager', 'rh', 'admin'])


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission : l'utilisateur ne peut voir que son propre profil ou l'admin voit tout"""
    
    def has_object_permission(self, request, view, obj):
        # L'admin peut voir tous les profils
        if request.user.role == 'admin':
            return True
        # Les autres ne peuvent voir que leur propre profil
        return obj.id == request.user.id
