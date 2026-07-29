import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
from gradebook.models import Grade, Subject

@pytest.mark.django_db
class TestGradeAPI:

    def test_unauthenticated_user_cannot_access_grades(self):
        client = APIClient()
        response = client.get("/api/v1/grades/")
        assert response.status_code == 403

    def test_authenticated_teacher_can_access_grades(self):
        teacher = User.objects.create_user(
            username="teacher1",
            password="testpass123",
            role=User.Role.TEACHER
        )
        client = APIClient()
        client.force_authenticate(user=teacher)
        response = client.get("/api/v1/grades/")
        assert response.status_code == 200

    def test_student_sees_only_own_grades(self):
        subject = Subject.objects.create(name="Математика")

        student1 = User.objects.create_user(
            username="student1", password="testpass123", role=User.Role.STUDENT
        )
        student2 = User.objects.create_user(
            username="student2", password="testpass123", role=User.Role.STUDENT
        )

        Grade.objects.create(student=student1, subject=subject, value=5)
        Grade.objects.create(student=student2, subject=subject, value=3)

        client = APIClient()
        client.force_authenticate(user=student1)
        response = client.get("/api/v1/grades/")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["student"] == student1.id