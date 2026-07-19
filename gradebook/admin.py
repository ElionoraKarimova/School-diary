from django.contrib import admin

# Register your models here.
from .models import Group, Grade, Subject,Schedule, Homework


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'value', 'teacher', 'date')
    list_filter = ('subject', 'date','value' )
    search_fields = ('student__username', 'subject__name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'weekday', 'lesson_number', 'subject', 'teacher', 'classroom')
    list_filter = ('group', 'weekday', 'teacher')
    ordering = ('group', 'weekday', 'lesson_number')

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'date', 'created_at')
    list_filter = ('date', 'schedule__group')