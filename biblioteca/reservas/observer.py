"""Patrón Observer (Integrante 3): Subject y Observer."""
from __future__ import annotations
from abc import ABC, abstractmethod


class Observador(ABC):
    @abstractmethod
    def actualizar(self, sujeto: "SujetoDisponibilidad") -> None: ...


class SujetoDisponibilidad:
    """Subject: lo hereda Libro. Avisa a sus observadores cuando queda disponible."""

    def __init__(self) -> None:
        self._observadores: list[Observador] = []

    def suscribir(self, obs: Observador) -> None:
        if obs not in self._observadores:
            self._observadores.append(obs)

    def desuscribir(self, obs: Observador) -> None:
        if obs in self._observadores:
            self._observadores.remove(obs)

    def notificar_disponible(self) -> None:
        for obs in list(self._observadores):
            obs.actualizar(self)
