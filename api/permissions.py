from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.account_type == 'employer')


class IsEmployee(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.account_type == 'employee')
