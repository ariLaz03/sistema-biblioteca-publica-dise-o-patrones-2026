from __future__ import annotations
from datetime import date, timedelta
from typing import Callable, Optional

from ..servicios.decorators import DetallePrestamo, DetalleBasico


class Prestamo:
    def __init__(self, libro, usuario, fecha_prestamo: date) -> None:
        self.libro = libro
        self.usuario = usuario
        self.fecha_prestamo = fecha_prestamo
        self.detalle: DetallePrestamo = DetalleBasico()   # Decorator (Integrante 4)
        self.fecha_devolucion: Optional[date] = None
        self.multa = 0.0

    def agregar_servicio(self, decorador: Callable[[DetallePrestamo], DetallePrestamo]) -> None:
        self.detalle = decorador(self.detalle)

    @property
    def fecha_limite(self) -> date:
        return self.fecha_prestamo + timedelta(
            days=self.libro.DIAS_PRESTAMO
            + self.usuario.politica.dias_adicionales   # Factory Method: según tipo de usuario
            + self.detalle.dias_extra())               # Decorator: servicios adicionales

    @property
    def activo(self) -> bool:
        return self.fecha_devolucion is None

    @property
    def costo_servicios(self) -> float:
        return self.detalle.costo_adicional()

    @property
    def total_a_pagar(self) -> float:
        return round(self.multa + self.costo_servicios, 2)
