"""Patrón Factory Method: políticas de préstamo según el tipo de usuario.

Para agregar un nuevo tipo de usuario basta con definir una política y un
creador con @registrar_tipo; no se modifica ningún código existente.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Optional, Type

from ..errores import BibliotecaError
from .modelos import (PoliticaDocente, PoliticaEstudiante, PoliticaExterno,
                      PoliticaPrestamo)


class PoliticaCreator(ABC):
    """Creator: el factory method `crear_politica` lo implementa cada subclase."""

    @abstractmethod
    def crear_politica(self) -> PoliticaPrestamo: ...

    def crear_usuario(self, nombre: str, canal: Optional[Callable[[str], None]] = None):
        """Operación común: crea un usuario con la política de este creador."""
        from ..usuarios import Usuario          # import local: evita ciclo de módulos
        return Usuario(nombre, canal, politica=self.crear_politica())


_REGISTRO: dict[str, Type[PoliticaCreator]] = {}


def registrar_tipo(nombre: str):
    """Decorador que registra un creador bajo el nombre de un tipo de usuario."""
    def decorador(cls: Type[PoliticaCreator]) -> Type[PoliticaCreator]:
        _REGISTRO[nombre.strip().lower()] = cls
        return cls
    return decorador


@registrar_tipo("estudiante")
class EstudianteCreator(PoliticaCreator):
    def crear_politica(self) -> PoliticaPrestamo:
        return PoliticaEstudiante()


@registrar_tipo("docente")
class DocenteCreator(PoliticaCreator):
    def crear_politica(self) -> PoliticaPrestamo:
        return PoliticaDocente()


@registrar_tipo("externo")
class ExternoCreator(PoliticaCreator):
    def crear_politica(self) -> PoliticaPrestamo:
        return PoliticaExterno()


def creador_politica_para(tipo: str) -> PoliticaCreator:
    try:
        return _REGISTRO[tipo.strip().lower()]()
    except KeyError:
        raise BibliotecaError(f"Tipo de usuario desconocido: {tipo}") from None


def tipos_usuario() -> list[str]:
    return sorted(_REGISTRO)
