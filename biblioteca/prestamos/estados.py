"""Patrón State (Integrante 2): estados de un libro."""
from __future__ import annotations
from abc import ABC

from ..errores import OperacionInvalida


class EstadoLibro(ABC):
    nombre = "Estado"

    def prestar(self, libro, usuario) -> None:
        raise OperacionInvalida(f"No se puede prestar un libro {self.nombre.lower()}")

    def devolver(self, libro) -> None:
        raise OperacionInvalida(f"No se puede devolver un libro {self.nombre.lower()}")

    def apartar(self, libro, usuario) -> None:
        raise OperacionInvalida(f"No se puede apartar un libro {self.nombre.lower()}")

    def liberar(self, libro) -> None:
        raise OperacionInvalida(f"No hay reserva que liberar en un libro {self.nombre.lower()}")

    def vencer(self, libro) -> None:
        raise OperacionInvalida(f"Solo un libro prestado puede vencer, no uno {self.nombre.lower()}")


class Disponible(EstadoLibro):
    nombre = "Disponible"

    def prestar(self, libro, usuario) -> None:
        libro._cambiar_estado(Prestado())

    def apartar(self, libro, usuario) -> None:
        libro.reservado_para = usuario
        libro._cambiar_estado(Reservado())


class Prestado(EstadoLibro):
    nombre = "Prestado"

    def devolver(self, libro) -> None:
        libro._cambiar_estado(Disponible())
        libro.notificar_disponible()          # Observer: avisa a quienes reservaron

    def vencer(self, libro) -> None:
        libro._cambiar_estado(Vencido())


class Vencido(EstadoLibro):
    """Libro prestado cuyo plazo ya expiró. Solo admite la devolución."""
    nombre = "Vencido"

    def devolver(self, libro) -> None:
        libro._cambiar_estado(Disponible())
        libro.notificar_disponible()


class Reservado(EstadoLibro):
    """Libro apartado para el usuario al que se notificó."""
    nombre = "Reservado"

    def prestar(self, libro, usuario) -> None:
        if usuario is not libro.reservado_para:
            raise OperacionInvalida("El libro está reservado para otro usuario")
        libro.reservado_para = None
        libro._cambiar_estado(Prestado())

    def liberar(self, libro) -> None:
        libro.reservado_para = None
        libro._cambiar_estado(Disponible())
        libro.notificar_disponible()
