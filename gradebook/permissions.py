import logging

from rest_framework import permissions

logger = logging.getLogger("gradebook")


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        allowed = request.user.is_authenticated and request.user.role == "TEACHER"
        if not allowed:
            logger.warning(
                "Permission denied: user %s (role: %s) attempted %s on %s",
                request.user,
                getattr(request.user, "role", "anonymous"),
                request.method,
                request.path,
            )
        return allowed

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        teacher = getattr(obj, "teacher", None)
        if teacher is None:
            teacher = getattr(obj.schedule, "teacher", None)

        allowed = teacher == request.user
        if not allowed:
            logger.warning(
                "Permission denied: teacher %s attempted %s on object %s owned by %s",
                request.user,
                request.method,
                obj.pk,
                teacher,
            )
        return allowed