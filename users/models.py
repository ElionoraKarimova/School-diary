from django.contrib.auth.models import AbstractUser
from django.db import models
from gradebook.models import Group


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Администратор"
        TEACHER = "TEACHER", "Учитель"
        STUDENT = "STUDENT", "Ученик"
        PARENT = "PARENT", "Родитель"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name="Роль"
    )


    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )


    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Класс"
    )


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

  
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"