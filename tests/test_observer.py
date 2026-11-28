"""Pruebas adicionales del Integrante 3: patrón Observer y casos borde de reservas."""
import pytest
from biblioteca.errores import BibliotecaError, OperacionInvalida
from biblioteca.libros import LibroDigitalCreator
from biblioteca.reservas import EstadoReserva, Observador, SujetoDisponibilidad
from biblioteca.usuarios import Usuario


# ---------- Patrón Observer en sí (con observadores falsos) ----------
class Espia(Observador):
    def __init__(self):
        self.llamadas = 0

    def actualizar(self, sujeto):
        self.llamadas += 1


def test_notifica_a_todos_los_observadores():
    s, a, b = SujetoDisponibilidad(), Espia(), Espia()
    s.suscribir(a); s.suscribir(b)
    s.notificar_disponible()
    assert (a.llamadas, b.llamadas) == (1, 1)


def test_no_duplica_suscripcion():
    s, a = SujetoDisponibilidad(), Espia()
    s.suscribir(a); s.suscribir(a)
    s.notificar_disponible()
    assert a.llamadas == 1


def test_desuscribir_deja_de_notificar():
    s, a = SujetoDisponibilidad(), Espia()
    s.suscribir(a); s.desuscribir(a)
    s.notificar_disponible()
    assert a.llamadas == 0


def test_notificar_sin_observadores_no_falla():
    SujetoDisponibilidad().notificar_disponible()


def test_desuscribir_inexistente_no_falla():
    SujetoDisponibilidad().desuscribir(Espia())


# ---------- Notificaciones ----------
def test_mensaje_incluye_titulo_y_usa_canal(libro, prestamos, reservas, ana):
    recibidos = []
    luis = Usuario("Luis", canal=recibidos.append)
    p = prestamos.prestar(libro, ana)
    reservas.reservar(luis, libro)
    prestamos.devolver(p)
    assert "Clean Code" in luis.bandeja[0]
    assert len(recibidos) == 1 and "Luis" in recibidos[0]


def test_sin_reservas_el_libro_queda_disponible(libro, prestamos):
    u = Usuario("Ana")
    p = prestamos.prestar(libro, u)
    prestamos.devolver(p)
    assert libro.disponible and u.bandeja == []


def test_observador_se_desuscribe_al_vaciar_la_cola(libro, prestamos, reservas, ana, luis):
    p = prestamos.prestar(libro, ana)
    reservas.reservar(luis, libro)
    prestamos.devolver(p)
    assert libro._observadores == []


# ---------- Casos borde de reservas ----------
def test_no_cancela_reserva_ya_cerrada(libro, prestamos, reservas, ana, luis):
    prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    reservas.cancelar(r)
    with pytest.raises(BibliotecaError):
        reservas.cancelar(r)


def test_vencer_pendiente_no_libera_el_libro(libro, prestamos, reservas, ana, luis):
    prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    reservas.vencer(r)
    assert r.estado == EstadoReserva.VENCIDA and libro.estado.nombre == "Prestado"


def test_no_se_puede_devolver_libro_reservado(libro, prestamos, reservas, ana, luis):
    p = prestamos.prestar(libro, ana)
    reservas.reservar(luis, libro)
    prestamos.devolver(p)
    with pytest.raises(OperacionInvalida):
        libro.devolver()


def test_se_puede_reservar_libro_ya_apartado(libro, prestamos, reservas, ana, luis):
    eva = Usuario("Eva")
    p = prestamos.prestar(libro, ana)
    reservas.reservar(luis, libro)
    prestamos.devolver(p)                    # queda Reservado para Luis
    r = reservas.reservar(eva, libro)        # Eva entra a la cola
    assert r.estado == EstadoReserva.PENDIENTE


def test_usuario_puede_reservar_de_nuevo_tras_cancelar(libro, prestamos, reservas, ana, luis):
    prestamos.prestar(libro, ana)
    reservas.cancelar(reservas.reservar(luis, libro))
    assert reservas.reservar(luis, libro).estado == EstadoReserva.PENDIENTE


def test_colas_independientes_por_libro(cat, prestamos, reservas, ana, luis):
    c = cat.categorias.obtener("Novela")
    l1 = LibroDigitalCreator().registrar(cat, "A1", "Uno", "X", c)
    l2 = LibroDigitalCreator().registrar(cat, "A2", "Dos", "X", c)
    p1, p2 = prestamos.prestar(l1, ana), prestamos.prestar(l2, ana)
    r1, r2 = reservas.reservar(luis, l1), reservas.reservar(Usuario("Eva"), l2)
    prestamos.devolver(p1)
    assert r1.estado == EstadoReserva.NOTIFICADA and r2.estado == EstadoReserva.PENDIENTE


def test_cumplida_solo_si_estaba_notificada(libro, prestamos, reservas, ana, luis):
    prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    reservas.marcar_cumplida(libro, luis)    # aún pendiente: no cambia
    assert r.estado == EstadoReserva.PENDIENTE


def test_reserva_activa_por_estado(libro, prestamos, reservas, ana, luis):
    prestamos.prestar(libro, ana)
    r = reservas.reservar(luis, libro)
    assert r.activa
    reservas.cancelar(r)
    assert not r.activa
