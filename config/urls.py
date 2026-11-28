"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import connection

# Health check view
def health_check(request):
    """Health check endpoint for Docker/load balancer."""
    try:
        # Check database connection
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "error"
    
    status = 200 if db_status == "ok" else 503
    return JsonResponse({
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
    }, status=status)

# i18n patterns (with locale prefix) - must be assigned directly to preserve LocalePrefixPattern detection
i18n_urlpatterns = i18n_patterns(
    path('learning/', include('learning.urls')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('practice/', include('practice.urls')),
    path('progress/', include('progress.urls')),
    path('ai/', include('ai.urls')),
)

# Non-i18n patterns (no locale prefix) - must come first
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('health/', health_check, name='health'),
    # API — без языкового префикса (вызывается из JS как /api/...)
    path('api/', include('runner.urls')),
    path('api/ai/', include('ai.api_urls')),
]

# Add i18n patterns - these contain LocalePrefixPattern which LocaleMiddleware detects
urlpatterns += i18n_patterns(
    path('learning/', include('learning.urls')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('practice/', include('practice.urls')),
    path('progress/', include('progress.urls')),
    path('ai/', include('ai.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # In development, serve static files from STATICFILES_DIRS, not STATIC_ROOT
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)