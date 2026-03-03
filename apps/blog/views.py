"""apps/blog/views.py"""
from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'blog/blog_list.jinja', {'posts': posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    recent = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:4]
    return render(request, 'blog/blog_detail.jinja', {'post': post, 'recent': recent})
