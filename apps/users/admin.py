"""apps/users/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PanditProfile, ClientProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'phone', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'phone', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'profile_image')}),
    )


@admin.register(PanditProfile)
class PanditProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'status', 'average_rating', 'base_price', 'total_bookings']
    list_filter = ['status', 'city']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['average_rating', 'total_bookings', 'slug']
    actions = ['approve_pandits', 'reject_pandits', 'suspend_pandits']

    @admin.action(description='✅ Approve selected pandits')
    def approve_pandits(self, request, queryset):
        queryset.update(status=PanditProfile.Status.APPROVED)

    @admin.action(description='❌ Reject selected pandits')
    def reject_pandits(self, request, queryset):
        queryset.update(status=PanditProfile.Status.REJECTED)

    @admin.action(description='🚫 Suspend selected pandits')
    def suspend_pandits(self, request, queryset):
        queryset.update(status=PanditProfile.Status.SUSPENDED)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__email']
