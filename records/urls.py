from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import ClinicalHistoryViewSet, DashboardSuperAdminView, DashboardRecepcionView

router = SimpleRouter()
router.register(r'clinical-history', ClinicalHistoryViewSet, basename='clinical-history')

urlpatterns = [
    path('dashboard/superadmin/', DashboardSuperAdminView.as_view(), name='dashboard-superadmin'),
    path('dashboard/recepcion/', DashboardRecepcionView.as_view(), name='dashboard-recepcion'),
]

urlpatterns += router.urls
