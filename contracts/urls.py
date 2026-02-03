from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ContractViewSet

router = DefaultRouter()
router.register(r'', ContractViewSet, basename='contract')

app_name = 'contracts'

urlpatterns = [
    path('', include(router.urls)),
]
