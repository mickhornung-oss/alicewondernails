from django.contrib import admin
from .models import PaymentMethod, PaymentTransaction, PaymentMethodSnapshot


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "provider",
        "customer_group",
        "is_active",
        "sort_order",
    ]
    list_filter = ["provider", "customer_group", "is_active", "created_at"]
    search_fields = ["name", "code", "provider"]
    ordering = ["sort_order", "name"]
    
    fieldsets = (
        ("Grundinfo", {
            "fields": ("name", "code", "provider", "customer_group", "description")
        }),
        ("Status", {
            "fields": ("is_active", "sort_order")
        }),
        ("Zeitstempel", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "method",
        "status",
        "amount",
        "currency",
        "customer_group",
        "provider",
        "created_at",
    ]
    list_filter = [
        "status",
        "provider",
        "customer_group",
        "currency",
        "created_at",
    ]
    search_fields = [
        "payment_reference",
        "provider_reference",
        "order__order_number",
        "method__name",
        "method__code",
    ]
    raw_id_fields = ("order", "method")
    ordering = ["-created_at"]
    
    fieldsets = (
        ("Grundinfo", {
            "fields": ("order", "method", "status")
        }),
        ("Betrag und Währung", {
            "fields": ("amount", "currency", "customer_group")
        }),
        ("Provider", {
            "fields": ("provider", "payment_reference", "provider_reference")
        }),
        ("Daten", {
            "fields": ("raw_response", "metadata")
        }),
        ("Zeitstempel", {
            "fields": (
                "created_at",
                "updated_at",
                "paid_at",
                "cancelled_at",
                "refunded_at"
            ),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = (
        "raw_response",
        "metadata",
        "created_at",
        "updated_at",
        "paid_at",
        "cancelled_at",
        "refunded_at",
    )


@admin.register(PaymentMethodSnapshot)
class PaymentMethodSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "method_name",
        "method_code",
        "provider",
        "customer_group",
        "created_at",
    ]
    list_filter = ["provider", "customer_group", "created_at"]
    search_fields = ["method_name", "method_code", "provider"]
    ordering = ["-created_at"]
    
    fieldsets = (
        ("Snapshot-Daten", {
            "fields": (
                "method",
                "method_code",
                "method_name",
                "provider",
                "customer_group"
            )
        }),
        ("Zeitstempel", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = (
        "method",
        "method_code",
        "method_name",
        "provider",
        "customer_group",
        "created_at",
    )
