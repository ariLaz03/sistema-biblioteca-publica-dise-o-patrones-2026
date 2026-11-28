"""Productos del Factory Method: políticas de préstamo según el tipo de usuario."""
from __future__ import annotations


class PoliticaPrestamo:
    """Política por defecto (estándar). Las subclases cambian los valores."""
    nombre = "Estándar"
    dias_adicionales = 0      # días que se suman al plazo del libro
    max_prestamos = 3         # préstamos activos permitidos
    factor_multa = 1.0        # multiplica la tarifa diaria de multa

    def resumen(self) -> str:
        return (f"+{self.dias_adicionales} días · máx {self.max_prestamos} libros"
                f" · multa ×{self.factor_multa:g}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.resumen()})"


class PoliticaEstudiante(PoliticaPrestamo):
    nombre = "Estudiante"
    dias_adicionales = 7
    max_prestamos = 4
    factor_multa = 1.0


class PoliticaDocente(PoliticaPrestamo):
    nombre = "Docente"
    dias_adicionales = 14
    max_prestamos = 6
    factor_multa = 0.5


class PoliticaExterno(PoliticaPrestamo):
    nombre = "Externo"
    dias_adicionales = 0
    max_prestamos = 2
    factor_multa = 1.5
