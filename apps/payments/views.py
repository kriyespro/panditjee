"""apps/payments/views.py — Razorpay integration, Payout requests, Availability, Invoice"""
import json
import hmac
import hashlib
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings as django_settings

from apps.bookings.models import Booking
from apps.users.models import PanditProfile
from .models import Transaction, Payout, AvailabilitySlot

try:
    import razorpay
    RAZORPAY_KEY_ID     = getattr(django_settings, 'RAZORPAY_KEY_ID', 'rzp_test_demo')
    RAZORPAY_KEY_SECRET = getattr(django_settings, 'RAZORPAY_KEY_SECRET', 'demo_secret')
    rz_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False

# ── Razorpay Payment ─────────────────────────────────────────────

@login_required
def razorpay_checkout(request, booking_id):
    """Initiate Razorpay payment for a COD booking."""
    booking = get_object_or_404(Booking, booking_id=booking_id, client=request.user)
    if booking.payment_mode != Booking.PaymentMode.ONLINE:
        messages.error(request, "This booking is on Cash on Delivery.")
        return redirect('bookings:my_bookings')

    if RAZORPAY_AVAILABLE:
        amount_paise = int(booking.amount * 100)
        order = rz_client.order.create({'amount': amount_paise, 'currency': 'INR', 'payment_capture': True})
        Transaction.objects.update_or_create(
            booking=booking,
            defaults={'razorpay_order_id': order['id'], 'total_amount': booking.amount,
                      'commission_amount': booking.commission_amount,
                      'pandit_amount': booking.pandit_amount},
        )
        context = {
            'booking': booking,
            'razorpay_key': RAZORPAY_KEY_ID,
            'razorpay_order_id': order['id'],
            'amount_paise': amount_paise,
        }
    else:
        context = {'booking': booking, 'razorpay_unavailable': True}

    return render(request, 'payments/razorpay_checkout.jinja', context)


@csrf_exempt
def razorpay_callback(request):
    """Handle Razorpay payment callback."""
    if request.method == 'POST':
        data = request.POST
        order_id   = data.get('razorpay_order_id', '')
        payment_id = data.get('razorpay_payment_id', '')
        signature  = data.get('razorpay_signature', '')

        try:
            txn = Transaction.objects.get(razorpay_order_id=order_id)
            if RAZORPAY_AVAILABLE:
                rz_client.utility.verify_payment_signature({
                    'razorpay_order_id':   order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature':  signature,
                })
            txn.razorpay_payment_id = payment_id
            txn.razorpay_signature  = signature
            txn.payment_status      = Transaction.Status.SUCCESS
            txn.save()
            txn.booking.status = Booking.Status.CONFIRMED
            txn.booking.save()
            messages.success(request, "Payment successful! Booking confirmed.")
            return redirect('bookings:success', booking_id=txn.booking.booking_id)
        except (Transaction.DoesNotExist, Exception) as e:
            messages.error(request, "Payment verification failed.")
            return redirect('bookings:my_bookings')
    return redirect('core:home')


# ── Payout ──────────────────────────────────────────────────────

@login_required
def request_payout(request):
    """Pandit requests a payout for earned amount."""
    if request.user.role != 'PANDIT':
        return redirect('core:home')
    pandit = request.user.pandit_profile
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amt = Decimal(amount)
            if amt <= 0:
                raise ValueError
            Payout.objects.create(pandit=pandit, amount=amt)
            messages.success(request, f"Payout request of ₹{amt} submitted! Admin will review within 2-3 business days.")
        except (ValueError, Exception):
            messages.error(request, "Invalid amount.")
        return redirect('payments:payout_history')

    completed_total = Decimal('0')
    for b in pandit.received_bookings.filter(status='COMPLETED'):
        completed_total += b.pandit_amount
    paid_payouts = Payout.objects.filter(pandit=pandit, status__in=['APPROVED','PAID']).values_list('amount', flat=True)
    paid_total = sum(paid_payouts, Decimal('0'))
    available = max(completed_total - paid_total, Decimal('0'))

    return render(request, 'payments/request_payout.jinja', {
        'pandit': pandit,
        'available': available,
        'payouts': Payout.objects.filter(pandit=pandit).order_by('-requested_at'),
    })


@login_required
def payout_history(request):
    if request.user.role != 'PANDIT':
        return redirect('core:home')
    pandit = request.user.pandit_profile
    payouts = Payout.objects.filter(pandit=pandit).order_by('-requested_at')
    return render(request, 'payments/payout_history.jinja', {'payouts': payouts})


# ── Availability Calendar ────────────────────────────────────────

@login_required
def availability_calendar(request):
    """Pandit manages available slots."""
    if request.user.role != 'PANDIT':
        return redirect('core:home')
    pandit = request.user.pandit_profile

    if request.method == 'POST':
        action    = request.POST.get('action')
        date_str  = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        from datetime import date
        try:
            slot_date = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messages.error(request, "Invalid date.")
            return redirect('payments:availability')

        if action == 'add':
            AvailabilitySlot.objects.get_or_create(pandit=pandit, date=slot_date, time_slot=time_slot)
            messages.success(request, f"Slot added: {slot_date} {time_slot}")
        elif action == 'remove':
            AvailabilitySlot.objects.filter(pandit=pandit, date=slot_date, time_slot=time_slot).delete()
            messages.success(request, f"Slot removed.")
        return redirect('payments:availability')

    from datetime import date, timedelta
    today = date.today()
    next_30 = [today + timedelta(days=i) for i in range(30)]
    existing = set(
        AvailabilitySlot.objects.filter(pandit=pandit, date__gte=today)
        .values_list('date', 'time_slot')
    )
    return render(request, 'payments/availability.jinja', {
        'pandit': pandit,
        'next_30': next_30,
        'time_slots': AvailabilitySlot.TimeSlot.choices,
        'existing': existing,
    })


# ── Invoice ──────────────────────────────────────────────────────

@login_required
def invoice_view(request, booking_id):
    """Print/download invoice for a booking."""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    if request.user != booking.client and request.user != booking.pandit.user and not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('core:home')
    return render(request, 'payments/invoice.jinja', {'booking': booking})
