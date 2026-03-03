"""apps/core/urls.py"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('pandits/', views.pandit_list, name='pandit_list'),
    path('pandits/<slug:slug>/', views.pandit_detail, name='pandit_detail'),
    # Static pages
    path('about/',   views.about_view,   name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/',   views.terms_view,   name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('faq/',     views.faq_view,     name='faq'),
]
