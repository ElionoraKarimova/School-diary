from django.conf import settings
from django.db import models
from django.utils.text import slugify
import datetime


def russian_to_slug(text):
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    res = []
    for char in text.lower():
        if char in translit:
            res.append(translit[char])
        elif char.isalnum():
            res.append(char)
        else:
            res.append('-')
    return slugify("".join(res))


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
    value = models.PositiveSmallIntegerField(verbose_name="Grade")
    date = models.DateField(default=datetime.date.today, verbose_name="Дата выставления")
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.username} - {self.subject.name}: {self.value}"


class Schedule(models.Model):
    WEEKDAYS = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Tuesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
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
    slug = models.SlugField(max_length=150, unique=True, blank=True, default='', verbose_name="URL-слаг")
    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
        unique_together = ('group', 'weekday', 'lesson_number')

    def save(self, *args, **kwargs):
        if not self.slug:
            raw_text = f"{self.group.name}-{self.subject.name}"
            base_slug = russian_to_slug(raw_text)

            slug = base_slug
            count = 1
            while Schedule.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

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