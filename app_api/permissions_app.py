# utf-8
from rest_framework.permissions import BasePermission, SAFE_METHODS


class AppPermission(BasePermission):
    message = '只有VIP才能访问'

    def has_permission(self, request, view):
        if not request.auth:
            return False
        if request.user.vip:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
