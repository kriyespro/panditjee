"""apps/core/urls.py"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('pandits/', views.pandit_list, name='pandit_list'),
    path('pandits/<slug:slug>/', views.pandit_detail, name='pandit_detail'),
]
