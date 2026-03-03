from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.bookings.models import Booking
from .models import Review
from .forms import ReviewForm
from django.db.models import Avg

@login_required
def create_review(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, client=request.user, status=Booking.Status.COMPLETED)
    
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this booking.")
        return redirect('bookings:my_bookings')
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.pandit = booking.pandit
            review.client = request.user
            review.save()
            
            # Update average rating on PanditProfile
            pandit_profile = booking.pandit
            avg_rating = pandit_profile.reviews.aggregate(Avg('rating'))['rating__avg']
            pandit_profile.average_rating = round(avg_rating, 1) if avg_rating else 0.0
            pandit_profile.save()
            
            messages.success(request, "Thank you for your review!")
            return redirect('bookings:my_bookings')
    else:
        form = ReviewForm()
        
    return render(request, 'reviews/create.jinja', {'form': form, 'booking': booking})
