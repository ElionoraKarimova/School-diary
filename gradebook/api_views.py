from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Schedule, Grade, Homework
from .serializers import ScheduleSerializer, GradeSerializer, HomeworkSerializer
from .permissions import IsTeacherOrReadOnly
from .sql import student_average_via_plpgsql
from .tasks import notify_grade_created
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from users.models import User


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all().select_related("group", "subject", "teacher")
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all().select_related("student", "subject")
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["subject", "student", "date"]

    def get_queryset(self) -> QuerySet[Grade]:
        qs = Grade.objects.all().select_related("student", "subject", "teacher")
        user = self.request.user
        if isinstance(user, User) and user.role == User.Role.STUDENT:
            return qs.filter(student=user)
        return qs

    def perform_create(self, serializer: BaseSerializer) -> None:
        grade = serializer.save(teacher=self.request.user)
        notify_grade_created.delay(grade.id)

    @action(detail=False, methods=["get"], url_path="averages")
    def averages(self, request: Request) -> Response:
        rows = (
            self.get_queryset()
            .values("subject_id", "subject__name")
            .annotate(average=Avg("value"), grades_count=Count("id"))
            .order_by("subject__name")
        )
        data = [
            {
                "subject_id": row["subject_id"],
                "subject_name": row["subject__name"],
                "average": round(row["average"], 2) if row["average"] else None,
                "grades_count": row["grades_count"],
            }
            for row in rows
        ]
        return Response(data)

    @action(detail=False, methods=["get"], url_path="my-average")
    def my_average(self, request: Request) -> Response:
        raw_id = request.query_params.get("student_id") or request.user.pk
        if raw_id is None:
            return Response(
                {"detail": "student_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        student_id = int(raw_id)
        average = student_average_via_plpgsql(student_id)
        return Response({"student_id": student_id, "average": average})

class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all().select_related("schedule__subject")
    serializer_class = HomeworkSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["schedule", "date"]
