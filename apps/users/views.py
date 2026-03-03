"""apps/users/views.py — Auth views"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache

from .models import User, PanditProfile, ClientProfile
from .forms import (ClientRegisterForm, PanditRegisterForm, LoginForm,
                    PanditEditProfileForm, ClientEditProfileForm,
                    ForgotPasswordForm, ResetPasswordForm)
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


def forgot_password_view(request):
    """Step 1: User enters email, gets token."""
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            token = get_random_string(32)
            cache.set(f'pwd_reset_{token}', user.pk, timeout=1800)  # 30 min
            reset_url = request.build_absolute_uri(f'/auth/reset-password/{token}/')
            try:
                send_mail(
                    'Reset Your Password — SD Online Pandit Jee',
                    f'Click below to reset your password (valid 30 min):\n\n{reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'If that email is registered, a reset link has been sent. 📧')
        except User.DoesNotExist:
            messages.success(request, 'If that email is registered, a reset link has been sent. 📧')
        return redirect('users:login')
    return render(request, 'users/forgot_password.jinja', {'form': form, 'page_title': 'Forgot Password'})


def reset_password_view(request, token):
    """Step 2: User clicks token link and sets new password."""
    user_pk = cache.get(f'pwd_reset_{token}')
    if not user_pk:
        messages.error(request, 'This reset link is invalid or has expired.')
        return redirect('users:forgot_password')
    user = get_object_or_404(User, pk=user_pk)
    form = ResetPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['new_password'])
        user.save()
        cache.delete(f'pwd_reset_{token}')
        messages.success(request, 'Password reset successfully! Please log in.')
        return redirect('users:login')
    return render(request, 'users/reset_password.jinja', {'form': form, 'page_title': 'Reset Password', 'token': token})


def _role_redirect(user):
    if user.is_site_admin or user.is_staff:
        return redirect('/admin/')
    if user.is_pandit:
        return redirect('/auth/pandit/dashboard/')
    return redirect('core:home')


@login_required
def profile_view(request):
    """Client profile edit."""
    if request.user.role == 'PANDIT':
        return redirect('users:pandit_edit_profile')
    form = ClientEditProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully! 🙏')
        return redirect('users:profile')
    return render(request, 'users/profile.jinja', {'form': form, 'page_title': 'My Profile'})


@login_required
def pandit_edit_profile(request):
    """Pandit profile edit."""
    if request.user.role != 'PANDIT':
        return redirect('core:home')
    profile = request.user.pandit_profile
    initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone,
        'specializations': profile.specializations.all(),
    }
    form = PanditEditProfileForm(request.POST or None, request.FILES or None,
                                  instance=profile, initial=initial)
    if request.method == 'POST' and form.is_valid():
        # Save profile fields
        profile = form.save(commit=False)
        profile.save()
        form.save_m2m()
        # Save user fields
        request.user.first_name = form.cleaned_data['first_name']
        request.user.last_name = form.cleaned_data['last_name']
        request.user.phone = form.cleaned_data.get('phone', '')
        if 'profile_image' in request.FILES:
            request.user.profile_image = request.FILES['profile_image']
        request.user.save()
        messages.success(request, 'Profile updated successfully! 🙏')
        return redirect('users:pandit_dashboard')
    return render(request, 'users/pandit_edit_profile.jinja', {
        'form': form, 'page_title': 'Edit Profile', 'profile': profile
    })


@login_required
def pandit_dashboard(request):
    """Pandit Dashboard: View bookings, earnings, etc."""
    if request.user.role != 'PANDIT':
        messages.error(request, 'Only Pandits can access this dashboard.')
        return redirect('core:home')

    profile = request.user.pandit_profile
    bookings = Booking.objects.filter(pandit__user=request.user).order_by('-created_at')

    active_bookings = bookings.filter(status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED])
    completed_bookings = bookings.filter(status=Booking.Status.COMPLETED)
    completed_count = completed_bookings.count()
    pending_count = bookings.filter(status=Booking.Status.PENDING).count()

    # Earnings
    earnings_qs = completed_bookings.aggregate(
        total=Sum('pandit_amount'),
        commission=Sum('commission_amount'),
        gross=Sum('amount'),
    )
    total_earnings  = earnings_qs['total'] or 0
    total_commission = earnings_qs['commission'] or 0
    gross_revenue   = earnings_qs['gross'] or 0

    return render(request, 'users/pandit_dashboard.jinja', {
        'profile': profile,
        'active_bookings': active_bookings,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'total_earnings': total_earnings,
        'total_commission': total_commission,
        'gross_revenue': gross_revenue,
        'page_title': 'Pandit Dashboard',
    })


@login_required
def pandit_action_booking(request, booking_id):
    """Accept, Reject, or Complete a booking"""
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
        profile = request.user.pandit_profile
        profile.total_bookings += 1
        profile.save()

    booking.save()
    return redirect('users:pandit_dashboard')
