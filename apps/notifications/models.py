from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


class Notification(models.Model):
    """In-app notification for users."""
    class Type(models.TextChoices):
        BOOKING   = 'BOOKING',  _('Booking')
        PAYMENT   = 'PAYMENT',  _('Payment')
        REVIEW    = 'REVIEW',   _('Review')
        PAYOUT    = 'PAYOUT',   _('Payout')
        SYSTEM    = 'SYSTEM',   _('System')

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    link       = models.CharField(max_length=300, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.title} → {self.user.email}"


def notify(user, title, message, notif_type='SYSTEM', link=''):
    """Helper to create an in-app notification."""
    Notification.objects.create(
        user=user, title=title, message=message,
        notif_type=notif_type, link=link,
    )
