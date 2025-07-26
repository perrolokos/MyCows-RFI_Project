from rest_framework import serializers
# Asegúrate de que SensorData y Alert están incluidos en esta importación
from .models import (
    Raza, CategoriaPuntuacion, Caracteristica, Ejemplar, Calificacion,
    SensorData, Alert
)

class RazaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raza
        fields = '__all__'

class CaracteristicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caracteristica
        fields = '__all__'

class CategoriaPuntuacionSerializer(serializers.ModelSerializer):
    caracteristicas = CaracteristicaSerializer(many=True, read_only=True)

    class Meta:
        model = CategoriaPuntuacion
        fields = ['id', 'nombre', 'ponderacion', 'puntaje_ideal_total', 'caracteristicas']


class CalificacionSerializer(serializers.ModelSerializer):
    evaluador = serializers.StringRelatedField(read_only=True)
    caracteristica_nombre = serializers.CharField(source='caracteristica.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='caracteristica.categoria.nombre', read_only=True)

    class Meta:
        model = Calificacion
        fields = [
            'id', 'ejemplar', 'caracteristica', 'puntuacion_obtenida',
            'fecha_calificacion', 'evaluador', 'caracteristica_nombre', 'categoria_nombre'
        ]
        read_only_fields = ('evaluador', 'fecha_calificacion')


class EjemplarSerializer(serializers.ModelSerializer):
    raza_nombre = serializers.CharField(source='raza.nombre', read_only=True)
    raza = serializers.PrimaryKeyRelatedField(queryset=Raza.objects.all(), write_only=True)
    calificaciones = CalificacionSerializer(many=True, read_only=True)
    # Relación anidada para alertas (de solo lectura)
    alerts = serializers.StringRelatedField(many=True, read_only=True)
    score_final = serializers.SerializerMethodField()

    class Meta:
        model = Ejemplar
        fields = [
            'id', 'identificador', 'nombre',
            'raza', 'raza_nombre',
            'fecha_nacimiento', 'peso_actual', 'talla_actual',
            'score_final', 'calificaciones', 'alerts'
        ]

    def get_score_final(self, obj):
        ultima_calificacion = obj.calificaciones.order_by('-fecha_calificacion').first()
        if not ultima_calificacion:
            return 0.0
        
        ultima_fecha = ultima_calificacion.fecha_calificacion
        calificaciones_sesion = obj.calificaciones.filter(fecha_calificacion=ultima_fecha)
        
        puntos_por_categoria = {}
        for cal in calificaciones_sesion:
            cat_id = cal.caracteristica.categoria.id
            if cat_id not in puntos_por_categoria:
                puntos_por_categoria[cat_id] = {
                    'puntos_obtenidos': 0,
                    'categoria_obj': cal.caracteristica.categoria
                }
            puntos_por_categoria[cat_id]['puntos_obtenidos'] += cal.puntuacion_obtenida
        
        score_final_calculado = 0.0
        for cat_id, data in puntos_por_categoria.items():
            categoria = data['categoria_obj']
            puntos_obtenidos = data['puntos_obtenidos']
            
            if categoria.puntaje_ideal_total > 0:
                score_categoria = (puntos_obtenidos / categoria.puntaje_ideal_total) * categoria.ponderacion
                score_final_calculado += score_categoria

        return round(score_final_calculado, 2)

# --- Serializadores añadidos en el Sprint 4 ---

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['timestamp', 'temperatura', 'actividad']

class AlertSerializer(serializers.ModelSerializer):
    ejemplar_nombre = serializers.CharField(source='ejemplar.nombre', read_only=True)
    ejemplar_identificador = serializers.CharField(source='ejemplar.identificador', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'