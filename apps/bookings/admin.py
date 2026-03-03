from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'client', 'pandit', 'puja_category', 'puja_date', 'status', 'payment_mode', 'amount')
    list_filter = ('status', 'payment_mode', 'puja_date')
    search_fields = ('booking_id', 'client__email', 'client__first_name', 'pandit__user__email', 'pandit__user__first_name')
    readonly_fields = ('booking_id', 'created_at', 'updated_at')
