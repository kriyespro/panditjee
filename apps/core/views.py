"""apps/core/views.py — Public-facing pages"""
from django.shortcuts import render, get_object_or_404
from .models import City, PujaCategory
from apps.users.models import PanditProfile


def home(request):
    cities = City.objects.filter(is_active=True)
    categories = PujaCategory.objects.filter(is_active=True)[:8]
    context = {
        'cities': cities,
        'categories': categories,
        'page_title': 'Book Verified Pandits Online — SD Online Pandit Jee',
        'meta_description': 'Book verified and experienced pandits in Gujarat for all puja ceremonies. Serving Surat, Ahmedabad, Vadodara and more cities.',
    }
    return render(request, 'core/home.jinja', context)


def pandit_list(request):
    city_slug = request.GET.get('city', '')
    puja_slug = request.GET.get('puja', '')

    pandits = PanditProfile.objects.filter(status=PanditProfile.Status.APPROVED).select_related('user', 'city')

    selected_city = None
    selected_puja = None

    if city_slug:
        selected_city = get_object_or_404(City, slug=city_slug, is_active=True)
        pandits = pandits.filter(city=selected_city)

    if puja_slug:
        selected_puja = get_object_or_404(PujaCategory, slug=puja_slug, is_active=True)
        pandits = pandits.filter(specializations=selected_puja)

    cities = City.objects.filter(is_active=True)
    categories = PujaCategory.objects.filter(is_active=True)

    context = {
        'pandits': pandits,
        'cities': cities,
        'categories': categories,
        'selected_city': selected_city,
        'selected_puja': selected_puja,
        'page_title': 'Find Pandits — SD Online Pandit Jee',
    }
    return render(request, 'core/pandit_list.jinja', context)


def pandit_detail(request, slug):
    pandit = get_object_or_404(PanditProfile, slug=slug, status='APPROVED')
    context = {
        'pandit': pandit,
        'page_title': f"Pt. {pandit.user.get_full_name()} — {pandit.city}",
        'meta_description': f"Book {pandit.user.get_full_name()}, experienced pandit in {pandit.city} for all puja ceremonies.",
    }
    return render(request, 'core/pandit_detail.jinja', context)

def custom_404_view(request, exception=None):
    return render(request, 'errors/404.jinja', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.jinja', status=500)
