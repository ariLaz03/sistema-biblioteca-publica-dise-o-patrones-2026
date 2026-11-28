import pytest
from biblioteca.colecciones import Coleccion
from biblioteca.errores import BibliotecaError
from biblioteca.libros import LibroFisicoCreator


def armar(cat):
    c = cat.categorias.obtener("Programación")
    mk = lambda i, t, a: LibroFisicoCreator().registrar(cat, i, t, a, c)
    raiz = Coleccion("Biblioteca")
    tec, py = Coleccion("Tecnología"), Coleccion("Python")
    raiz.agregar(tec); tec.agregar(py)
    py.agregar_libro(mk("1", "Fluent Python", "Luciano Ramalho"))
    tec.agregar_libro(mk("2", "Clean Code", "Robert Martin"))
    raiz.agregar_libro(mk("3", "Dune", "Frank Herbert"))
    return raiz, tec, py


def test_conteo_recursivo(cat):
    raiz, tec, py = armar(cat)
    assert (raiz.contar_libros(), tec.contar_libros(), py.contar_libros()) == (3, 2, 1)


def test_busqueda_y_subcoleccion(cat):
    raiz, tec, py = armar(cat)
    assert [l.titulo for l in raiz.buscar("martin")] == ["Clean Code"]
    assert raiz.buscar_coleccion("python") is py


def test_no_permite_ciclos(cat):
    raiz, tec, py = armar(cat)
    with pytest.raises(BibliotecaError):
        py.agregar(raiz)
    with pytest.raises(BibliotecaError):
        tec.agregar(tec)


def test_mover_componente_cambia_de_padre(cat):
    raiz, tec, py = armar(cat)
    raiz.agregar(py)                       # mueve Python de Tecnología a la raíz
    assert py.padre is raiz and tec.contar_libros() == 1


def test_mostrar_arbol(cat):
    raiz, *_ = armar(cat)
    texto = raiz.mostrar()
    assert "[Biblioteca] (3 libros)" in texto and "  [Tecnología]" in texto
    assert "- Fluent Python (Disponible)" in texto
