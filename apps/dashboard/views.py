from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum

from apps.users.models import User, PanditProfile, ClientProfile
from apps.bookings.models import Booking

@staff_member_required(login_url='users:login')
def admin_dashboard_home(request):
    # KPIs
    total_users = User.objects.count()
    total_pandits = PanditProfile.objects.count()
    total_bookings = Booking.objects.count()
    
    earnings_dict = Booking.objects.filter(status=Booking.Status.COMPLETED).aggregate(total=Sum('commission_amount'))
    total_revenue = earnings_dict['total'] or 0
    
    pending_pandits = PanditProfile.objects.filter(status='PENDING')
    recent_bookings = Booking.objects.order_by('-created_at')[:5]

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
    pandits = PanditProfile.objects.all().order_by('-user__date_joined')
    return render(request, 'dashboard/pandits.jinja', {'pandits': pandits})

@staff_member_required(login_url='users:login')
def admin_bookings_list(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'dashboard/bookings.jinja', {'bookings': bookings})

@staff_member_required(login_url='users:login')
def admin_action_pandit(request, user_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        profile = get_object_or_404(PanditProfile, user__id=user_id)
        
        if action == 'approve':
            profile.status = 'APPROVED'
            messages.success(request, f"Pandit {profile.user.get_full_name()} approved.")
        elif action == 'reject':
            profile.status = 'REJECTED'
            messages.info(request, f"Pandit {profile.user.get_full_name()} rejected.")
        elif action == 'suspend':
            profile.status = 'SUSPENDED'
            messages.warning(request, f"Pandit {profile.user.get_full_name()} suspended.")
            
        profile.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:home'))
