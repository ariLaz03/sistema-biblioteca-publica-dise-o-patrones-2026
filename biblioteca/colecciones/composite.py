"""Patrón Composite (Integrante 4): colecciones y subcolecciones."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from ..errores import BibliotecaError


class ComponenteColeccion(ABC):
    def __init__(self, nombre: str) -> None:
        self.nombre = nombre
        self.padre: Optional["Coleccion"] = None

    @abstractmethod
    def listar_libros(self) -> list: ...

    @abstractmethod
    def mostrar(self, nivel: int = 0) -> str: ...

    def contar_libros(self) -> int:
        return len(self.listar_libros())

    def buscar(self, texto: str) -> list:
        t = texto.lower()
        return [l for l in self.listar_libros()
                if t in l.titulo.lower() or t in l.autor.lower()]


class LibroHoja(ComponenteColeccion):
    """Leaf: envuelve un Libro del catálogo."""

    def __init__(self, libro) -> None:
        super().__init__(libro.titulo)
        self.libro = libro

    def listar_libros(self) -> list:
        return [self.libro]

    def mostrar(self, nivel: int = 0) -> str:
        return f"{'  ' * nivel}- {self.libro.titulo} ({self.libro.estado.nombre})"


class Coleccion(ComponenteColeccion):
    """Composite: contiene libros y otras colecciones."""

    def __init__(self, nombre: str) -> None:
        super().__init__(nombre)
        self._hijos: list[ComponenteColeccion] = []

    def agregar(self, componente: ComponenteColeccion) -> ComponenteColeccion:
        if isinstance(componente, Coleccion) and self._forma_ciclo(componente):
            raise BibliotecaError("Una colección no puede contenerse a sí misma")
        if componente.padre is not None:
            componente.padre.quitar(componente)
        componente.padre = self
        self._hijos.append(componente)
        return componente

    def agregar_libro(self, libro) -> LibroHoja:
        return self.agregar(LibroHoja(libro))

    def quitar(self, componente: ComponenteColeccion) -> None:
        self._hijos.remove(componente)
        componente.padre = None

    def _forma_ciclo(self, nueva: "Coleccion") -> bool:
        nodo: Optional[Coleccion] = self
        while nodo is not None:
            if nodo is nueva:
                return True
            nodo = nodo.padre
        return False

    @property
    def subcolecciones(self) -> list["Coleccion"]:
        return [h for h in self._hijos if isinstance(h, Coleccion)]

    def listar_libros(self) -> list:
        libros: list = []
        for h in self._hijos:
            libros.extend(h.listar_libros())
        return libros

    def buscar_coleccion(self, nombre: str) -> Optional["Coleccion"]:
        if self.nombre.lower() == nombre.lower():
            return self
        for sub in self.subcolecciones:
            encontrada = sub.buscar_coleccion(nombre)
            if encontrada:
                return encontrada
        return None

    def mostrar(self, nivel: int = 0) -> str:
        lineas = [f"{'  ' * nivel}[{self.nombre}] ({self.contar_libros()} libros)"]
        lineas += [h.mostrar(nivel + 1) for h in self._hijos]
        return "\n".join(lineas)
