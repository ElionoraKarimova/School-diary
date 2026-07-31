import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from gradebook.models import Grade, Subject

User = get_user_model()


@pytest.mark.django_db
class TestGradeAPI:

    def test_unauthenticated_user_cannot_access_grades(self):
        client = APIClient()
        response = client.get("/api/v1/grades/")
        assert response.status_code == 403

    def test_authenticated_teacher_can_access_grades(self):
        teacher = User.objects.create_user(
            username="teacher1", password="testpass123", role=User.Role.TEACHER
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
        assert response.data["count"] == 1
        assert response.data["results"][0]["student"] == student1.id

    def test_student_cannot_create_grade(self):
        subject = Subject.objects.create(name="Физика")
        student = User.objects.create_user(
            username="student3", password="testpass123", role=User.Role.STUDENT
        )

        client = APIClient()
        client.force_authenticate(user=student)

        response = client.post(
            "/api/v1/grades/",
            {
                "student": student.id,
                "subject": subject.id,
                "value": 9,
                "date": "2026-07-29",
            },
        )

        assert response.status_code == 403
        assert Grade.objects.count() == 0

    def test_teacher_cannot_edit_another_teachers_grade(self):
        subject = Subject.objects.create(name="Chemistry")
        student = User.objects.create_user(
            username="student4", password="testpass123", role=User.Role.STUDENT
        )
        teacher_a = User.objects.create_user(
            username="teacher_a", password="testpass123", role=User.Role.TEACHER
        )
        teacher_b = User.objects.create_user(
            username="teacher_b", password="testpass123", role=User.Role.TEACHER
        )

        grade = Grade.objects.create(
            student=student, subject=subject, teacher=teacher_a, value=8
        )

        client = APIClient()
        client.force_authenticate(user=teacher_b)

        response = client.patch(f"/api/v1/grades/{grade.id}/", {"value": 2})

        assert response.status_code == 403
        grade.refresh_from_db()
        assert grade.value == 8
