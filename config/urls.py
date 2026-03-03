"""
config/urls.py — Root URL configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = "SD Pandit Jee Admin"
admin.site.site_title = "SD Pandit Jee"
admin.site.index_title = "Administration"

urlpatterns = [
    path('sd/', admin.site.urls),  # Default Django admin renamed to /sd/
    
    # App URLs
    path('', include('apps.core.urls')),         # Public pages / home
    path('auth/', include('apps.users.urls')),   # Auth: login, register, etc.
    path('booking/', include('apps.bookings.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('admin/', include('apps.dashboard.urls')),
    # Phase 2 — REST API
    path('api/', include('apps.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.core.views.custom_404_view'
handler500 = 'apps.core.views.custom_500_view'
