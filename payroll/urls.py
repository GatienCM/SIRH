from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalaryScaleViewSet, PayrollViewSet, PayrollItemViewSet

router = DefaultRouter()
router.register(r'salary-scales', SalaryScaleViewSet, basename='salary-scale')
router.register(r'payrolls', PayrollViewSet, basename='payroll')
router.register(r'items', PayrollItemViewSet, basename='payroll-item')

app_name = 'payroll'

urlpatterns = [
    path('', include(router.urls)),
]
