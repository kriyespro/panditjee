"""apps/users/views.py — Auth views"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import User, PanditProfile, ClientProfile
from .forms import ClientRegisterForm, PanditRegisterForm, LoginForm
from apps.bookings.models import Booking


def login_view(request):
    if request.user.is_authenticated:
        return _role_redirect(request.user)
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.email}! 🙏')
            return _role_redirect(user)
        messages.error(request, 'Invalid email or password.')
    return render(request, 'users/login.jinja', {'form': form, 'page_title': 'Login — SD Online Pandit Jee'})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. 🙏')
    return redirect('core:home')


def register_client(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    form = ClientRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = User.Role.CLIENT
        user.username = user.email.split('@')[0]
        user.set_password(form.cleaned_data['password'])
        user.save()
        ClientProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, 'Account created! Welcome to SD Online Pandit Jee 🙏')
        return redirect('core:home')
    return render(request, 'users/register_client.jinja', {'form': form, 'page_title': 'Register as Client'})


def register_pandit(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    form = PanditRegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = User.Role.PANDIT
        user.username = user.email.split('@')[0]
        user.set_password(form.cleaned_data['password'])
        user.save()
        pandit = PanditProfile.objects.create(
            user=user,
            city=form.cleaned_data.get('city'),
            experience_years=form.cleaned_data.get('experience_years', 0),
            languages=form.cleaned_data.get('languages', 'Hindi'),
            base_price=form.cleaned_data.get('base_price', 1500),
            id_proof=form.cleaned_data.get('id_proof'),
            bank_account_name=form.cleaned_data.get('bank_account_name', ''),
            bank_account_number=form.cleaned_data.get('bank_account_number', ''),
            ifsc_code=form.cleaned_data.get('ifsc_code', ''),
        )
        if form.cleaned_data.get('specializations'):
            pandit.specializations.set(form.cleaned_data['specializations'])
        messages.success(request, 'Registration submitted! Admin will review and approve your profile. 🙏')
        return redirect('core:home')
    return render(request, 'users/register_pandit.jinja', {'form': form, 'page_title': 'Register as Pandit'})


def _role_redirect(user):
    if user.is_site_admin or user.is_staff:
        return redirect('/admin/')
    if user.is_pandit:
        return redirect('/pandit/dashboard/')
    return redirect('core:home')


@login_required
def profile_view(request):
    """
    Placeholder for edit profile page
    """
    return render(request, 'users/profile.jinja', {'page_title': 'My Profile'})


@login_required
def pandit_dashboard(request):
    """
    Pandit Dashboard: View bookings, earnings, etc.
    """
    if request.user.role != 'PANDIT':
        messages.error(request, 'Only Pandits can access this dashboard.')
        return redirect('core:home')
        
    bookings = Booking.objects.filter(pandit__user=request.user).order_by('-created_at')
    
    active_bookings = bookings.filter(status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED])
    completed_count = bookings.filter(status=Booking.Status.COMPLETED).count()
    pending_count = bookings.filter(status=Booking.Status.PENDING).count()
    
    # Calculate Total Earnings
    earnings_dict = bookings.filter(status=Booking.Status.COMPLETED).aggregate(total=Sum('pandit_amount'))
    total_earnings = earnings_dict['total'] or 0
    
    return render(request, 'users/pandit_dashboard.jinja', {
        'active_bookings': active_bookings,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'total_earnings': total_earnings,
        'page_title': 'Pandit Dashboard'
    })


@login_required
def pandit_action_booking(request, booking_id):
    """
    Accept, Reject, or Complete a booking
    """
    if request.user.role != 'PANDIT' or request.method != 'POST':
        return redirect('core:home')
        
    booking = get_object_or_404(Booking, booking_id=booking_id, pandit__user=request.user)
    action = request.POST.get('action')
    
    if action == 'accept' and booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.CONFIRMED
        messages.success(request, f"Booking {str(booking.booking_id)[:8].upper()} Accepted.")
    elif action == 'reject' and booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.CANCELLED
        messages.info(request, f"Booking {str(booking.booking_id)[:8].upper()} Rejected.")
    elif action == 'complete' and booking.status == Booking.Status.CONFIRMED:
        booking.status = Booking.Status.COMPLETED
        messages.success(request, f"Booking {str(booking.booking_id)[:8].upper()} marked as Completed!")
        
        # update pandit stats
        profile = request.user.panditprofile
        profile.total_bookings += 1
        profile.save()
        
    booking.save()
    return redirect('users:pandit_dashboard')
