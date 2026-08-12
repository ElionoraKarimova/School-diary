import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from gradebook.models import Grade, Subject
from gradebook.sql import student_average_via_plpgsql

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

    def test_grade_created_via_api_records_owning_teacher(self):
        subject = Subject.objects.create(name="Biology")
        student = User.objects.create_user(
            username="student_own", password="testpass123", role=User.Role.STUDENT
        )
        teacher = User.objects.create_user(
            username="teacher_own", password="testpass123", role=User.Role.TEACHER
        )

        client = APIClient()
        client.force_authenticate(user=teacher)
        response = client.post(
            "/api/v1/grades/",
            {"student": student.id, "subject": subject.id, "value": 4},
        )

        assert response.status_code == 201
        grade = Grade.objects.get(id=response.data["id"])
        assert grade.teacher == teacher

    def test_teacher_can_edit_own_grade(self):
        subject = Subject.objects.create(name="History")
        student = User.objects.create_user(
            username="student_edit", password="testpass123", role=User.Role.STUDENT
        )
        teacher = User.objects.create_user(
            username="teacher_edit", password="testpass123", role=User.Role.TEACHER
        )

        client = APIClient()
        client.force_authenticate(user=teacher)
        created = client.post(
            "/api/v1/grades/",
            {"student": student.id, "subject": subject.id, "value": 4},
        )
        grade_id = created.data["id"]
        patched = client.patch(f"/api/v1/grades/{grade_id}/", {"value": 5})
        assert patched.status_code == 200
        assert Grade.objects.get(id=grade_id).value == 5

    def test_jwt_login_returns_tokens(self):

        User.objects.create_user(
            username="jwt_user", password="s3cret-pass", role=User.Role.TEACHER
        )
        client = APIClient()

        token_resp = client.post(
            "/api/v1/auth/token/",
            {"username": "jwt_user", "password": "s3cret-pass"},
        )
        assert token_resp.status_code == 200
        assert "access" in token_resp.data
        assert "refresh" in token_resp.data

        access = token_resp.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        grades_resp = client.get("/api/v1/grades/")
        assert grades_resp.status_code == 200

    def test_averages_endpoint_returns_correct_average(self):
        subject = Subject.objects.create(name="Maths")
        student = User.objects.create_user(
            username="student_avg", password="testpass123", role=User.Role.STUDENT
        )
        teacher = User.objects.create_user(
            username="teacher_avg", password="testpass123", role=User.Role.TEACHER
        )
        Grade.objects.create(student=student, subject=subject, teacher=teacher, value=4)
        Grade.objects.create(student=student, subject=subject, teacher=teacher, value=2)

        client = APIClient()
        client.force_authenticate(user=teacher)
        response = client.get("/api/v1/grades/averages/")

        assert response.status_code == 200
        maths = next(row for row in response.data if row["subject_name"] == "Maths")
        assert maths["average"] == 3.0  # (4 + 2) / 2
        assert maths["grades_count"] == 2

    def test_plpgsql_student_average(self):
        subject = Subject.objects.create(name="Geography")
        student = User.objects.create_user(
            username="student_pg", password="testpass123", role=User.Role.STUDENT
        )
        teacher = User.objects.create_user(
            username="teacher_pg", password="testpass123", role=User.Role.TEACHER
        )
        Grade.objects.create(student=student, subject=subject, teacher=teacher, value=5)
        Grade.objects.create(student=student, subject=subject, teacher=teacher, value=4)

        result = student_average_via_plpgsql(student.id)
        assert result == 4.5

        empty_student = User.objects.create_user(
            username="student_empty", password="testpass123", role=User.Role.STUDENT
        )
        assert student_average_via_plpgsql(empty_student.id) is None
