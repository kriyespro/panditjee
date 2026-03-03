"""apps/core/models.py — City & PujaCategory"""
from django.db import models
from django.utils.text import slugify


class City(models.Model):
    name      = models.CharField(max_length=100)
    slug      = models.SlugField(unique=True, blank=True)
    state     = models.CharField(max_length=100, default='Gujarat')
    is_active = models.BooleanField(default=True)
    image     = models.ImageField(upload_to='cities/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.state}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PujaCategory(models.Model):
    name        = models.CharField(max_length=150)
    slug        = models.SlugField(unique=True, blank=True)
    icon        = models.CharField(max_length=10, default='🕉️', help_text='Emoji icon')
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    sort_order  = models.PositiveIntegerField(default=0)
    image       = models.ImageField(upload_to='puja_categories/', null=True, blank=True)

    class Meta:
        verbose_name = 'Puja Category'
        verbose_name_plural = 'Puja Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
