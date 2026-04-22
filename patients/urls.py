from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PatientViewSet

router = SimpleRouter()
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
]
