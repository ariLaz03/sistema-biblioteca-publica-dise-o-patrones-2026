from __future__ import annotations
from datetime import date


class CalculadoraMulta:
    """Multa = días de retraso × tarifa diaria del tipo de libro (con tope de días)."""

    def __init__(self, tope_dias: int = 30) -> None:
        self.tope_dias = tope_dias

    def calcular(self, prestamo, fecha_devolucion: date) -> float:
        retraso = max(0, (fecha_devolucion - prestamo.fecha_limite).days)
        return round(min(retraso, self.tope_dias) * prestamo.libro.MULTA_DIARIA, 2)
