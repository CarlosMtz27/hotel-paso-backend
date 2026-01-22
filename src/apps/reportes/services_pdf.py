from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from io import BytesIO
from .services import reporte_turnos


def generar_pdf_turnos(fecha_desde=None, fecha_hasta=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    data = reporte_turnos(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )

    tabla = [
        [
            "ID",
            "Empleado",
            "Turno",
            "Inicio",
            "Fin",
            "Caja Inicial",
            "Efectivo",
            "Transferencia",
            "Tarjeta",
            "Ingresos",
            "Sueldo",
            "Esperado",
            "Reportado",
            "Diferencia",
        ]
    ]

    for item in data:
        tabla.append([
            item["turno_id"],
            item["empleado"],
            item["tipo_turno"],
            item["fecha_inicio"].strftime("%Y-%m-%d %H:%M") if item["fecha_inicio"] else "",
            item["fecha_fin"].strftime("%Y-%m-%d %H:%M") if item["fecha_fin"] else "",
            f"${item['caja_inicial']}",
            f"${item['total_efectivo']}",
            f"${item['total_transferencia']}",
            f"${item['total_tarjeta']}",
            f"${item['total_ingresos']}",
            f"${item['sueldo']}",
            f"${item['efectivo_esperado']}",
            f"${item['efectivo_reportado']}",
            f"${item['diferencia']}",
        ])

    table = Table(tabla, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))

    doc.build([table])

    buffer.seek(0)
    return buffer
