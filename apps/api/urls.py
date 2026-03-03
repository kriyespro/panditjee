"""apps/api/urls.py"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Auth
    path('auth/register/', views.api_register,   name='register'),
    path('auth/login/',    views.api_login,       name='login'),
    path('auth/refresh/',  TokenRefreshView.as_view(), name='token_refresh'),

    # Pandits
    path('pandits/',        views.api_pandit_list,   name='pandit_list'),
    path('pandits/<int:pandit_id>/', views.api_pandit_detail, name='pandit_detail'),

    # Bookings
    path('bookings/my/',    views.api_my_bookings,   name='my_bookings'),

    # Reviews
    path('reviews/create/', views.api_create_review, name='create_review'),
]
