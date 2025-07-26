from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ganado.views import DashboardKPIView, TaskStatusView
from django.conf import settings
from django.conf.urls.static import static

# SECCIÓN DE IMPORTACIÓN CORREGIDA
# Se añade el 'AlertViewSet' que faltaba a la importación desde .views
from .views import (
    RazaViewSet, CategoriaPuntuacionViewSet,
    EjemplarViewSet, CalificacionViewSet, AlertViewSet
)

router = DefaultRouter()
router.register(r'razas', RazaViewSet)
router.register(r'categorias', CategoriaPuntuacionViewSet)
router.register(r'ejemplares', EjemplarViewSet)
router.register(r'calificaciones', CalificacionViewSet)
# Esta línea ahora funcionará porque AlertViewSet ha sido importado
router.register(r'alerts', AlertViewSet) 

urlpatterns = [
    path('', include(router.urls)),
    path('api/dashboard-kpis/', DashboardKPIView.as_view(), name='dashboard_kpis'),
    path('api/task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)