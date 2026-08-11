from django.db.models import Avg, Count
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Schedule, Grade, Homework
from .serializers import ScheduleSerializer, GradeSerializer, HomeworkSerializer
from .permissions import IsTeacherOrReadOnly
from .sql import student_average_via_plpgsql
from django_filters.rest_framework import DjangoFilterBackend


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

    def get_queryset(self):
        qs = Grade.objects.all().select_related("student", "subject", "teacher")
        user = self.request.user
        if getattr(user, "role", None) == "STUDENT":
            return qs.filter(student=user)
        return qs
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=False, methods=["get"], url_path="averages")
    def averages(self, request):
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
    def my_average(self, request):
        student_id = request.query_params.get("student_id") or request.user.id
        average = student_average_via_plpgsql(int(student_id))
        return Response({"student_id": int(student_id), "average": average})

class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all().select_related("schedule__subject")
    serializer_class = HomeworkSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["schedule", "date"]
