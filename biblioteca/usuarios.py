from __future__ import annotations
from typing import Callable, Optional

from .politicas.modelos import PoliticaPrestamo


class Usuario:
    """Usuario de la biblioteca. Recibe notificaciones (destinatario del Observer)
    y tiene una política de préstamo según su tipo (Factory Method)."""

    def __init__(self, nombre: str, canal: Optional[Callable[[str], None]] = None,
                 politica: Optional[PoliticaPrestamo] = None) -> None:
        self.nombre = nombre
        self.politica = politica or PoliticaPrestamo()
        self.deuda = 0.0                 # multas pendientes
        self.bandeja: list[str] = []
        self._canal = canal              # consola, correo, etc.

    @property
    def tipo(self) -> str:
        return self.politica.nombre

    def recibir(self, mensaje: str) -> None:
        self.bandeja.append(mensaje)
        if self._canal:
            self._canal(f"[Notificación para {self.nombre}] {mensaje}")

    def __repr__(self) -> str:
        return f"Usuario({self.nombre!r}, {self.tipo})"
