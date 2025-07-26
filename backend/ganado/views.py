from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated

# SECCIÓN DE IMPORTACIÓN CORREGIDA
# Se añaden los modelos que faltaban: Alert y SensorData
from .models import (
    Raza, CategoriaPuntuacion, Ejemplar, Calificacion, Alert, SensorData
)
# Se añade el serializador que faltaba: AlertSerializer
from .serializers import (
    RazaSerializer, CategoriaPuntuacionSerializer,
    EjemplarSerializer, CalificacionSerializer, SensorDataSerializer, AlertSerializer
)
from .rules import process_sensor_data

# ... (importaciones existentes)
from .tasks import generate_ejemplar_report
from celery.result import AsyncResult
from django.db.models import Count, Avg


# --- PERMISOS Y VISTAS DE SPRINT 4 ---

class HasIotApiKey(BasePermission):
    """ Permiso simple para verificar la API key en la cabecera. """
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-KEY')
        return api_key == settings.IOT_API_KEY

class IoTDataIngestionView(APIView):
    permission_classes = [HasIotApiKey]

    def post(self, request, *args, **kwargs):
        data = request.data
        device_id = data.get('device_id')
        temperatura = data.get('temperatura')
        actividad = data.get('actividad')

        if not device_id:
            return Response({"error": "device_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ejemplar = Ejemplar.objects.get(identificador=device_id)
        except Ejemplar.DoesNotExist:
            return Response({"error": "Ejemplar no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        SensorData.objects.create(
            ejemplar=ejemplar,
            temperatura=temperatura,
            actividad=actividad
        )

        process_sensor_data(ejemplar, temperatura, actividad)
        return Response({"status": "datos recibidos"}, status=status.HTTP_201_CREATED)


# --- VIEWSETS PRINCIPALES ---

class RazaViewSet(viewsets.ModelViewSet):
    queryset = Raza.objects.all()
    serializer_class = RazaSerializer
    permission_classes = [IsAuthenticated]

class CategoriaPuntuacionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoriaPuntuacion.objects.prefetch_related('caracteristicas').all()
    serializer_class = CategoriaPuntuacionSerializer
    permission_classes = [IsAuthenticated]

class EjemplarViewSet(viewsets.ModelViewSet):
    queryset = Ejemplar.objects.prefetch_related('calificaciones__caracteristica__categoria', 'alerts').all()
    serializer_class = EjemplarSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='calificar')
    @transaction.atomic
    def calificar(self, request, pk=None):
        ejemplar = self.get_object()
        data = request.data.copy()
        for calificacion_data in data:
            calificacion_data['ejemplar'] = ejemplar.pk

        serializer = CalificacionSerializer(data=data, many=True)
        if serializer.is_valid():
            self.perform_create_batch(serializer, request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create_batch(self, serializer, user):
        serializer.save(evaluador=user)

    @action(detail=True, methods=['get'], url_path='sensor-data')
    def sensor_data(self, request, pk=None):
        ejemplar = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        data = ejemplar.sensor_data.filter(timestamp__gte=since).order_by('timestamp')
        serializer = SensorDataSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='generate-report')
    def generate_report(self, request, pk=None):
        task = generate_ejemplar_report.delay(pk)
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(evaluador=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    # Se corrige el error aquí, ahora 'Alert' y 'AlertSerializer' están definidos
    queryset = Alert.objects.filter(is_read=False)
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'status': 'alerta marcada como leída'})
    
class DashboardKPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_ejemplares = Ejemplar.objects.count()
        active_alerts = Alert.objects.filter(is_read=False).count()

        ejemplares_por_raza = Ejemplar.objects.values('raza__nombre').annotate(count=Count('id'))

        # Nota: Esto será más complejo en una app real para obtener el score de cada animal
        avg_score = 0 # Placeholder para una lógica más compleja

        kpis = {
            'total_ejemplares': total_ejemplares,
            'active_alerts': active_alerts,
            'ejemplares_por_raza': list(ejemplares_por_raza),
            'avg_score': avg_score
        }
        return Response(kpis)

class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        task_result = AsyncResult(task_id)
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": task_result.result if task_result.successful() else None
        }
        return Response(result)        