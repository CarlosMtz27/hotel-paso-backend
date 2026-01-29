from openpyxl import Workbook
from django.http import HttpResponse

from .services import reporte_turnos
from .serializers import ReporteTurnoSerializer


def exportar_turnos_excel(*, usuario, fecha_desde=None, fecha_hasta=None):
    """
    Genera un archivo Excel con el reporte de turnos.
    Reutiliza el servicio y el serializador para mantener la consistencia de los datos.
    """
    # 1. Obtener el queryset del servicio.
    turnos_qs = reporte_turnos(
        usuario=usuario,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Turnos"

    # 2. Serializar los datos para asegurar una estructura consistente.
    data = ReporteTurnoSerializer(turnos_qs, many=True).data

    headers = [
        "ID Turno",
        "Empleado",
        "Tipo",
        "Fecha Inicio",
        "Fecha Fin",
        "Caja Inicial",
        "Total Efectivo",
        "Total Transferencia",
        "Total Tarjeta",
        "Total Ingresos",
        "Sueldo",
        "Efectivo Esperado",
        "Efectivo Reportado",
        "Diferencia",
        "Sin Ingresos",
    ]

    ws.append(headers)

    # 3. Escribir los datos serializados en el archivo Excel.
    for item in data:
        ws.append([
            item["turno_id"],
            item["empleado"],
            item["tipo_turno"],
            item["fecha_inicio"],  # El serializador ya formatea la fecha.
            item["fecha_fin"],
            item["caja_inicial"],
            item["total_efectivo"],
            item["total_transferencia"],
            item["total_tarjeta"],
            item["total_ingresos"],
            item["sueldo"],
            item["efectivo_esperado"],
            item["efectivo_reportado"],
            item["diferencia"],
            item["sin_ingresos"],
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=reporte_turnos.xlsx"

    wb.save(response)
    return response
