"""apps/core/views.py — Public-facing pages"""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import City, PujaCategory
from apps.users.models import PanditProfile


def home(request):
    cities = City.objects.filter(is_active=True)
    categories = PujaCategory.objects.filter(is_active=True)[:8]
    featured_pandits = PanditProfile.objects.filter(status=PanditProfile.Status.APPROVED).select_related('user', 'city').order_by('-average_rating')[:6]
    context = {
        'cities': cities,
        'categories': categories,
        'featured_pandits': featured_pandits,
        'page_title': 'Book Verified Pandits Online — SD Online Pandit Jee',
        'meta_description': 'Book verified and experienced pandits in Gujarat for all puja ceremonies. Serving Surat, Ahmedabad, Vadodara and more cities.',
    }
    return render(request, 'core/home.jinja', context)


def pandit_list(request):
    city_slug = request.GET.get('city', '')
    puja_slug = request.GET.get('puja', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    language  = request.GET.get('language', '')

    pandits = PanditProfile.objects.filter(
        status=PanditProfile.Status.APPROVED
    ).select_related('user', 'city').order_by('-average_rating', '-total_bookings')

    selected_city = None
    selected_puja = None

    if city_slug:
        selected_city = get_object_or_404(City, slug=city_slug, is_active=True)
        pandits = pandits.filter(city=selected_city)

    if puja_slug:
        selected_puja = get_object_or_404(PujaCategory, slug=puja_slug, is_active=True)
        pandits = pandits.filter(specializations=selected_puja)

    if min_price:
        try:
            pandits = pandits.filter(base_price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            pandits = pandits.filter(base_price__lte=float(max_price))
        except ValueError:
            pass

    if language:
        pandits = pandits.filter(languages__icontains=language)

    cities     = City.objects.filter(is_active=True)
    categories = PujaCategory.objects.filter(is_active=True)

    paginator   = Paginator(pandits, 12)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)

    context = {
        'pandits': page_obj,
        'page_obj': page_obj,
        'cities': cities,
        'categories': categories,
        'selected_city': selected_city,
        'selected_puja': selected_puja,
        'min_price': min_price,
        'max_price': max_price,
        'language': language,
        'page_title': 'Find Pandits — SD Online Pandit Jee',
    }
    return render(request, 'core/pandit_list.jinja', context)


def pandit_detail(request, slug):
    pandit  = get_object_or_404(PanditProfile, slug=slug, status='APPROVED')
    reviews = pandit.reviews.select_related('client').order_by('-created_at')[:10]
    can_review = False
    if request.user.is_authenticated and request.user.role == 'CLIENT':
        from apps.bookings.models import Booking
        can_review = Booking.objects.filter(
            client=request.user, pandit=pandit, status=Booking.Status.COMPLETED,
        ).exclude(review__isnull=False).exists()
    context = {
        'pandit': pandit,
        'reviews': reviews,
        'can_review': can_review,
        'page_title': f"Pt. {pandit.user.get_full_name()} — {pandit.city}",
        'meta_description': f"Book {pandit.user.get_full_name()}, experienced pandit in {pandit.city} for all puja ceremonies.",
    }
    return render(request, 'core/pandit_detail.jinja', context)


# ── Static Pages ──────────────────────────────────────────────────────────────

def about_view(request):
    return render(request, 'core/about.jinja', {
        'page_title': 'About Us — SD Online Pandit Jee',
        'meta_description': 'Learn about SD Online Pandit Jee — connecting clients with verified pandits across Gujarat.',
    })


def contact_view(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '')
        email   = request.POST.get('email', '')
        message = request.POST.get('message', '')
        try:
            send_mail(
                f'Contact Form: {name}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(request, 'Thank you! We will get back to you within 24 hours. 🙏')
        return redirect('core:contact')
    return render(request, 'core/contact.jinja', {
        'page_title': 'Contact Us — SD Online Pandit Jee',
    })


def terms_view(request):
    return render(request, 'core/terms.jinja', {
        'page_title': 'Terms & Conditions — SD Online Pandit Jee',
    })


def privacy_view(request):
    return render(request, 'core/privacy.jinja', {
        'page_title': 'Privacy Policy — SD Online Pandit Jee',
    })


def faq_view(request):
    return render(request, 'core/faq.jinja', {
        'page_title': 'FAQ — SD Online Pandit Jee',
    })


def custom_404_view(request, exception=None):
    return render(request, 'errors/404.jinja', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.jinja', status=500)
