from django.conf import settings
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название класса")
    year = models.PositiveIntegerField(verbose_name="Учебный год")

    class Meta:
        verbose_name = "Класс"
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


class Schedule(models.Model):
    WEEKDAYS = (
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='schedules', verbose_name="Класс")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")


    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'TEACHER'},
        related_name="teacher_schedules",
        verbose_name="Учитель"
    )

    weekday = models.IntegerField(choices=WEEKDAYS, verbose_name="День недели")
    lesson_number = models.PositiveIntegerField(verbose_name="Номер урока")
    classroom = models.CharField(max_length=10, blank=True, null=True, verbose_name="Кабинет")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
       
        unique_together = ('group', 'weekday', 'lesson_number')

    def __str__(self):
        return f"{self.get_weekday_display()} | Урок №{self.lesson_number} | {self.group} - {self.subject}"


class Homework(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='homeworks',
        verbose_name="Урок в расписании"
    )
    date = models.DateField(verbose_name="Дата, на которую задано")
    task = models.TextField(verbose_name="Задание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"

    def __str__(self):
        return f"ДЗ на {self.date} по {self.schedule.subject.name} для {self.schedule.group.name}"