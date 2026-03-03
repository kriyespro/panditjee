"""apps/blog/models.py"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class BlogPost(models.Model):
    title        = models.CharField(max_length=250)
    slug         = models.SlugField(max_length=250, unique=True)
    excerpt      = models.TextField(max_length=500, blank=True)
    content      = models.TextField()
    image        = models.ImageField(upload_to='blog/', blank=True, null=True)
    author       = models.CharField(max_length=100, default='SD PanditJee Team')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
