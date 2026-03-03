"""apps/core/admin.py"""
from django.contrib import admin
from .models import City, PujaCategory


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'state']
    search_fields = ['name']


@admin.register(PujaCategory)
class PujaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'sort_order']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['sort_order']
