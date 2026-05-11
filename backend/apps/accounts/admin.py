from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountsUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'customer_status',
        'is_staff',
        'is_active',
    )
    list_filter = ('customer_status', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Customer status', {'fields': ('customer_status',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Customer status', {'fields': ('email', 'customer_status')}),
    )
