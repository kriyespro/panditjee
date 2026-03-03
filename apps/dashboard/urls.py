from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard_home, name='home'),
    path('pandits/', views.admin_pandits_list, name='pandits'),
    path('bookings/', views.admin_bookings_list, name='bookings'),
    path('action/pandit/<int:user_id>/', views.admin_action_pandit, name='action_pandit'),
]
