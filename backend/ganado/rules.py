from datetime import timedelta
from django.utils import timezone
from .models import Alert

# Constantes para los umbrales de alerta
UMBRAL_TEMPERATURA_ALTA = 39.2
UMBRAL_ACTIVIDAD_ALTA = 90.0 # Umbral para posible celo

def check_for_existing_alert(ejemplar, alert_type):
    """ Evita crear alertas duplicadas en un corto periodo de tiempo. """
    since = timezone.now() - timedelta(hours=12)
    return Alert.objects.filter(
        ejemplar=ejemplar,
        alert_type=alert_type,
        is_read=False,
        timestamp__gte=since
    ).exists()

def process_sensor_data(ejemplar, temperatura, actividad):
    """
    Función principal del motor de reglas.
    Analiza los datos y crea alertas si se cumplen las condiciones.
    """
    if temperatura and temperatura > UMBRAL_TEMPERATURA_ALTA:
        if not check_for_existing_alert(ejemplar, Alert.AlertType.FIEBRE):
            Alert.objects.create(
                ejemplar=ejemplar,
                alert_type=Alert.AlertType.FIEBRE,
                message=f"Temperatura alta detectada: {temperatura}°C."
            )

    if actividad and actividad > UMBRAL_ACTIVIDAD_ALTA:
        if not check_for_existing_alert(ejemplar, Alert.AlertType.CELO):
            Alert.objects.create(
                ejemplar=ejemplar,
                alert_type=Alert.AlertType.CELO,
                message=f"Pico de actividad detectado: {actividad}. Posible celo."
            )