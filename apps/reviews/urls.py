from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<uuid:booking_id>/', views.create_review, name='create'),
]
