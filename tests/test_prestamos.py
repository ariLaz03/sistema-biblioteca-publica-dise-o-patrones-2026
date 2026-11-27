from datetime import date, timedelta
import pytest
from biblioteca.errores import BibliotecaError, OperacionInvalida

HOY = date(2026, 11, 1)


def test_prestamo_y_estados(libro, prestamos, ana):
    assert libro.estado.nombre == "Disponible"
    p = prestamos.prestar(libro, ana, HOY)
    assert libro.estado.nombre == "Prestado"
    assert p.fecha_limite == HOY + timedelta(days=7)
    prestamos.devolver(p, HOY + timedelta(days=3))
    assert libro.estado.nombre == "Disponible" and not p.activo


def test_no_se_presta_dos_veces(libro, prestamos, ana, luis):
    prestamos.prestar(libro, ana, HOY)
    with pytest.raises(OperacionInvalida):
        prestamos.prestar(libro, luis, HOY)


def test_multa_por_retraso(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    multa = prestamos.devolver(p, HOY + timedelta(days=7 + 4))   # 4 días tarde
    assert multa == 4.00 and ana.deuda == 4.00 and p.total_a_pagar == 4.00


def test_sin_multa_a_tiempo(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    assert prestamos.devolver(p, HOY + timedelta(days=7)) == 0


def test_tope_de_multa(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    assert prestamos.devolver(p, HOY + timedelta(days=200)) == 30.00


def test_deuda_bloquea_nuevos_prestamos(cat, libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    prestamos.devolver(p, HOY + timedelta(days=10))
    with pytest.raises(BibliotecaError):
        prestamos.prestar(libro, ana, HOY)
    prestamos.pagar_multa(ana, ana.deuda)
    prestamos.prestar(libro, ana, HOY)


def test_no_devolver_dos_veces(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    prestamos.devolver(p, HOY)
    with pytest.raises(BibliotecaError):
        prestamos.devolver(p, HOY)


def test_limite_de_prestamos(cat, prestamos, ana):
    from biblioteca.libros import LibroFisicoCreator
    c = cat.categorias.obtener("Novela")
    libros = [LibroFisicoCreator().registrar(cat, str(i), f"L{i}", "X", c) for i in range(4)]
    for l in libros[:3]:
        prestamos.prestar(l, ana, HOY)
    with pytest.raises(BibliotecaError):
        prestamos.prestar(libros[3], ana, HOY)


def test_vencidos(libro, prestamos, ana):
    prestamos.prestar(libro, ana, HOY)
    assert prestamos.vencidos(HOY + timedelta(days=8))
    assert not prestamos.vencidos(HOY + timedelta(days=7))
