from django.db import models
from django.conf import settings


class Group(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название класса")
    year= models.PositiveIntegerField(verbose_name="Учебный год")

    class Meta:
        verbose_name= "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return f"{self.name} ({self.year})"
class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название предмета")

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name

class Grade(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grades",
        limit_choices_to={'role': 'STUDENT'},
        verbose_name="Ученик"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Предмет"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="given_grades",
        limit_choices_to={'role': 'TEACHER'},
        verbose_name="Учитель"
    )
    value = models.PositiveSmallIntegerField(verbose_name="Оценка")
    date = models.DateField(auto_now_add=True, verbose_name="Дата выставления")
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

    def __str__(self):
        return f"{self.student.username} - {self.subject.name}: {self.value}"

