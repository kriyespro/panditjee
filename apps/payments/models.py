from django.db import models
from django.utils.translation import gettext_lazy as _


class Transaction(models.Model):
    """Razorpay payment transaction."""
    class Status(models.TextChoices):
        PENDING  = 'PENDING',  _('Pending')
        SUCCESS  = 'SUCCESS',  _('Success')
        FAILED   = 'FAILED',   _('Failed')
        REFUNDED = 'REFUNDED', _('Refunded')

    booking            = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='transaction')
    razorpay_order_id  = models.CharField(max_length=120, blank=True)
    razorpay_payment_id= models.CharField(max_length=120, blank=True)
    razorpay_signature = models.CharField(max_length=256, blank=True)
    total_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pandit_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status     = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    failure_reason     = models.TextField(blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.booking.booking_id} — {self.payment_status}"


class Payout(models.Model):
    """Pandit payout requests and admin approval."""
    class Status(models.TextChoices):
        PENDING  = 'PENDING',  _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        PAID     = 'PAID',     _('Paid')
        REJECTED = 'REJECTED', _('Rejected')

    pandit       = models.ForeignKey('users.PanditProfile', on_delete=models.CASCADE, related_name='payouts')
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    utr_reference= models.CharField(max_length=120, blank=True, help_text='UTR / Transaction reference after payment')
    remark       = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    paid_at      = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout ₹{self.amount} — {self.pandit.user.get_full_name()} — {self.status}"


class AvailabilitySlot(models.Model):
    """Pandit's available date + time-slot."""
    class TimeSlot(models.TextChoices):
        MORNING   = 'MORNING',   _('Morning (6 AM–12 PM)')
        AFTERNOON = 'AFTERNOON', _('Afternoon (12–4 PM)')
        EVENING   = 'EVENING',   _('Evening (4–8 PM)')

    pandit    = models.ForeignKey('users.PanditProfile', on_delete=models.CASCADE, related_name='slots')
    date      = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TimeSlot.choices)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pandit', 'date', 'time_slot')
        ordering = ['date', 'time_slot']

    def __str__(self):
        return f"{self.pandit.user.get_full_name()} | {self.date} | {self.time_slot}"
