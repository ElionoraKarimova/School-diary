from rest_framework import serializers
from .models import Schedule, Grade, Homework, Subject, Group


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "year"]


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="student.get_full_name")
    subject_name = serializers.ReadOnlyField(source="subject.name")
    teacher = serializers.ReadOnlyField(source="teacher.id")
    teacher_name = serializers.ReadOnlyField(source="teacher.get_full_name")

    class Meta:
        model = Grade
        fields = [
            "id",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "teacher",
            "teacher_name",
            "value",
            "date",
            "comment",
        ]
    def validate_value(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Балл должен быть от 1 до 10.")
        return value

class HomeworkSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source="schedule.subject.name")

    class Meta:
        model = Homework
        fields = ["id", "schedule", "subject_name", "date", "task", "created_at"]


class ScheduleSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source="group.name")
    subject_name = serializers.ReadOnlyField(source="subject.name")
    teacher_name = serializers.ReadOnlyField(source="teacher.get_full_name")

    class Meta:
        model = Schedule
        fields = [
            "id",
            "group",
            "group_name",
            "subject",
            "subject_name",
            "teacher",
            "teacher_name",
            "weekday",
            "lesson_number",
            "classroom",
            "slug",
        ]
