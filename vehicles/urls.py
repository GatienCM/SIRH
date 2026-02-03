from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import VehicleViewSet

router = DefaultRouter()
router.register(r'', VehicleViewSet, basename='vehicle')

app_name = 'vehicles'

urlpatterns = [
    path('', include(router.urls)),
]
