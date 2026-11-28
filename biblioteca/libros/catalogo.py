from __future__ import annotations
from typing import Optional

from ..errores import BibliotecaError
from .categorias import GestorCategorias
from .libro import Libro


class Catalogo:
    def __init__(self, categorias: Optional[GestorCategorias] = None) -> None:
        self.categorias = categorias or GestorCategorias()
        self._libros: dict[str, Libro] = {}

    def agregar(self, libro: Libro) -> None:
        if not libro.isbn or not libro.titulo:
            raise BibliotecaError("ISBN y título son obligatorios")
        if libro.isbn in self._libros:
            raise BibliotecaError(f"Ya existe un libro con ISBN {libro.isbn}")
        if not self.categorias.existe(libro.categoria):
            raise BibliotecaError("La categoría del libro no está registrada")
        self._libros[libro.isbn] = libro

    def obtener(self, isbn: str) -> Libro:
        try:
            return self._libros[isbn]
        except KeyError:
            raise BibliotecaError(f"No existe el libro con ISBN {isbn}") from None

    def eliminar(self, isbn: str) -> None:
        libro = self.obtener(isbn)
        if not libro.disponible:
            raise BibliotecaError("No se puede eliminar un libro prestado o reservado")
        del self._libros[isbn]

    def buscar(self, titulo: str = "", autor: str = "", categoria: str = "",
               isbn: str = "") -> list[Libro]:
        def ok(campo: str, texto: str) -> bool:
            return texto.lower() in (campo or "").lower()
        return [l for l in self.listar()
                if ok(l.titulo, titulo) and ok(l.autor, autor)
                and ok(l.categoria.nombre, categoria) and ok(l.isbn, isbn)]

    def listar(self, orden: str = "titulo") -> list[Libro]:
        return sorted(self._libros.values(), key=lambda l: str(getattr(l, orden)).lower())

    def disponibles(self) -> list[Libro]:
        return [l for l in self.listar() if l.disponible]
