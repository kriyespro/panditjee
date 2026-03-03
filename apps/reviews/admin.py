from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'rating', 'booking', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('client__email', 'pandit__user__email', 'review_text')
