"""Reservas y notificaciones (Integrante 3)."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..errores import BibliotecaError
from ..usuarios import Usuario
from .observer import Observador, SujetoDisponibilidad


class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    NOTIFICADA = "Notificada"   # libro apartado esperando al usuario
    CUMPLIDA = "Cumplida"       # el usuario retiró el libro
    CANCELADA = "Cancelada"
    VENCIDA = "Vencida"         # no retiró el libro a tiempo


@dataclass
class Reserva:
    usuario: Usuario
    libro: "object"
    fecha: datetime = field(default_factory=datetime.now)
    estado: EstadoReserva = EstadoReserva.PENDIENTE

    @property
    def activa(self) -> bool:
        return self.estado in (EstadoReserva.PENDIENTE, EstadoReserva.NOTIFICADA)


class ObservadorReservas(Observador):
    """Observer concreto: cuando el libro queda disponible atiende la cola."""

    def __init__(self, servicio: "ServicioReservas") -> None:
        self._servicio = servicio

    def actualizar(self, libro: SujetoDisponibilidad) -> None:
        self._servicio.atender_disponibilidad(libro)


class ServicioReservas:
    def __init__(self) -> None:
        self._colas: dict[int, list[Reserva]] = {}
        self._observador = ObservadorReservas(self)

    # ---- casos de uso
    def reservar(self, usuario: Usuario, libro) -> Reserva:
        if libro.disponible:
            raise BibliotecaError("El libro está disponible: no requiere reserva")
        cola = self._colas.setdefault(id(libro), [])
        if any(r.usuario is usuario and r.activa for r in cola):
            raise BibliotecaError("El usuario ya tiene una reserva activa de este libro")
        reserva = Reserva(usuario, libro)
        cola.append(reserva)
        libro.suscribir(self._observador)
        return reserva

    def cancelar(self, reserva: Reserva) -> None:
        self._cerrar(reserva, EstadoReserva.CANCELADA)

    def vencer(self, reserva: Reserva) -> None:
        """El usuario no retiró el libro apartado: pasa al siguiente de la cola."""
        self._cerrar(reserva, EstadoReserva.VENCIDA)

    def marcar_cumplida(self, libro, usuario: Usuario) -> None:
        for r in self._colas.get(id(libro), []):
            if r.usuario is usuario and r.estado == EstadoReserva.NOTIFICADA:
                r.estado = EstadoReserva.CUMPLIDA

    def pendientes(self, libro) -> list[Reserva]:
        return [r for r in self._colas.get(id(libro), [])
                if r.estado == EstadoReserva.PENDIENTE]

    # ---- Observer
    def atender_disponibilidad(self, libro) -> None:
        pendientes = self.pendientes(libro)
        if not pendientes:
            libro.desuscribir(self._observador)
            return
        primera = pendientes[0]                      # FIFO
        primera.estado = EstadoReserva.NOTIFICADA
        libro.apartar_para(primera.usuario)          # State: Disponible -> Reservado
        primera.usuario.recibir(f"El libro «{libro.titulo}» ya está disponible para ti.")
        if len(pendientes) == 1:
            libro.desuscribir(self._observador)

    def _cerrar(self, reserva: Reserva, nuevo: EstadoReserva) -> None:
        if not reserva.activa:
            raise BibliotecaError("La reserva ya no está activa")
        estaba_notificada = reserva.estado == EstadoReserva.NOTIFICADA
        reserva.estado = nuevo
        if estaba_notificada:
            reserva.libro.liberar_reserva()  # vuelve a Disponible y avisa al siguiente
