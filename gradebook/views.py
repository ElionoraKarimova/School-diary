from .forms import GradeForm, HomeworkForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Schedule, Grade, Homework
from users.models import User
import datetime
from django.contrib import messages


@login_required
def home_view(request):

    user = request.user
    context = {"user": user}

    if user.role == "TEACHER":
        schedule = (
            Schedule.objects.filter(teacher=user)
            .select_related("group", "subject")
            .order_by("weekday", "lesson_number")
        )
        weekdays = {
            1: "Понедельник",
            2: "Вторник",
            3: "Среда",
            4: "Четверг",
            5: "Пятница",
            6: "Суббота",
        }
        schedule_by_day = {day_name: [] for day_name in weekdays.values()}

        for item in schedule:
            day_name = weekdays.get(item.weekday, "Другой день")
            schedule_by_day[day_name].append(item)

        context["schedule_by_day"] = schedule_by_day

    elif user.role == "STUDENT":
        if user.group:
            weekdays = {
                1: "ПОНЕДЕЛЬНИК",
                2: "ВТОРНИК",
                3: "СРЕДА",
                4: "ЧЕТВЕРГ",
                5: "ПЯТНИЦА",
                6: "СУББОТА",
            }

            today = datetime.date.today()
            monday = today - datetime.timedelta(days=today.weekday())

            schedules = (
                Schedule.objects.filter(group=user.group)
                .select_related("subject", "teacher")
                .order_by("weekday", "lesson_number")
            )

            grades = Grade.objects.filter(student=user).select_related("subject")
            grades_map = {g.subject_id: g.value for g in grades}

            homeworks = (
                Homework.objects.filter(schedule__group=user.group)
                .select_related("schedule")
                .order_by("-date")
            )
            hw_map = {}
            for hw in homeworks:
                if hw.schedule_id not in hw_map:
                    hw_map[hw.schedule_id] = hw.task

            diary_by_day = []
            for day_num, day_name in weekdays.items():

                day_date = monday + datetime.timedelta(days=day_num - 1)

                day_lessons = [s for s in schedules if s.weekday == day_num]
                lessons_data = []

                for lesson in day_lessons:
                    lessons_data.append(
                        {
                            "number": lesson.lesson_number,
                            "subject": lesson.subject.name,
                            "homework": hw_map.get(lesson.id, ""),
                            "grade": grades_map.get(lesson.subject_id, ""),
                        }
                    )

                if lessons_data:
                    diary_by_day.append(
                        {
                            "day_name": day_name,
                            "date": day_date.strftime("%d.%m.%Y"),
                            "lessons": lessons_data,
                        }
                    )

            context["diary_by_day"] = diary_by_day
    return render(request, "gradebook/home.html", context)


@login_required
def journal_view(request, slug):
    user = request.user
    if user.role != "TEACHER":
        return redirect("home")

    current_schedule = get_object_or_404(Schedule, slug=slug, teacher=user)

    if request.method == "POST":
        if "save_grade" in request.POST:
            form = GradeForm(request.POST)
            if form.is_valid():
                student_id = form.cleaned_data["student_id"]
                date_str = form.cleaned_data["date"]
                val = form.cleaned_data["value"]

                if val is not None:
                    Grade.objects.update_or_create(
                        student_id=student_id,
                        subject=current_schedule.subject,
                        date=date_str,
                        defaults={"value": val, "teacher": user},
                    )
                else:
                    Grade.objects.filter(
                        student_id=student_id,
                        subject=current_schedule.subject,
                        date=date_str,
                    ).delete()
            else:
                messages.error(request, "Grade must be a number between 0 and 10.")

        elif "save_homework" in request.POST:
            form = HomeworkForm(request.POST)
            if form.is_valid():
                date_str = form.cleaned_data["date"]
                task = form.cleaned_data["task"].strip()
                if task:
                    Homework.objects.update_or_create(
                        schedule=current_schedule,
                        date=date_str,
                        defaults={"task": task},
                    )
                else:
                    Homework.objects.filter(
                        schedule=current_schedule, date=date_str
                    ).delete()
            else:
                messages.error(request, "Invalid homework data.")
        return redirect("journal_detail", slug=slug)

    students = User.objects.filter(
        group=current_schedule.group, role="STUDENT"
    ).order_by("last_name", "first_name")
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    grades = Grade.objects.filter(
        subject=current_schedule.subject, student__group=current_schedule.group
    ).select_related("student")
    grade_map = {(g.student_id, g.date.strftime("%Y-%m-%d")): g for g in grades}

    homeworks = Homework.objects.filter(schedule=current_schedule)
    hw_map = {hw.date.strftime("%Y-%m-%d"): hw.task for hw in homeworks}

    context = {
        "user": user,
        "current_schedule": current_schedule,
        "students": students,
        "dates": dates,
        "grade_map": grade_map,
        "hw_map": hw_map,
    }
    return render(request, "gradebook/journal.html", context)
