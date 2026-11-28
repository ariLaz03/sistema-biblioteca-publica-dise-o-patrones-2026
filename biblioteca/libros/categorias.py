from __future__ import annotations
from dataclasses import dataclass

from ..errores import BibliotecaError


@dataclass(frozen=True)
class Categoria:
    nombre: str
    descripcion: str = ""


class GestorCategorias:
    def __init__(self) -> None:
        self._categorias: dict[str, Categoria] = {}

    def crear(self, nombre: str, descripcion: str = "") -> Categoria:
        clave = nombre.strip().lower()
        if not clave:
            raise BibliotecaError("El nombre de la categoría es obligatorio")
        if clave in self._categorias:
            raise BibliotecaError(f"La categoría «{nombre}» ya existe")
        cat = Categoria(nombre.strip(), descripcion)
        self._categorias[clave] = cat
        return cat

    def obtener(self, nombre: str) -> Categoria:
        try:
            return self._categorias[nombre.strip().lower()]
        except KeyError:
            raise BibliotecaError(f"La categoría «{nombre}» no existe") from None

    def existe(self, categoria: Categoria) -> bool:
        return self._categorias.get(categoria.nombre.lower()) == categoria

    def listar(self) -> list[Categoria]:
        return sorted(self._categorias.values(), key=lambda c: c.nombre.lower())

    def eliminar(self, nombre: str, catalogo=None) -> None:
        cat = self.obtener(nombre)
        if catalogo and catalogo.buscar(categoria=cat.nombre):
            raise BibliotecaError("No se puede eliminar: hay libros en esa categoría")
        del self._categorias[cat.nombre.lower()]
