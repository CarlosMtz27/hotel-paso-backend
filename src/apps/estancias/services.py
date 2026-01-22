from django.utils import timezone
from apps.estancias.models import Estancia
from apps.caja.models import MovimientoCaja
from apps.turnos.models import Turno
from apps.estancias.models import HoraExtra



def registrar_estancia(
    *,
    turno,
    habitacion,
    horas_base,
    precio_base,
    metodo_pago,
):
    if not turno.activo:
        raise ValueError("No hay turno activo")

    estancia = Estancia.objects.create(
        turno=turno,
        habitacion=habitacion,
        horas_base=horas_base,
        precio_base=precio_base,
        metodo_pago=metodo_pago,
    )

    # Movimiento de caja SOLO si es efectivo
    if metodo_pago == Estancia.MetodoPago.EFECTIVO:
        MovimientoCaja.objects.create(
            turno=turno,
            tipo="ESTANCIA",
            monto=precio_base,
            metodo_pago="EFECTIVO",
        )

    return estancia


def registrar_horas_extra(
    *,
    estancia,
    turno,
    cantidad_horas,
    precio_por_hora,
    metodo_pago,
):
    if not estancia.activa:
        raise ValueError("La estancia ya fue cerrada")

    precio_total = cantidad_horas * precio_por_hora

    hora_extra = HoraExtra.objects.create(
        estancia=estancia,
        turno=turno,
        cantidad_horas=cantidad_horas,
        precio_total=precio_total,
        metodo_pago=metodo_pago,
    )

    if metodo_pago == "EFECTIVO":
        MovimientoCaja.objects.create(
            turno=turno,
            tipo="EXTRA",
            monto=precio_total,
            metodo_pago="EFECTIVO",
        )

    return hora_extra
