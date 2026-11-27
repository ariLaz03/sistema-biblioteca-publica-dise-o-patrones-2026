from __future__ import annotations
from typing import Callable, Optional


class Usuario:
    """Usuario de la biblioteca. Recibe notificaciones (destinatario del Observer)."""

    def __init__(self, nombre: str, canal: Optional[Callable[[str], None]] = None) -> None:
        self.nombre = nombre
        self.deuda = 0.0                 # multas pendientes
        self.bandeja: list[str] = []
        self._canal = canal              # consola, correo, etc.

    def recibir(self, mensaje: str) -> None:
        self.bandeja.append(mensaje)
        if self._canal:
            self._canal(f"[Notificación para {self.nombre}] {mensaje}")

    def __repr__(self) -> str:
        return f"Usuario({self.nombre!r})"
