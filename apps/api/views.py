"""apps/api/views.py — REST API endpoints (Phase 2)"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.users.models import User, PanditProfile
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.core.models import City, PujaCategory


# ── Auth ──────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    email    = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    name     = request.data.get('name', 'User')
    role     = request.data.get('role', 'CLIENT')

    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered.'}, status=400)

    first, *last = name.split(' ', 1)
    user = User.objects.create_user(
        username=email, email=email, password=password,
        first_name=first, last_name=last[0] if last else '',
        role=role.upper(),
    )
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token), 'refresh': str(refresh)}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    email    = request.data.get('email', '')
    password = request.data.get('password', '')
    user     = authenticate(request, username=email, password=password)
    if not user:
        return Response({'error': 'Invalid credentials.'}, status=401)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'role': user.role,
        'name': user.get_full_name(),
    })


# ── Pandits ───────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def api_pandit_list(request):
    pandits = PanditProfile.objects.filter(status='APPROVED').select_related('user', 'city')
    city  = request.GET.get('city', '')
    puja  = request.GET.get('puja', '')
    if city:
        pandits = pandits.filter(city__slug=city)
    if puja:
        pandits = pandits.filter(specializations__slug=puja)
    data = [{
        'id': p.pk,
        'name': p.user.get_full_name(),
        'slug': p.slug,
        'city': p.city.name if p.city else '',
        'experience_years': p.experience_years,
        'base_price': str(p.base_price),
        'average_rating': str(p.average_rating),
        'total_bookings': p.total_bookings,
        'languages': p.languages,
        'specializations': [s.name for s in p.specializations.all()],
    } for p in pandits[:50]]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_pandit_detail(request, pandit_id):
    try:
        p = PanditProfile.objects.get(pk=pandit_id, status='APPROVED')
    except PanditProfile.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    return Response({
        'id': p.pk,
        'name': p.user.get_full_name(),
        'slug': p.slug,
        'city': p.city.name if p.city else '',
        'experience_years': p.experience_years,
        'base_price': str(p.base_price),
        'average_rating': str(p.average_rating),
        'total_bookings': p.total_bookings,
        'bio': p.bio,
        'languages': p.languages,
        'specializations': [{'name': s.name, 'icon': s.icon} for s in p.specializations.all()],
    })


# ── Bookings ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_bookings(request):
    if request.user.role == 'CLIENT':
        bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    elif request.user.role == 'PANDIT':
        bookings = Booking.objects.filter(pandit__user=request.user).order_by('-created_at')
    else:
        bookings = Booking.objects.none()
    data = [{
        'booking_id': str(b.booking_id),
        'pandit': b.pandit.user.get_full_name(),
        'client': b.client.get_full_name(),
        'puja': b.puja_category.name if b.puja_category else '',
        'puja_date': str(b.puja_date),
        'puja_time': str(b.puja_time),
        'amount': str(b.amount),
        'status': b.status,
        'created_at': str(b.created_at.date()),
    } for b in bookings]
    return Response(data)


# ── Reviews ───────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_review(request):
    booking_id = request.data.get('booking_id')
    rating     = request.data.get('rating')
    text       = request.data.get('review_text', '')
    try:
        booking = Booking.objects.get(booking_id=booking_id, client=request.user, status='COMPLETED')
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found or not eligible for review.'}, status=404)
    if hasattr(booking, 'review'):
        return Response({'error': 'Already reviewed.'}, status=400)
    review = Review.objects.create(
        booking=booking, pandit=booking.pandit, client=request.user,
        rating=int(rating), review_text=text,
    )
    from django.db.models import Avg
    avg = booking.pandit.reviews.aggregate(Avg('rating'))['rating__avg']
    booking.pandit.average_rating = round(avg, 1) if avg else 0.0
    booking.pandit.save()
    return Response({'message': 'Review submitted successfully.'}, status=201)
