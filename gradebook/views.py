from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Schedule, Grade, Homework
from users.models import User
import datetime


@login_required
def home_view(request):
    user = request.user
    context = {
        'user': user,
    }

    if user.role == 'STUDENT':
        context['message'] = f"Добро пожаловать в дневник, ученик {user.get_full_name() or user.username}!"
        if user.group:
            context['group_info'] = f"Твой класс: {user.group.name}"

            schedule = Schedule.objects.filter(group=user.group).select_related('subject', 'teacher').order_by(
                'weekday', 'lesson_number')
            context['schedule'] = schedule


            homeworks = Homework.objects.filter(schedule__group=user.group,
                                                date__gte=datetime.date.today()).select_related(
                'schedule__subject').order_by('date')
            context['homeworks'] = homeworks

        grades = Grade.objects.filter(student=user).select_related('subject', 'teacher').order_by('-date')
        context['grades'] = grades

    elif user.role == 'TEACHER':
        context['message'] = f"Здравствуйте, уважаемый учитель {user.get_full_name() or user.username}!"

        teacher_lessons = Schedule.objects.filter(teacher=user).select_related('group', 'subject').distinct('group',
                                                                                                            'subject')
        context['teacher_lessons'] = teacher_lessons

        selected_group_id = request.GET.get('group')
        selected_subject_id = request.GET.get('subject')

        if selected_group_id and selected_subject_id:
            lesson = Schedule.objects.filter(teacher=user, group_id=selected_group_id,
                                             subject_id=selected_subject_id).first()
            if lesson:
                context['selected_lesson'] = lesson
                context['students'] = User.objects.filter(group_id=selected_group_id, role='STUDENT')

        if request.method == 'POST':
            if 'sub_grade' in request.POST:
                student_id = request.POST.get('student_id')
                subject_id = request.POST.get('subject_id')
                grade_value = request.POST.get('grade_value')
                comment = request.POST.get('comment', '')

                if student_id and subject_id and grade_value:
                    Grade.objects.create(
                        student_id=student_id,
                        subject_id=subject_id,
                        teacher=user,
                        value=int(grade_value),
                        comment=comment,
                        date=datetime.date.today()
                    )
                    return redirect(f"/?group={selected_group_id}&subject={selected_subject_id}")

            elif 'sub_homework' in request.POST:
                task_text = request.POST.get('task')
                due_date_str = request.POST.get('due_date')


                if selected_group_id and selected_subject_id and task_text and due_date_str:
                    lesson = Schedule.objects.filter(teacher=user, group_id=selected_group_id,
                                                     subject_id=selected_subject_id).first()
                    if lesson:
                        Homework.objects.create(
                            schedule=lesson,
                            task=task_text,
                            date=due_date_str
                        )
                    return redirect(f"/?group={selected_group_id}&subject={selected_subject_id}")

    else:
        context['message'] = f"Добро пожаловать в панель управления, {user.username}!"

    return render(request, 'gradebook/home.html', context)