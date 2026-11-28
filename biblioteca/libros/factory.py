"""Patrón Factory Method (Integrante 1)."""
from __future__ import annotations
from abc import ABC, abstractmethod

from ..errores import BibliotecaError
from .libro import Audiolibro, Libro, LibroDigital, LibroFisico


class LibroCreator(ABC):
    """Creator: define el factory method `crear_libro` y la operación común `registrar`."""

    @abstractmethod
    def crear_libro(self, isbn, titulo, autor, categoria, anio=None, **extra) -> Libro: ...

    def registrar(self, catalogo, isbn, titulo, autor, categoria, anio=None, **extra) -> Libro:
        libro = self.crear_libro(isbn, titulo, autor, categoria, anio, **extra)
        catalogo.agregar(libro)
        return libro


class LibroFisicoCreator(LibroCreator):
    def crear_libro(self, isbn, titulo, autor, categoria, anio=None, **extra) -> Libro:
        return LibroFisico(isbn, titulo, autor, categoria, anio, **extra)


class LibroDigitalCreator(LibroCreator):
    def crear_libro(self, isbn, titulo, autor, categoria, anio=None, **extra) -> Libro:
        return LibroDigital(isbn, titulo, autor, categoria, anio, **extra)


class AudiolibroCreator(LibroCreator):
    def crear_libro(self, isbn, titulo, autor, categoria, anio=None, **extra) -> Libro:
        return Audiolibro(isbn, titulo, autor, categoria, anio, **extra)


_CREADORES = {"fisico": LibroFisicoCreator, "digital": LibroDigitalCreator,
              "audiolibro": AudiolibroCreator}


def creador_para(tipo: str) -> LibroCreator:
    try:
        return _CREADORES[tipo.strip().lower()]()
    except KeyError:
        raise BibliotecaError(f"Tipo de libro desconocido: {tipo}") from None
