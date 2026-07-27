from rest_framework import viewsets, permissions
from .models import Schedule, Grade, Homework
from .serializers import ScheduleSerializer, GradeSerializer, HomeworkSerializer


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all().select_related('group', 'subject', 'teacher')
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all().select_related('student', 'subject')
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return Grade.objects.filter(student=user)
        return Grade.objects.all()


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all().select_related('schedule__subject')
    serializer_class = HomeworkSerializer
    permission_classes = [permissions.IsAuthenticated]