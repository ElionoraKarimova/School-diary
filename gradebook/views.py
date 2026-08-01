from .forms import GradeForm, HomeworkForm, ScheduleForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Schedule, Grade, Homework
from users.models import User
import datetime
from django.contrib import messages
import logging
from users.forms import AddStudentForm
logger = logging.getLogger("gradebook")

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
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
        }
        schedule_by_day = {day_name: [] for day_name in weekdays.values()}

        for item in schedule:
            day_name = weekdays.get(item.weekday, "Other day")
            schedule_by_day[day_name].append(item)

        context["schedule_by_day"] = schedule_by_day

    elif user.role == "STUDENT":
        if user.group:
            weekdays = {
                1: "MONDAY",
                2: "TUESDAY",
                3: "WEDNESDAY",
                4: "THURSDAY",
                5: "FRIDAY",
                6: "SATURDAY",
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
def admin_dashboard_view(request):
    user = request.user
    if user.role != "ADMIN":
        return redirect("home")

    if request.method == "POST":
        if "add_student" in request.POST:
            student_form = AddStudentForm(request.POST)
            if student_form.is_valid():
                User.objects.create_user(
                    username=student_form.cleaned_data["username"],
                    first_name=student_form.cleaned_data["first_name"],
                    last_name=student_form.cleaned_data["last_name"],
                    password=student_form.cleaned_data["password"],
                    role=User.Role.STUDENT,
                    group=student_form.cleaned_data["group"],
                )
                logger.info(
                    "Admin %s added new student: %s",
                    user.username,
                    student_form.cleaned_data["username"],
                )
                messages.success(request, "Student added successfully.")
                return redirect("admin_dashboard")
            schedule_form = ScheduleForm()

        elif "add_schedule" in request.POST:
            schedule_form = ScheduleForm(request.POST)
            if schedule_form.is_valid():
                schedule_form.save()
                logger.info(
                    "Admin %s added a new schedule entry: %s",
                    user.username,
                    schedule_form.cleaned_data,
                )
                messages.success(request, "Schedule entry added successfully.")
                return redirect("admin_dashboard")
            student_form = AddStudentForm()

        else:
            student_form = AddStudentForm()
            schedule_form = ScheduleForm()
    else:
        student_form = AddStudentForm()
        schedule_form = ScheduleForm()

    return render(
        request,
        "gradebook/admin_dashboard.html",
        {"user": user, "form": student_form, "schedule_form": schedule_form},
    )

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
                    logger.info(
                        "Teacher %s set grade %s for student %s (subject: %s, date: %s)",
                        user.username,
                        val,
                        student_id,
                        current_schedule.subject,
                        date_str,
                    )
                else:
                    Grade.objects.filter(
                        student_id=student_id,
                        subject=current_schedule.subject,
                        date=date_str,
                    ).delete()
                    logger.info(
                        "Teacher %s deleted grade for student %s (subject: %s, date: %s)",
                        user.username,
                        student_id,
                        current_schedule.subject,
                        date_str,
                    )
            else:
                logger.warning(
                    "Teacher %s submitted invalid grade data: %s",
                    user.username,
                    request.POST.get("value"),
                )
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
