from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardViewSet, LeaveRequestViewSet, TimeOffBalanceViewSet,
    DocumentViewSet, NotificationViewSet
)

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'time-off-balances', TimeOffBalanceViewSet, basename='time-off-balance')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'notifications', NotificationViewSet, basename='notification')

app_name = 'portal'

urlpatterns = [
    path('', include(router.urls)),
]
