from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import AuthViewSet, UserViewSet, LoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('', include(router.urls)),
]
