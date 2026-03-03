"""apps/payments/urls.py"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<uuid:booking_id>/',      views.razorpay_checkout, name='checkout'),
    path('callback/',                   views.razorpay_callback, name='callback'),
    path('payout/request/',             views.request_payout,    name='request_payout'),
    path('payout/history/',             views.payout_history,    name='payout_history'),
    path('availability/',               views.availability_calendar, name='availability'),
    path('invoice/<uuid:booking_id>/',  views.invoice_view,      name='invoice'),
]
