"""apps/users/urls.py"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/',            views.login_view,      name='login'),
    path('logout/',           views.logout_view,     name='logout'),
    path('register/',         views.register_client, name='register_client'),
    path('register/pandit/', views.register_pandit, name='register_pandit'),
    path('profile/', views.profile_view, name='profile'),
    
    path('pandit/dashboard/', views.pandit_dashboard, name='pandit_dashboard'),
    path('pandit/action/<uuid:booking_id>/', views.pandit_action_booking, name='pandit_action_booking'),
]
