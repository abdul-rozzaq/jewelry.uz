from rest_framework.permissions import BasePermission


from apps.transactions.models import Transaction
from apps.users.models import User, UserRoles


class CanAcceptTransaction(BasePermission):

    def has_object_permission(self, request, view, obj: Transaction):

        user: User = request.user

        if user.is_staff or user.is_superuser or user.role == UserRoles.ADMIN:
            return True

        elif user.organization == obj.receiver:
            return True

        return False
