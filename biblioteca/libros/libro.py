from __future__ import annotations
from typing import Optional

from ..prestamos.estados import Disponible, EstadoLibro
from ..reservas.observer import SujetoDisponibilidad
from .categorias import Categoria


class Libro(SujetoDisponibilidad):
    """Producto base. Es el Subject (Observer) y el Context (State)."""
    FORMATO = "Genérico"
    DIAS_PRESTAMO = 7
    MULTA_DIARIA = 1.0

    def __init__(self, isbn: str, titulo: str, autor: str,
                 categoria: Categoria, anio: Optional[int] = None) -> None:
        super().__init__()
        self.isbn, self.titulo, self.autor = isbn, titulo, autor
        self.categoria, self.anio = categoria, anio
        self.reservado_para = None
        self._estado: EstadoLibro = Disponible()

    # --- State
    @property
    def estado(self) -> EstadoLibro:
        return self._estado

    @property
    def disponible(self) -> bool:
        return isinstance(self._estado, Disponible)

    def _cambiar_estado(self, nuevo: EstadoLibro) -> None:
        self._estado = nuevo

    def prestar(self, usuario) -> None:
        self._estado.prestar(self, usuario)

    def devolver(self) -> None:
        self._estado.devolver(self)

    def apartar_para(self, usuario) -> None:
        self._estado.apartar(self, usuario)

    def liberar_reserva(self) -> None:
        self._estado.liberar(self)

    def marcar_vencido(self) -> None:
        self._estado.vencer(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.titulo!r}, {self._estado.nombre})"


class LibroFisico(Libro):
    FORMATO, DIAS_PRESTAMO, MULTA_DIARIA = "Físico", 7, 1.00

    def __init__(self, *args, ubicacion: str = "Sin asignar", **kw) -> None:
        super().__init__(*args, **kw)
        self.ubicacion = ubicacion


class LibroDigital(Libro):
    FORMATO, DIAS_PRESTAMO, MULTA_DIARIA = "Digital", 14, 0.50

    def __init__(self, *args, formato_archivo: str = "PDF", **kw) -> None:
        super().__init__(*args, **kw)
        self.formato_archivo = formato_archivo


class Audiolibro(Libro):
    FORMATO, DIAS_PRESTAMO, MULTA_DIARIA = "Audiolibro", 10, 0.75

    def __init__(self, *args, duracion_min: int = 0, **kw) -> None:
        super().__init__(*args, **kw)
        self.duracion_min = duracion_min
