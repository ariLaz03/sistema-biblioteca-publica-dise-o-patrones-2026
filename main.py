"""Demo del Sistema de Biblioteca Pública (los 4 integrantes integrados)."""
from datetime import date, timedelta

from biblioteca.colecciones import Coleccion
from biblioteca.libros import Catalogo, creador_para
from biblioteca.politicas import creador_politica_para
from biblioteca.prestamos import ServicioPrestamos
from biblioteca.reservas import ServicioReservas
from biblioteca.servicios import EntregaDomicilio, RenovacionPrioritaria


def titulo(txt: str) -> None:
    print(f"\n=== {txt} ===")


def main() -> None:
    hoy = date(2026, 11, 1)

    titulo("1. Catálogo y Factory Method (Integrante 1)")
    cat = Catalogo()
    prog = cat.categorias.crear("Programación", "Libros técnicos")
    nov = cat.categorias.crear("Novela")
    creador_para("fisico").registrar(cat, "111", "Clean Code", "Robert Martin", prog, 2008, ubicacion="A-1")
    creador_para("digital").registrar(cat, "222", "Fluent Python", "Luciano Ramalho", prog, 2022)
    creador_para("audiolibro").registrar(cat, "333", "Dune", "Frank Herbert", nov, duracion_min=1260)
    for l in cat.listar():
        print(f"  {l.isbn} {l.titulo:<15} {l.FORMATO:<10} {l.categoria.nombre}")
    print("  Búsqueda 'python':", [l.titulo for l in cat.buscar(titulo="python")])

    titulo("2. Préstamos, State, multas (Integrante 2) + Factory de políticas (1) + Decorator (4)")
    reservas = ServicioReservas()
    prestamos = ServicioPrestamos(reservas=reservas)
    ana = creador_politica_para("estudiante").crear_usuario("Ana", print)   # Factory Method
    luis = creador_politica_para("docente").crear_usuario("Luis", print)
    print(f"  {ana.nombre}: {ana.politica}\n  {luis.nombre}: {luis.politica}")
    clean = cat.obtener("111")
    p = prestamos.prestar(clean, ana, hoy, servicios=[RenovacionPrioritaria, EntregaDomicilio])
    print(f"  Estado del libro: {clean.estado.nombre} | vence {p.fecha_limite}")
    print(f"  Servicios: {p.detalle.descripcion()} (costo S/ {p.costo_servicios:.2f})")

    titulo("3. Reserva y notificación (Integrante 3, Observer)")
    reservas.reservar(luis, clean)
    prestamos.actualizar_vencidos(p.fecha_limite + timedelta(days=1))
    print(f"  Pasa el plazo: el libro queda {clean.estado.nombre} (State)")
    multa = prestamos.devolver(p, p.fecha_limite + timedelta(days=6))    # 6 días tarde
    print(f"  Multa de Ana: S/ {multa:.2f} | estado del libro: {clean.estado.nombre}")
    prestamos.prestar(clean, luis, hoy + timedelta(days=30))
    print(f"  Luis retiró el libro: {clean.estado.nombre}")

    titulo("4. Colecciones y subcolecciones (Integrante 4, Composite)")
    raiz, tec, py = Coleccion("Biblioteca Central"), Coleccion("Tecnología"), Coleccion("Python")
    raiz.agregar(tec); tec.agregar(py)
    py.agregar_libro(cat.obtener("222")); tec.agregar_libro(clean)
    raiz.agregar_libro(cat.obtener("333"))
    print(raiz.mostrar())


if __name__ == "__main__":
    main()
