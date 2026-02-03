from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ShiftTypeViewSet, ShiftViewSet, AssignmentViewSet

router = DefaultRouter()
router.register(r'shift-types', ShiftTypeViewSet, basename='shifttype')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'assignments', AssignmentViewSet, basename='assignment')

app_name = 'planning'

urlpatterns = [
    path('', include(router.urls)),
]
