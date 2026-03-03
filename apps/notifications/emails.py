"""
apps/notifications/emails.py — Email helper functions
"""
from django.core.mail import send_mail
from django.conf import settings


def _send(subject, message, to_email):
    """Safe send — never raises."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_booking_confirmation(booking):
    """Email client after booking."""
    subject = f"Booking Confirmed 🙏 — {booking.puja_category.name if booking.puja_category else 'Puja'}"
    message = f"""Namaste {booking.client.get_full_name()},

Your booking has been confirmed!

Booking ID : {str(booking.booking_id)[:8].upper()}
Pandit     : Pt. {booking.pandit.user.get_full_name()}
Puja       : {booking.puja_category.name if booking.puja_category else 'Puja'}
Date       : {booking.puja_date}
Time       : {booking.puja_time}
Address    : {booking.address}
Amount     : ₹{booking.amount}
Payment    : {booking.get_payment_mode_display()}

Thank you for trusting SD Online Pandit Jee 🙏
"""
    _send(subject, message, booking.client.email)


def send_pandit_new_booking(booking):
    """Email pandit when a new booking is received."""
    subject = f"New Booking Received — {booking.puja_category.name if booking.puja_category else 'Puja'}"
    message = f"""Namaste Pt. {booking.pandit.user.get_full_name()},

You have received a new booking!

Booking ID : {str(booking.booking_id)[:8].upper()}
Client     : {booking.client.get_full_name()}
Puja       : {booking.puja_category.name if booking.puja_category else 'Puja'}
Date       : {booking.puja_date}
Time       : {booking.puja_time}
Address    : {booking.address}
Your Payout: ₹{booking.pandit_amount}

Please log in to your dashboard to accept the booking.

SD Online Pandit Jee Team 🙏
"""
    _send(subject, message, booking.pandit.user.email)


def send_pandit_approved(pandit_profile):
    """Email pandit when admin approves their profile."""
    subject = "🎉 Your Pandit Profile is Approved — SD Online Pandit Jee"
    message = f"""Namaste Pt. {pandit_profile.user.get_full_name()},

Great news! Your pandit profile has been approved and is now live on SD Online Pandit Jee.

Clients can now discover and book you at:
https://sdonlinepanditjee.com/pandits/{pandit_profile.slug}/

Start receiving bookings by keeping your profile updated.

SD Online Pandit Jee Team 🙏
"""
    _send(subject, message, pandit_profile.user.email)


def send_pandit_rejected(pandit_profile):
    """Email pandit when admin rejects their profile."""
    subject = "Profile Review — SD Online Pandit Jee"
    message = f"""Namaste Pt. {pandit_profile.user.get_full_name()},

Thank you for registering on SD Online Pandit Jee.

After reviewing your profile, we are unable to approve it at this time.
Please contact our support team for more information or to reapply.

SD Online Pandit Jee Team 🙏
"""
    _send(subject, message, pandit_profile.user.email)


def send_booking_cancelled(booking):
    """Email both parties when booking is cancelled."""
    subject = f"Booking Cancelled — {str(booking.booking_id)[:8].upper()}"
    _send(subject, f"Your booking (ID: {str(booking.booking_id)[:8].upper()}) has been cancelled.", booking.client.email)
    _send(subject, f"Booking (ID: {str(booking.booking_id)[:8].upper()}) from {booking.client.get_full_name()} has been cancelled.", booking.pandit.user.email)
