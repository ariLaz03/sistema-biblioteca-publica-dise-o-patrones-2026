from datetime import date, timedelta
from biblioteca.servicios import EntregaDomicilio, RenovacionPrioritaria, SeguroDanio

HOY = date(2026, 11, 1)


def test_decorators_se_acumulan(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY, servicios=[RenovacionPrioritaria, EntregaDomicilio, SeguroDanio])
    assert p.costo_servicios == 10.0
    assert p.fecha_limite == HOY + timedelta(days=7 + 7)
    d = p.detalle.descripcion()
    assert d.startswith("Préstamo estándar") and "Renovación" in d and "domicilio" in d and "Seguro" in d


def test_renovacion_evita_multa(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY, servicios=[RenovacionPrioritaria])
    assert prestamos.devolver(p, HOY + timedelta(days=12)) == 0
    assert p.total_a_pagar == 2.0


def test_sin_servicios(libro, prestamos, ana):
    p = prestamos.prestar(libro, ana, HOY)
    assert p.costo_servicios == 0 and p.detalle.descripcion() == "Préstamo estándar"
