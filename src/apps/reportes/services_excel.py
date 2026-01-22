from openpyxl import Workbook
from django.http import HttpResponse

from .services import reporte_turnos


def quitar_timezone(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=None)


def exportar_turnos_excel(*, usuario, fecha_desde=None, fecha_hasta=None):

    data = reporte_turnos(
        usuario=usuario,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Turnos"

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

    for item in data:
        ws.append([
            item["turno_id"],
            item["empleado"],
            item["tipo_turno"],
            quitar_timezone(item["fecha_inicio"]),
            quitar_timezone(item["fecha_fin"]),
            float(item["caja_inicial"]),
            float(item["total_efectivo"]),
            float(item["total_transferencia"]),
            float(item["total_tarjeta"]),
            float(item["total_ingresos"]),
            float(item["sueldo"]),
            float(item["efectivo_esperado"] or 0),
            float(item["efectivo_reportado"] or 0),
            float(item["diferencia"] or 0),
            item["sin_ingresos"],
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=reporte_turnos.xlsx"

    wb.save(response)
    return response
