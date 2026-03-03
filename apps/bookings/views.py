from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.models import PanditProfile
from .models import Booking
from .forms import BookingForm
from django.db import transaction

@login_required
def checkout_view(request, pandit_slug):
    """
    Step 1 & Step 2: User selects date/time/address and confirms (COD).
    """
    if request.user.role != 'CLIENT':
        messages.error(request, "Only clients can book pandits.")
        return redirect('core:home')
        
    pandit = get_object_or_404(PanditProfile, slug=pandit_slug)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, pandit=pandit)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.client = request.user
                booking.pandit = pandit
                
                # Fetch price for the selected puja category
                # For MVP, we use Pandit base_price, or if they have PujaPrice we'd use that.
                # Here we just use base_price for simplicity.
                booking.amount = pandit.base_price
                
                # Commission calculation (e.g. 20% global)
                commission_pct = Decimal(str(pandit.commission_percent)) if pandit.commission_percent is not None else Decimal('20.0')
                commission = (booking.amount * commission_pct) / Decimal('100')
                booking.commission_amount = commission
                booking.pandit_amount = booking.amount - commission
                
                booking.status = Booking.Status.CONFIRMED # auto confirm for COD
                booking.payment_mode = Booking.PaymentMode.COD
                booking.save()
                
            messages.success(request, f"Booking Confirmed! Your Booking ID: {booking.booking_id}")
            return redirect('bookings:success', booking_id=booking.booking_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BookingForm(pandit=pandit)
        
    return render(request, 'bookings/checkout.jinja', {
        'pandit': pandit,
        'form': form,
    })

@login_required
def booking_success_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, client=request.user)
    return render(request, 'bookings/success.jinja', {'booking': booking})

@login_required
def my_bookings_view(request):
    if request.user.role == 'CLIENT':
        bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    elif request.user.role == 'PANDIT':
        # Handled in pandit dashboard, but fall back just in case
        bookings = Booking.objects.filter(pandit__user=request.user).order_by('-created_at')
    else:
        bookings = []
        
    return render(request, 'bookings/my_bookings.jinja', {'bookings': bookings})

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, client=request.user)
    
    if booking.status in [Booking.Status.PENDING, Booking.Status.CONFIRMED]:
        # Validate 24hr cancellation policy (can add logic later)
        booking.status = Booking.Status.CANCELLED
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
    else:
        messages.error(request, f"You cannot cancel an already {booking.status.lower()} booking.")
        
    return redirect('bookings:my_bookings')
