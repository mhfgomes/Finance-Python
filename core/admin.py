from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
