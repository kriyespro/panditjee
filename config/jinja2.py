"""
config/jinja2.py — Jinja2 environment configuration
"""
from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def url(viewname, *args, **kwargs):
    """
    Jinja2-friendly wrapper around Django's reverse().
    Usage in templates:
        url('core:home')
        url('core:pandit_detail', slug=pandit.slug)
    """
    return reverse(viewname, args=args if args else None, kwargs=kwargs if kwargs else None)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': url,
        'messages': messages,
    })
    env.globals['get_messages'] = _get_messages
    return env


def _get_messages(request):
    return messages.get_messages(request)
