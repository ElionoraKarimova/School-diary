from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from .models import Schedule, Grade, Homework
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

        grades = Grade.objects.filter(student=user).select_related('subject', 'teacher').order_by('-date')
        context['grades'] = grades


    elif user.role == 'TEACHER':
        context['message'] = f"Здравствуйте, уважаемый учитель {user.get_full_name() or user.username}!"
    else:
        context['message'] = f"Добро пожаловать в панель управления, {user.username}!"

    return render(request, 'gradebook/home.html', context)
