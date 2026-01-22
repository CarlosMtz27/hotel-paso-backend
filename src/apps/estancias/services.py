from django.utils import timezone
from apps.estancias.models import Estancia
from apps.caja.models import MovimientoCaja
from apps.turnos.models import Turno


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
