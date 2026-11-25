from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsFactoryAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_factory_admin
        )


class IsWholesaler(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.WHOLESALER
        )


class IsWholesalerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_factory_admin
                or request.user.role == request.user.Role.WHOLESALER
            )
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.method in SAFE_METHODS or request.user.is_factory_admin)
        )
