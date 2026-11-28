"""Patrón Decorator (Integrante 4): servicios adicionales en los préstamos."""
from __future__ import annotations
from abc import ABC, abstractmethod


class DetallePrestamo(ABC):
    @abstractmethod
    def descripcion(self) -> str: ...
    @abstractmethod
    def costo_adicional(self) -> float: ...
    @abstractmethod
    def dias_extra(self) -> int: ...


class DetalleBasico(DetallePrestamo):
    def descripcion(self) -> str:
        return "Préstamo estándar"

    def costo_adicional(self) -> float:
        return 0.0

    def dias_extra(self) -> int:
        return 0


class ServicioAdicional(DetallePrestamo):
    """Decorator base: envuelve otro detalle y delega."""
    NOMBRE = "Servicio"
    COSTO = 0.0
    DIAS = 0

    def __init__(self, interno: DetallePrestamo) -> None:
        self._interno = interno

    def descripcion(self) -> str:
        return f"{self._interno.descripcion()} + {self.NOMBRE}"

    def costo_adicional(self) -> float:
        return self._interno.costo_adicional() + self.COSTO

    def dias_extra(self) -> int:
        return self._interno.dias_extra() + self.DIAS


class RenovacionPrioritaria(ServicioAdicional):
    NOMBRE, COSTO, DIAS = "Renovación prioritaria (+7 días)", 2.0, 7


class EntregaDomicilio(ServicioAdicional):
    NOMBRE, COSTO = "Entrega a domicilio", 5.0


class SeguroDanio(ServicioAdicional):
    NOMBRE, COSTO = "Seguro contra daños", 3.0
