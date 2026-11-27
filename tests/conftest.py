import pytest
from biblioteca.libros import Catalogo, LibroFisicoCreator, LibroDigitalCreator
from biblioteca.prestamos import ServicioPrestamos
from biblioteca.reservas import ServicioReservas
from biblioteca.usuarios import Usuario


@pytest.fixture
def cat():
    c = Catalogo()
    c.categorias.crear("Programación")
    c.categorias.crear("Novela")
    return c


@pytest.fixture
def libro(cat):
    return LibroFisicoCreator().registrar(
        cat, "111", "Clean Code", "Robert Martin", cat.categorias.obtener("Programación"), 2008)


@pytest.fixture
def reservas():
    return ServicioReservas()


@pytest.fixture
def prestamos(reservas):
    return ServicioPrestamos(reservas=reservas)


@pytest.fixture
def ana():
    return Usuario("Ana")


@pytest.fixture
def luis():
    return Usuario("Luis")
