from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Ejemplar
from .serializers import EjemplarSerializer # Reutilizamos la lógica del score
import os
from django.conf import settings

@shared_task
def generate_ejemplar_report(ejemplar_id):
    """
    Tarea asíncrona para generar un reporte PDF de un ejemplar.
    """
    try:
        ejemplar = Ejemplar.objects.get(id=ejemplar_id)

        # Reutilizamos el serializer para obtener el score calculado
        serializer = EjemplarSerializer(instance=ejemplar)
        score_final = serializer.data.get('score_final', 'N/A')

        context = {'ejemplar': ejemplar, 'score_final': score_final}
        html_string = render_to_string('ganado/report_template.html', context)

        # Definir la ruta de salida del archivo
        output_folder = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, f'reporte_ejemplar_{ejemplar_id}.pdf')

        # Generar el PDF
        HTML(string=html_string).write_pdf(output_path)

        # Devolver la URL del archivo para que el frontend pueda acceder a él
        report_url = os.path.join(settings.MEDIA_URL, 'reports', f'reporte_ejemplar_{ejemplar_id}.pdf')
        return {'status': 'SUCCESS', 'report_url': report_url}
    except Exception as e:
        return {'status': 'FAILURE', 'error': str(e)}