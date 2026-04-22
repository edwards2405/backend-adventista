from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import LoginView, LogoutView, MeView, StaffViewSet

router = SimpleRouter()
router.register(r'staff', StaffViewSet, basename='staff')

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='auth_login'),
    path('auth/logout', LogoutView.as_view(), name='auth_logout'),
    path('auth/me', MeView.as_view(), name='auth_me'),
    path('', include(router.urls)),
]
