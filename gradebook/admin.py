from django.contrib import admin

# Register your models here.
from .models import Group, Grade, Subject


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