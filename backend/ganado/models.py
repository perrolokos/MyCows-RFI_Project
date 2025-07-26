# Create your models here.
# ganado/models.py

from django.db import models
from django.conf import settings

class Raza(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    peso_ideal_min = models.FloatField(blank=True, null=True)
    peso_ideal_max = models.FloatField(blank=True, null=True)
    talla_ideal = models.FloatField(blank=True, null=True)
    capa_colores = models.CharField(max_length=255, blank=True, help_text="Colores aceptados separados por comas")

    def __str__(self):
        return self.nombre

# ... (otros modelos)

class CategoriaPuntuacion(models.Model):
    nombre = models.CharField(max_length=100)
    ponderacion = models.IntegerField(help_text="Porcentaje del total, ej: 40 para 40%")
    # CAMPO AÑADIDO: Almacena la suma de los puntajes ideales de sus características
    puntaje_ideal_total = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.ponderacion}%)"

# ... (otros modelos)

class Caracteristica(models.Model):
    categoria = models.ForeignKey(CategoriaPuntuacion, on_delete=models.CASCADE, related_name='caracteristicas')
    nombre = models.CharField(max_length=100)
    puntaje_ideal = models.IntegerField()
    rango_aceptado_min = models.FloatField()
    rango_aceptado_max = models.FloatField()

    def __str__(self):
        return self.nombre

class Ejemplar(models.Model):
    identificador = models.CharField(max_length=50, unique=True, help_text="ID del arete o RFID")
    nombre = models.CharField(max_length=100, blank=True)
    raza = models.ForeignKey(Raza, on_delete=models.PROTECT)
    fecha_nacimiento = models.DateField()
    peso_actual = models.FloatField(blank=True, null=True)
    talla_actual = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre or 'Sin Nombre'} ({self.identificador})"

class Calificacion(models.Model):
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='calificaciones')
    caracteristica = models.ForeignKey(Caracteristica, on_delete=models.CASCADE)
    puntuacion_obtenida = models.FloatField()
    fecha_calificacion = models.DateField(auto_now_add=True)
    evaluador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('ejemplar', 'caracteristica', 'fecha_calificacion')

    def __str__(self):
        return f"{self.ejemplar} - {self.caracteristica.nombre}: {self.puntuacion_obtenida}"


# ... (modelos existentes)

class SensorData(models.Model):
    """ Almacena una lectura de sensor para un ejemplar en un momento dado. """
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='sensor_data')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    temperatura = models.FloatField(null=True, blank=True)
    actividad = models.FloatField(null=True, blank=True, help_text="Nivel de actividad o pasos")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.ejemplar.identificador} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Alert(models.Model):
    """ Almacena una alerta generada para un ejemplar. """
    class AlertType(models.TextChoices):
        FIEBRE = 'FIEBRE', 'Fiebre Alta'
        CELO = 'CELO', 'Posible Celo'
        INACTIVIDAD = 'INACTIVIDAD', 'Inactividad Anormal'

    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Alerta {self.alert_type} para {self.ejemplar.identificador}"
    