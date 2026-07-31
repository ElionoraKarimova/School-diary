from rest_framework import permissions


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == "TEACHER"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        teacher = getattr(obj, "teacher", None)
        if teacher is None:
            teacher = getattr(obj.schedule, "teacher", None)

        return teacher == request.user