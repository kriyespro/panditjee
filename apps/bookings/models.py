from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REFUNDED = 'REFUNDED', _('Refunded')

    class PaymentMode(models.TextChoices):
        ONLINE = 'ONLINE', _('Online')
        COD = 'COD', _('Cash on Delivery')

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    pandit = models.ForeignKey('users.PanditProfile', on_delete=models.CASCADE, related_name='received_bookings')
    puja_category = models.ForeignKey('core.PujaCategory', on_delete=models.SET_NULL, null=True)
    
    puja_date = models.DateField()
    puja_time = models.TimeField()
    address = models.TextField()
    special_notes = models.TextField(blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount paid by client")
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pandit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount pandit receives after commission")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_mode = models.CharField(max_length=20, choices=PaymentMode.choices, default=PaymentMode.COD)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.client.email} to {self.pandit.user.email}"
