"""Estado Vencido (State) y su integración con Observer."""
from datetime import date, timedelta
import pytest
from biblioteca.errores import OperacionInvalida
from biblioteca.prestamos import Vencido

HOY = date(2026, 11, 1)


def test_libro_prestado_pasa_a_vencido(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    nuevos = prestamos.actualizar_vencidos(HOY + timedelta(days=8))
    assert nuevos == [p] and isinstance(libro.estado, Vencido) and not libro.disponible


def test_no_vence_antes_del_limite(libro, prestamos, ana):
    prestamos.prestar(libro, ana, HOY)
    assert prestamos.actualizar_vencidos(HOY + timedelta(days=7)) == []
    assert libro.estado.nombre == "Prestado"


def test_vencido_avisa_al_usuario(libro, prestamos, ana):
    prestamos.prestar(libro, ana, HOY)
    prestamos.actualizar_vencidos(HOY + timedelta(days=9))
    assert "venció" in ana.bandeja[0] and "Clean Code" in ana.bandeja[0]


def test_actualizar_es_idempotente(libro, prestamos, ana):
    prestamos.prestar(libro, ana, HOY)
    prestamos.actualizar_vencidos(HOY + timedelta(days=9))
    assert prestamos.actualizar_vencidos(HOY + timedelta(days=10)) == []
    assert len(ana.bandeja) == 1


def test_vencido_no_se_puede_prestar_ni_apartar(libro, prestamos, ana, luis):
    prestamos.prestar(libro, ana, HOY)
    prestamos.actualizar_vencidos(HOY + timedelta(days=9))
    with pytest.raises(OperacionInvalida):
        libro.prestar(luis)
    with pytest.raises(OperacionInvalida):
        libro.apartar_para(luis)


def test_disponible_no_puede_vencer(libro):
    with pytest.raises(OperacionInvalida):
        libro.marcar_vencido()


def test_devolver_vencido_cobra_multa_y_queda_disponible(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    prestamos.actualizar_vencidos(HOY + timedelta(days=10))
    multa = prestamos.devolver(p, HOY + timedelta(days=10))      # 3 días tarde
    assert multa == 3.00 and libro.disponible


def test_vencido_se_puede_reservar_y_notifica_al_devolver(libro, prestamos, reservas, ana, luis):
    p = prestamos.prestar(libro, ana, HOY)
    prestamos.actualizar_vencidos(HOY + timedelta(days=10))
    r = reservas.reservar(luis, libro)
    prestamos.devolver(p, HOY + timedelta(days=10))
    assert r.estado.value == "Notificada" and libro.estado.nombre == "Reservado"
    assert any("disponible" in m for m in luis.bandeja)
