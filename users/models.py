from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Администратор"
        TEACHER = "TEACHER", "Учитель"
        STUDENT = "STUDENT", "Ученик"
        PARENT = "PARENT", "Родитель"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=not Role.STUDENT,
        verbose_name="Роль"
    )
phone= models.CharField(
    max_length=20,
    blank=True,
    null=True,
    verbose_name="Телефон"
)

def __str__(self):
    return f"{self.username} ({self.get_role_display()})"