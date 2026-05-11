from django.contrib import admin

from .models import Address, CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'display_name', 'phone')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'user',
        'address_type',
        'city',
        'country',
        'is_default',
    )
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = (
        'full_name',
        'company',
        'street',
        'postal_code',
        'city',
        'user__username',
        'user__email',
    )
