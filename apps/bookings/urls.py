from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('checkout/<slug:pandit_slug>/', views.checkout_view, name='checkout'),
    path('success/<uuid:booking_id>/', views.booking_success_view, name='success'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('my-bookings/<uuid:booking_id>/cancel/', views.cancel_booking_view, name='cancel'),
]
