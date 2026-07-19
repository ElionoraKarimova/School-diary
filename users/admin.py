from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'group')}),
    )
    list_display = ['username', 'email', 'role', 'group', 'is_staff']
