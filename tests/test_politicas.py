"""Factory Method de políticas de préstamo según el tipo de usuario."""
from datetime import date, timedelta
import pytest
from biblioteca.errores import BibliotecaError
from biblioteca.libros import LibroFisicoCreator
from biblioteca.politicas import (PoliticaCreator, PoliticaDocente, PoliticaEstudiante,
                                  PoliticaExterno, PoliticaPrestamo, creador_politica_para,
                                  registrar_tipo, tipos_usuario)
from biblioteca.prestamos import ServicioPrestamos
from biblioteca.usuarios import Usuario

HOY = date(2026, 11, 1)


def test_factory_crea_la_politica_de_cada_tipo():
    assert isinstance(creador_politica_para("estudiante").crear_politica(), PoliticaEstudiante)
    assert isinstance(creador_politica_para("Docente").crear_politica(), PoliticaDocente)
    assert isinstance(creador_politica_para(" EXTERNO ").crear_politica(), PoliticaExterno)


def test_tipo_desconocido():
    with pytest.raises(BibliotecaError):
        creador_politica_para("alien")


def test_crear_usuario_asigna_politica():
    u = creador_politica_para("docente").crear_usuario("Marta")
    assert u.tipo == "Docente" and u.politica.max_prestamos == 6


def test_usuario_sin_politica_usa_la_estandar():
    u = Usuario("Pepe")
    assert type(u.politica) is PoliticaPrestamo and u.politica.max_prestamos == 3


def test_plazo_depende_del_tipo_de_usuario(libro):
    prest = ServicioPrestamos()
    est = creador_politica_para("estudiante").crear_usuario("E")
    ext = creador_politica_para("externo").crear_usuario("X")
    assert prest.prestar(libro, est, HOY).fecha_limite == HOY + timedelta(days=7 + 7)
    libro.devolver()
    assert prest.prestar(libro, ext, HOY).fecha_limite == HOY + timedelta(days=7)


def test_multa_depende_del_tipo_de_usuario(libro):
    prest = ServicioPrestamos()
    doc = creador_politica_para("docente").crear_usuario("D")
    p = prest.prestar(libro, doc, HOY)
    # plazo 7+14 = 21 días; 4 días tarde × 1.00 × 0.5 = 2.00
    assert prest.devolver(p, p.fecha_limite + timedelta(days=4)) == 2.00


def test_externo_paga_mas_multa(libro):
    prest = ServicioPrestamos()
    ext = creador_politica_para("externo").crear_usuario("X")
    p = prest.prestar(libro, ext, HOY)
    assert prest.devolver(p, p.fecha_limite + timedelta(days=4)) == 6.00   # 4 × 1.00 × 1.5


def test_limite_de_prestamos_segun_tipo(cat):
    prest = ServicioPrestamos()
    c = cat.categorias.obtener("Novela")
    libros = [LibroFisicoCreator().registrar(cat, str(i), f"L{i}", "X", c) for i in range(5)]
    ext = creador_politica_para("externo").crear_usuario("X")
    doc = creador_politica_para("docente").crear_usuario("D")
    prest.prestar(libros[0], ext, HOY); prest.prestar(libros[1], ext, HOY)
    with pytest.raises(BibliotecaError):                # externo: máximo 2
        prest.prestar(libros[2], ext, HOY)
    for l in libros[2:]:                                 # docente: hasta 6
        prest.prestar(l, doc, HOY)


def test_nuevo_tipo_sin_modificar_codigo_existente(libro):
    class PoliticaJubilado(PoliticaPrestamo):
        nombre, dias_adicionales, max_prestamos, factor_multa = "Jubilado", 21, 5, 0.0

    @registrar_tipo("jubilado")
    class JubiladoCreator(PoliticaCreator):
        def crear_politica(self):
            return PoliticaJubilado()

    assert "jubilado" in tipos_usuario()
    u = creador_politica_para("jubilado").crear_usuario("Abuelo")
    prest = ServicioPrestamos()
    p = prest.prestar(libro, u, HOY)
    assert p.fecha_limite == HOY + timedelta(days=7 + 21)
    assert prest.devolver(p, p.fecha_limite + timedelta(days=10)) == 0.0   # sin multa
