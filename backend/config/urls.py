from django.urls import include, path

urlpatterns = [
    path('api/health/', include('apps.core.urls')),
    path('api/', include('apps.api.urls')),
]
