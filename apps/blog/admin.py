"""apps/blog/admin.py — Register blog models for /sd/ Django admin"""
from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display   = ('title', 'author', 'is_published', 'published_at')
    list_filter    = ('is_published',)
    search_fields  = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
