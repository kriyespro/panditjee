from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
import csv

from apps.users.models import User, PanditProfile, ClientProfile
from apps.bookings.models import Booking


@staff_member_required(login_url='users:login')
def admin_dashboard_home(request):
    total_users    = User.objects.count()
    total_pandits  = PanditProfile.objects.filter(status='APPROVED').count()
    total_bookings = Booking.objects.count()
    earnings_dict  = Booking.objects.filter(status=Booking.Status.COMPLETED).aggregate(total=Sum('commission_amount'))
    total_revenue  = earnings_dict['total'] or 0
    pending_pandits = PanditProfile.objects.filter(status='PENDING').select_related('user', 'city')
    recent_bookings = Booking.objects.order_by('-created_at').select_related('client', 'pandit__user', 'puja_category')[:5]

    return render(request, 'dashboard/home.jinja', {
        'total_users': total_users,
        'total_pandits': total_pandits,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'pending_pandits': pending_pandits,
        'recent_bookings': recent_bookings,
    })


@staff_member_required(login_url='users:login')
def admin_pandits_list(request):
    status_filter = request.GET.get('status', '')
    pandits = PanditProfile.objects.select_related('user', 'city').order_by('-user__date_joined')
    if status_filter:
        pandits = pandits.filter(status=status_filter)
    return render(request, 'dashboard/pandits.jinja', {
        'pandits': pandits,
        'status_filter': status_filter,
        'status_choices': PanditProfile.Status.choices,
    })


@staff_member_required(login_url='users:login')
def admin_bookings_list(request):
    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.order_by('-created_at').select_related('client', 'pandit__user', 'puja_category')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'dashboard/bookings.jinja', {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': Booking.Status.choices,
    })


@staff_member_required(login_url='users:login')
def admin_action_pandit(request, user_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        profile = get_object_or_404(PanditProfile, user__id=user_id)
        name = profile.user.get_full_name()

        if action == 'approve':
            profile.status = 'APPROVED'
            messages.success(request, f"Pandit {name} approved.")
        elif action == 'reject':
            profile.status = 'REJECTED'
            messages.info(request, f"Pandit {name} rejected.")
        elif action == 'suspend':
            profile.status = 'SUSPENDED'
            messages.warning(request, f"Pandit {name} suspended.")
        elif action == 'reinstate':
            profile.status = 'APPROVED'
            messages.success(request, f"Pandit {name} reinstated.")

        # Update commission if provided
        commission = request.POST.get('commission_percent', '').strip()
        if commission:
            try:
                profile.commission_percent = float(commission)
            except ValueError:
                pass

        profile.save()
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@staff_member_required(login_url='users:login')
def admin_booking_action(request, booking_id):
    """Update booking status from admin."""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=booking_id)
        new_status = request.POST.get('status')
        if new_status in dict(Booking.Status.choices):
            booking.status = new_status
            booking.save()
            messages.success(request, f"Booking status updated to {new_status}.")
    return redirect(request.META.get('HTTP_REFERER', '/admin/bookings/'))


@staff_member_required(login_url='users:login')
def admin_export_bookings_csv(request):
    """Export all bookings as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Booking ID', 'Client', 'Pandit', 'Puja', 'Date', 'Status', 'Amount', 'Commission', 'Pandit Amount'])
    for b in Booking.objects.select_related('client', 'pandit__user', 'puja_category').order_by('-created_at'):
        writer.writerow([
            str(b.booking_id)[:8].upper(),
            b.client.get_full_name(),
            b.pandit.user.get_full_name(),
            b.puja_category.name if b.puja_category else '',
            b.puja_date,
            b.status,
            b.amount,
            b.commission_amount,
            b.pandit_amount,
        ])
    return response
