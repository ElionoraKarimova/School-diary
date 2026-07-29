import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_create_user_with_role(self):
        user = User.objects.create_user(
            username="test_teacher", password="testpass123", role=User.Role.TEACHER
        )
        assert user.username == "test_teacher"
        assert user.role == User.Role.TEACHER

    def test_password_is_hashed(self):
        user = User.objects.create_user(username="u1", password="testpass123")
        assert user.password != "testpass123"
        assert user.check_password("testpass123")

    def test_default_role_is_student(self):
        user = User.objects.create_user(username="u2", password="testpass123")
        assert user.role == User.Role.STUDENT
