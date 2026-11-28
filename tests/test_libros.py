import pytest
from biblioteca.errores import BibliotecaError
from biblioteca.libros import (AudiolibroCreator, Catalogo, LibroDigital,
                               LibroDigitalCreator, LibroFisico, creador_para)


def test_factory_method_crea_cada_tipo(cat):
    p = cat.categorias.obtener("Programación")
    assert isinstance(creador_para("fisico").crear_libro("1", "A", "X", p), LibroFisico)
    assert isinstance(LibroDigitalCreator().crear_libro("2", "B", "X", p, formato_archivo="EPUB"), LibroDigital)
    a = AudiolibroCreator().crear_libro("3", "C", "X", p, duracion_min=90)
    assert a.duracion_min == 90 and a.DIAS_PRESTAMO == 10


def test_factory_tipo_desconocido():
    with pytest.raises(BibliotecaError):
        creador_para("holograma")


def test_registrar_y_buscar(cat, libro):
    LibroDigitalCreator().registrar(cat, "222", "Dune", "Frank Herbert", cat.categorias.obtener("Novela"))
    assert len(cat.listar()) == 2
    assert [l.isbn for l in cat.buscar(titulo="clean")] == ["111"]
    assert [l.isbn for l in cat.buscar(autor="herbert")] == ["222"]
    assert [l.isbn for l in cat.buscar(categoria="novela")] == ["222"]
    assert cat.obtener("111") is libro


def test_isbn_duplicado_y_categoria_no_registrada(cat, libro):
    with pytest.raises(BibliotecaError):
        LibroDigitalCreator().registrar(cat, "111", "Otro", "Y", libro.categoria)
    otra = Catalogo().categorias.crear("Externa")
    with pytest.raises(BibliotecaError):
        LibroDigitalCreator().registrar(cat, "999", "Z", "Y", otra)


def test_categorias(cat, libro):
    with pytest.raises(BibliotecaError):
        cat.categorias.crear("novela")            # duplicada (sin distinguir mayúsculas)
    with pytest.raises(BibliotecaError):
        cat.categorias.eliminar("Programación", cat)   # tiene libros
    cat.categorias.eliminar("Novela", cat)
    assert [c.nombre for c in cat.categorias.listar()] == ["Programación"]


def test_no_elimina_libro_prestado(cat, libro, prestamos, ana):
    prestamos.prestar(libro, ana)
    with pytest.raises(BibliotecaError):
        cat.eliminar("111")
