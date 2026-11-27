import pytest
from biblioteca.errores import BibliotecaError, OperacionInvalida
from biblioteca.reservas import EstadoReserva


def test_notifica_y_aparta_al_devolver(libro, prestamos, reservas, ana, luis):
    p = prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    prestamos.devolver(p)
    assert r.estado == EstadoReserva.NOTIFICADA
    assert libro.estado.nombre == "Reservado" and len(luis.bandeja) == 1


def test_orden_fifo(libro, prestamos, reservas, ana, luis):
    from biblioteca.usuarios import Usuario
    eva = Usuario("Eva")
    p = prestamos.prestar(libro, ana)
    rl, re_ = reservas.reservar(luis, libro), reservas.reservar(eva, libro)
    prestamos.devolver(p)
    assert rl.estado == EstadoReserva.NOTIFICADA and re_.estado == EstadoReserva.PENDIENTE
    assert eva.bandeja == []


def test_libro_apartado_solo_lo_presta_quien_reservo(libro, prestamos, reservas, ana, luis):
    from biblioteca.usuarios import Usuario
    otro = Usuario("Otro")
    p = prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    prestamos.devolver(p)
    with pytest.raises(OperacionInvalida):
        prestamos.prestar(libro, otro)
    prestamos.prestar(libro, luis)
    assert r.estado == EstadoReserva.CUMPLIDA and libro.estado.nombre == "Prestado"


def test_cancelar_pendiente_se_omite(libro, prestamos, reservas, ana, luis):
    from biblioteca.usuarios import Usuario
    eva = Usuario("Eva")
    p = prestamos.prestar(libro, ana)
    rl = reservas.reservar(luis, libro); reservas.reservar(eva, libro)
    reservas.cancelar(rl)
    prestamos.devolver(p)
    assert luis.bandeja == [] and len(eva.bandeja) == 1


def test_reserva_vencida_pasa_al_siguiente(libro, prestamos, reservas, ana, luis):
    from biblioteca.usuarios import Usuario
    eva = Usuario("Eva")
    p = prestamos.prestar(libro, ana)
    rl = reservas.reservar(luis, libro); reservas.reservar(eva, libro)
    prestamos.devolver(p)
    reservas.vencer(rl)                    # Luis no retiró el libro
    assert rl.estado == EstadoReserva.VENCIDA
    assert len(eva.bandeja) == 1 and libro.reservado_para is eva


def test_cancelar_notificada_libera_libro(libro, prestamos, reservas, ana, luis):
    p = prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    prestamos.devolver(p)
    reservas.cancelar(r)
    assert libro.disponible


def test_validaciones(libro, prestamos, reservas, ana, luis):
    with pytest.raises(BibliotecaError):
        reservas.reservar(ana, libro)              # disponible
    prestamos.prestar(libro, ana)
    reservas.reservar(luis, libro)
    with pytest.raises(BibliotecaError):
        reservas.reservar(luis, libro)             # duplicada
