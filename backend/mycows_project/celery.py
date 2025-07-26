import os
from celery import Celery

# Establecer el módulo de configuración de Django para el 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycows_project.settings')

app = Celery('mycows_project')

# Usar una cadena aquí significa que el worker no necesita serializar
# el objeto de configuración a los procesos hijos.
# - namespace='CELERY' significa que todas las claves de configuración de Celery
#   deben tener un prefijo `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar automáticamente los módulos de tareas de todas las apps registradas.
app.autodiscover_tasks()