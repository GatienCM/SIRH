from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ProfessionViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'professions', ProfessionViewSet, basename='profession')
router.register(r'', EmployeeViewSet, basename='employee')

app_name = 'employees'

urlpatterns = [
    path('', include(router.urls)),
]
