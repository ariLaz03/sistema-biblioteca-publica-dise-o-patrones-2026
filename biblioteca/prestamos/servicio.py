from __future__ import annotations
from datetime import date
from typing import Callable, Iterable, Optional

from ..errores import BibliotecaError
from ..usuarios import Usuario
from .multas import CalculadoraMulta
from .prestamo import Prestamo


class ServicioPrestamos:
    def __init__(self, calculadora: Optional[CalculadoraMulta] = None,
                 reservas=None, max_por_usuario: int = 3) -> None:
        self.calculadora = calculadora or CalculadoraMulta()
        self.reservas = reservas
        self.max_por_usuario = max_por_usuario
        self.historial: list[Prestamo] = []

    def prestar(self, libro, usuario: Usuario, hoy: Optional[date] = None,
                servicios: Iterable[Callable] = ()) -> Prestamo:
        hoy = hoy or date.today()
        if usuario.deuda > 0:
            raise BibliotecaError(f"{usuario.nombre} tiene multas pendientes: {usuario.deuda:.2f}")
        if len(self.activos(usuario)) >= self.max_por_usuario:
            raise BibliotecaError(f"Máximo de {self.max_por_usuario} préstamos activos")
        libro.prestar(usuario)                         # State valida la operación
        prestamo = Prestamo(libro, usuario, hoy)
        for servicio in servicios:                     # Decorator
            prestamo.agregar_servicio(servicio)
        self.historial.append(prestamo)
        if self.reservas:
            self.reservas.marcar_cumplida(libro, usuario)
        return prestamo

    def devolver(self, prestamo: Prestamo, hoy: Optional[date] = None) -> float:
        if not prestamo.activo:
            raise BibliotecaError("El préstamo ya fue devuelto")
        hoy = hoy or date.today()
        prestamo.fecha_devolucion = hoy
        prestamo.multa = self.calculadora.calcular(prestamo, hoy)
        prestamo.usuario.deuda += prestamo.multa
        prestamo.libro.devolver()                      # State + Observer
        return prestamo.multa

    def pagar_multa(self, usuario: Usuario, monto: float) -> None:
        usuario.deuda = round(max(0.0, usuario.deuda - monto), 2)

    def activos(self, usuario: Optional[Usuario] = None) -> list[Prestamo]:
        return [p for p in self.historial
                if p.activo and (usuario is None or p.usuario is usuario)]

    def vencidos(self, hoy: Optional[date] = None) -> list[Prestamo]:
        hoy = hoy or date.today()
        return [p for p in self.activos() if p.fecha_limite < hoy]
