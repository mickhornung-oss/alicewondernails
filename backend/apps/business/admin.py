from django.contrib import admin

from .models import BusinessProfile


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'user',
        'status',
        'requested_at',
        'reviewed_at',
    )
    list_filter = ('status',)
    search_fields = ('company_name', 'user__email', 'user__username', 'vat_id')
