from __future__ import annotations
from datetime import date


class CalculadoraMulta:
    """Multa = días de retraso × tarifa del tipo de libro × factor de la política
    del usuario (con tope de días)."""

    def __init__(self, tope_dias: int = 30) -> None:
        self.tope_dias = tope_dias

    def calcular(self, prestamo, fecha_devolucion: date) -> float:
        retraso = max(0, (fecha_devolucion - prestamo.fecha_limite).days)
        tarifa = prestamo.libro.MULTA_DIARIA * prestamo.usuario.politica.factor_multa
        return round(min(retraso, self.tope_dias) * tarifa, 2)
