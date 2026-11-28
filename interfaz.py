"""Interfaz web local del Sistema de Biblioteca Pública (las 4 partes integradas).

Uso:  py interfaz.py      (se abre el navegador en http://localhost:8000)
Sin instalar nada: usa solo la librería estándar y el código real del proyecto:
  Integrante 1: Catálogo, categorías, Factory Method
  Integrante 2: Préstamos, State, multas
  Integrante 3: Reservas y notificaciones (Observer)
  Integrante 4: Colecciones (Composite) y servicios del préstamo (Decorator)
"""
from __future__ import annotations

import json
import threading
import time
import webbrowser
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from biblioteca.colecciones import Coleccion, LibroHoja
from biblioteca.errores import BibliotecaError
from biblioteca.libros import Catalogo, creador_para
from biblioteca.politicas import creador_politica_para, tipos_usuario
from biblioteca.prestamos import ServicioPrestamos
from biblioteca.reservas import ServicioReservas
from biblioteca.servicios import EntregaDomicilio, RenovacionPrioritaria, SeguroDanio
from biblioteca.usuarios import Usuario

SERVICIOS = {"renovacion": RenovacionPrioritaria, "domicilio": EntregaDomicilio, "seguro": SeguroDanio}


class Demo:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.reiniciar()

    def anotar(self, texto: str) -> None:
        self.log.append(f"{time.strftime('%H:%M:%S')}  {texto}")

    # ------------------------------------------------------------ datos iniciales
    def reiniciar(self) -> None:
        self.log: list[str] = []
        self.catalogo = Catalogo()
        cats = {n: self.catalogo.categorias.crear(n, d) for n, d in [
            ("Programación", "Software y computación"), ("Novela", "Narrativa y ficción"),
            ("Ciencia", "Divulgación científica"), ("Historia", "Historia y sociedad"),
            ("Infantil", "Lectura para niños y jóvenes"), ("Autoayuda", "Desarrollo personal"),
            ("Arte", "Artes y cultura")]}
        # (tipo, isbn, título, autor, categoría, año, datos extra del formato)
        libros = [
            ("fisico", "111", "Clean Code", "Robert C. Martin", "Programación", 2008, {"ubicacion": "A-1"}),
            ("digital", "222", "Fluent Python", "Luciano Ramalho", "Programación", 2022, {}),
            ("fisico", "223", "Design Patterns", "Gamma, Helm, Johnson, Vlissides", "Programación", 1994, {"ubicacion": "A-2"}),
            ("fisico", "224", "The Pragmatic Programmer", "Andrew Hunt, David Thomas", "Programación", 1999, {"ubicacion": "A-3"}),
            ("digital", "225", "Introduction to Algorithms", "Thomas H. Cormen et al.", "Programación", 1990, {"formato_archivo": "PDF"}),
            ("audiolibro", "333", "Dune", "Frank Herbert", "Novela", 1965, {"duracion_min": 1260}),
            ("fisico", "444", "El Principito", "Antoine de Saint-Exupéry", "Novela", 1943, {"ubicacion": "B-1"}),
            ("fisico", "445", "Cien años de soledad", "Gabriel García Márquez", "Novela", 1967, {"ubicacion": "B-2"}),
            ("fisico", "446", "Conversación en La Catedral", "Mario Vargas Llosa", "Novela", 1969, {"ubicacion": "B-3"}),
            ("fisico", "447", "Los ríos profundos", "José María Arguedas", "Novela", 1958, {"ubicacion": "B-4"}),
            ("audiolibro", "551", "Cosmos", "Carl Sagan", "Ciencia", 1980, {"duracion_min": 780}),
            ("digital", "552", "Breve historia del tiempo", "Stephen Hawking", "Ciencia", 1988, {"formato_archivo": "EPUB"}),
            ("fisico", "553", "El gen egoísta", "Richard Dawkins", "Ciencia", 1976, {"ubicacion": "C-1"}),
            ("digital", "661", "Sapiens", "Yuval Noah Harari", "Historia", 2011, {"formato_archivo": "EPUB"}),
            ("fisico", "662", "Armas, gérmenes y acero", "Jared Diamond", "Historia", 1997, {"ubicacion": "D-1"}),
            ("fisico", "663", "Comentarios reales de los incas", "Inca Garcilaso de la Vega", "Historia", 1609, {"ubicacion": "D-2"}),
            ("fisico", "771", "Matilda", "Roald Dahl", "Infantil", 1988, {"ubicacion": "E-1"}),
            ("audiolibro", "772", "Platero y yo", "Juan Ramón Jiménez", "Infantil", 1914, {"duracion_min": 240}),
            ("digital", "881", "Hábitos atómicos", "James Clear", "Autoayuda", 2018, {"formato_archivo": "EPUB"}),
            ("audiolibro", "882", "Los 7 hábitos de la gente altamente efectiva", "Stephen R. Covey", "Autoayuda", 1989, {"duracion_min": 900}),
            ("fisico", "991", "La historia del arte", "E. H. Gombrich", "Arte", 1950, {"ubicacion": "F-1"}),
        ]
        for tipo, isbn, titulo, autor, cat, anio, extra in libros:
            creador_para(tipo).registrar(self.catalogo, isbn, titulo, autor, cats[cat], anio, **extra)

        self.reservas = ServicioReservas()
        self.prestamos = ServicioPrestamos(reservas=self.reservas)
        canal = lambda m: self.anotar("🔔 " + m)
        self.usuarios = {n: creador_politica_para(t).crear_usuario(n, canal) for n, t in (
            ("Ana", "estudiante"), ("Luis", "docente"), ("Eva", "externo"),
            ("Carlos", "estudiante"), ("Marta", "docente"), ("Diego", "externo"))}
        self.lista_reservas: list = []

        # colecciones y subcolecciones (Composite)
        self.raiz = Coleccion("Biblioteca Central")
        sub = lambda padre, nombre: padre.agregar(Coleccion(nombre))
        poner = lambda col, *isbns: [col.agregar_libro(self.catalogo.obtener(i)) for i in isbns]
        tec = sub(self.raiz, "Tecnología"); py = sub(tec, "Python"); alg = sub(tec, "Algoritmos y diseño")
        lit = sub(self.raiz, "Literatura"); lat = sub(lit, "Novela latinoamericana"); cla = sub(lit, "Clásicos universales")
        cie = sub(self.raiz, "Ciencias"); hum = sub(self.raiz, "Humanidades"); his = sub(hum, "Historia")
        inf = sub(self.raiz, "Infantil y juvenil"); des = sub(self.raiz, "Desarrollo personal")
        poner(py, "222"); poner(tec, "111", "224"); poner(alg, "223", "225")
        poner(lat, "445", "446", "447"); poner(cla, "444", "333"); poner(cie, "551", "552", "553")
        poner(his, "661", "662", "663"); poner(hum, "991"); poner(inf, "771", "772"); poner(des, "881", "882")

        # algunos préstamos y una reserva iniciales para que la demo no empiece vacía
        U, C = self.usuarios, self.catalogo.obtener
        self.prestamos.prestar(C("111"), U["Ana"], servicios=[RenovacionPrioritaria])
        self.prestamos.prestar(C("445"), U["Carlos"])
        self.prestamos.prestar(C("661"), U["Marta"], servicios=[SeguroDanio])
        self.lista_reservas.append(self.reservas.reservar(U["Eva"], C("445")))
        self.anotar("Demo lista: Ana tiene «Clean Code», Carlos «Cien años de soledad» "
                    "(Eva lo reservó) y Marta «Sapiens».")

    # ------------------------------------------------------------ vista
    def _arbol(self, c: Coleccion) -> dict:
        return {"nombre": c.nombre, "total": c.contar_libros(),
                "libros": [{"titulo": h.libro.titulo, "estado": h.libro.estado.nombre}
                           for h in c._hijos if isinstance(h, LibroHoja)],
                "subs": [self._arbol(s) for s in c.subcolecciones]}

    def _nombres_colecciones(self, c: Coleccion, out: list) -> list:
        out.append(c.nombre)
        for s in c.subcolecciones:
            self._nombres_colecciones(s, out)
        return out

    def estado(self) -> dict:
        hoy = date.today()
        activos = {id(p.libro): p.usuario.nombre for p in self.prestamos.activos()}
        libros = [{"isbn": l.isbn, "titulo": l.titulo, "autor": l.autor, "formato": l.FORMATO,
                   "categoria": l.categoria.nombre, "anio": l.anio, "estado": l.estado.nombre,
                   "prestado_a": activos.get(id(l)),
                   "reservado_para": l.reservado_para.nombre if l.reservado_para else None,
                   "en_cola": len(self.reservas.pendientes(l)), "dias": l.DIAS_PRESTAMO,
                   "multa_diaria": l.MULTA_DIARIA}
                  for l in self.catalogo.listar()]
        cats = [{"nombre": c.nombre, "descripcion": c.descripcion,
                 "libros": len(self.catalogo.buscar(categoria=c.nombre))}
                for c in self.catalogo.categorias.listar()]
        prestamos = [{"id": i, "isbn": p.libro.isbn, "titulo": p.libro.titulo, "usuario": p.usuario.nombre,
                      "desde": p.fecha_prestamo.isoformat(), "hasta": p.fecha_limite.isoformat(),
                      "servicios": p.detalle.descripcion(), "costo": p.costo_servicios,
                      "activo": p.activo, "multa": p.multa,
                      "vencido": p.activo and p.fecha_limite < hoy}
                     for i, p in enumerate(self.prestamos.historial)]
        return {
            "libros": libros, "categorias": cats, "prestamos": prestamos,
            "tipos": tipos_usuario(),
            "usuarios": [{"nombre": n, "tipo": u.tipo, "politica": u.politica.resumen(),
                          "deuda": u.deuda, "bandeja": u.bandeja}
                         for n, u in self.usuarios.items()],
            "reservas": [{"id": i, "usuario": r.usuario.nombre, "libro": r.libro.titulo,
                          "estado": r.estado.value, "activa": r.activa}
                         for i, r in enumerate(self.lista_reservas)],
            "arbol": self._arbol(self.raiz),
            "colecciones": self._nombres_colecciones(self.raiz, []),
            "servicios": [{"key": k, "nombre": c.NOMBRE, "costo": c.COSTO}
                          for k, c in SERVICIOS.items()],
            "log": self.log[-60:][::-1]}

    # ------------------------------------------------------------ acciones
    def _quitar_de_colecciones(self, c: Coleccion, libro) -> None:
        for h in list(c._hijos):
            if isinstance(h, LibroHoja) and h.libro is libro:
                c.quitar(h)
        for s in c.subcolecciones:
            self._quitar_de_colecciones(s, libro)

    def accion(self, d: dict) -> None:
        a = d.get("accion")
        if a == "reiniciar":
            return self.reiniciar()

        # ---- Integrante 1: catálogo y categorías
        if a == "crear_categoria":
            c = self.catalogo.categorias.crear(d["nombre"], d.get("descripcion", ""))
            self.anotar(f"Categoría creada: {c.nombre}.")
        elif a == "eliminar_categoria":
            self.catalogo.categorias.eliminar(d["nombre"], self.catalogo)
            self.anotar(f"Categoría eliminada: {d['nombre']}.")
        elif a == "registrar_libro":
            cat = self.catalogo.categorias.obtener(d["categoria"])
            anio = int(d["anio"]) if str(d.get("anio", "")).strip() else None
            libro = creador_para(d["tipo"]).registrar(
                self.catalogo, d["isbn"].strip(), d["titulo"].strip(), d["autor"].strip(), cat, anio)
            self.anotar(f"Libro registrado: «{libro.titulo}» ({libro.FORMATO}) vía Factory Method.")
        elif a == "eliminar_libro":
            libro = self.catalogo.obtener(d["isbn"])
            self.catalogo.eliminar(d["isbn"])
            self._quitar_de_colecciones(self.raiz, libro)
            self.anotar(f"Libro eliminado: «{libro.titulo}».")

        # ---- usuarios
        elif a == "nuevo_usuario":
            n = d["nombre"].strip()
            if not n or n in self.usuarios:
                raise BibliotecaError("Nombre vacío o usuario ya existente")
            u = creador_politica_para(d["tipo"]).crear_usuario(n, lambda m: self.anotar("🔔 " + m))
            self.usuarios[n] = u
            self.anotar(f"Usuario creado: {n} ({u.tipo}) vía Factory Method de políticas.")

        # ---- Integrante 2 (+4 Decorator): préstamos
        elif a == "prestar":
            libro, u = self.catalogo.obtener(d["isbn"]), self.usuarios[d["usuario"]]
            servicios = [SERVICIOS[k] for k in d.get("servicios", [])]
            p = self.prestamos.prestar(libro, u, servicios=servicios)
            extra = f" · {p.detalle.descripcion()}" if servicios else ""
            self.anotar(f"{u.nombre} retiró «{libro.titulo}», vence {p.fecha_limite}.{extra}")
        elif a == "devolver":
            p = self.prestamos.historial[int(d["id"])]
            retraso = max(0, int(d.get("retraso", 0)))
            self.anotar(f"{p.usuario.nombre} devolvió «{p.libro.titulo}»"
                        f"{f' con {retraso} días de retraso' if retraso else ' a tiempo'}"
                        " → el libro avisa a sus observadores (Observer).")
            multa = self.prestamos.devolver(p, p.fecha_limite + timedelta(days=retraso))
            if multa:
                self.anotar(f"Multa para {p.usuario.nombre}: S/ {multa:.2f}.")
        elif a == "simular_dias":
            dias = max(0, int(d.get("dias", 0)))
            nuevos = self.prestamos.actualizar_vencidos(date.today() + timedelta(days=dias))
            self.anotar(f"Pasan {dias} días: {len(nuevos)} préstamo(s) pasan al estado Vencido (State).")
        elif a == "pagar":
            u = self.usuarios[d["usuario"]]
            monto = u.deuda
            self.prestamos.pagar_multa(u, monto)
            self.anotar(f"{u.nombre} pagó su multa de S/ {monto:.2f}.")

        # ---- Integrante 3: reservas (Observer)
        elif a == "reservar":
            libro, u = self.catalogo.obtener(d["isbn"]), self.usuarios[d["usuario"]]
            self.lista_reservas.append(self.reservas.reservar(u, libro))
            self.anotar(f"{u.nombre} reservó «{libro.titulo}» (entra a la cola).")
        elif a in ("cancelar", "vencer"):
            r = self.lista_reservas[int(d["id"])]
            (self.reservas.cancelar if a == "cancelar" else self.reservas.vencer)(r)
            self.anotar(f"Reserva de {r.usuario.nombre} ({r.libro.titulo}): {r.estado.value}.")

        # ---- Integrante 4: colecciones (Composite)
        elif a == "crear_coleccion":
            nombre = d["nombre"].strip()
            if not nombre or self.raiz.buscar_coleccion(nombre):
                raise BibliotecaError("Nombre vacío o colección ya existente")
            padre = self.raiz.buscar_coleccion(d["padre"])
            if padre is None:
                raise BibliotecaError("La colección padre no existe")
            padre.agregar(Coleccion(nombre))
            self.anotar(f"Colección «{nombre}» creada dentro de «{padre.nombre}».")
        elif a == "agregar_a_coleccion":
            col = self.raiz.buscar_coleccion(d["coleccion"])
            libro = self.catalogo.obtener(d["isbn"])
            if col is None:
                raise BibliotecaError("La colección no existe")
            if libro in col.listar_libros():
                raise BibliotecaError("El libro ya está en esa colección")
            col.agregar_libro(libro)
            self.anotar(f"«{libro.titulo}» agregado a la colección «{col.nombre}».")
        else:
            raise BibliotecaError("Acción desconocida")


DEMO = Demo()

PAGINA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Biblioteca Pública · Sistema de gestión</title>
<style>
:root{--bg:#f5f3fb;--card:#fff;--tx:#1f1b2e;--mu:#6b6785;--bd:#e8e4f3;--ac:#7c3aed;--ac2:#ec4899;
--ok:#059669;--okb:#d1fae5;--warn:#b45309;--wb:#fef3c7;--bad:#dc2626;--bb:#fee2e2;--ib:#ede9fe;--sh:0 4px 18px rgba(80,50,160,.10)}
@media (prefers-color-scheme:dark){:root{--bg:#0f0b1e;--card:#1a1530;--tx:#f1eefc;--mu:#a29cc0;--bd:#2d2650;
--ac:#a78bfa;--ok:#34d399;--okb:#0b3a2c;--warn:#fbbf24;--wb:#3d2a06;--bad:#f87171;--bb:#42171b;--ib:#2a2250;--sh:0 4px 18px rgba(0,0,0,.4)}}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--tx)}
.hero{background:linear-gradient(120deg,#4338ca,#7c3aed 48%,#ec4899);color:#fff;padding:26px 24px 70px}
.hero-in{max-width:1280px;margin:auto;display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between}
.hero h1{margin:0;font-size:28px;letter-spacing:-.3px}
.hero p{margin:6px 0 10px;opacity:.9}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chips span{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.3);padding:3px 11px;border-radius:99px;font-size:12.5px;font-weight:600}
.quien{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:14px;padding:12px 14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.quien label{font-size:13px;opacity:.95}
.quien select{background:#fff;color:#1f1b2e;border:0;font-weight:600}
.quien button{background:rgba(255,255,255,.2);color:#fff;border:1px solid rgba(255,255,255,.4)}
.wrap{max-width:1280px;margin:auto;padding:0 24px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-top:-46px}
.stat{background:var(--card);border-radius:16px;padding:14px 16px;box-shadow:var(--sh);display:flex;gap:12px;align-items:center;border:1px solid var(--bd)}
.stat .ic{width:44px;height:44px;border-radius:12px;display:grid;place-items:center;font-size:22px;flex:none}
.stat b{font-size:24px;display:block;line-height:1.1}.stat span{font-size:12.5px;color:var(--mu)}
input,select,button{font:inherit;padding:8px 12px;border-radius:10px;border:1px solid var(--bd);background:var(--card);color:var(--tx)}
input{min-width:0}button{cursor:pointer;transition:.15s}button:hover{border-color:var(--ac);transform:translateY(-1px)}
button.p{background:linear-gradient(120deg,#7c3aed,#c026d3);color:#fff;border:0;font-weight:600}
button.d{color:var(--bad)}button.s{padding:6px 11px;font-size:13px}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0 4px}
nav button{border-radius:99px;padding:9px 18px;font-weight:600}
nav button.on{background:linear-gradient(120deg,#7c3aed,#ec4899);color:#fff;border:0;box-shadow:0 4px 14px rgba(124,58,237,.35)}
main{display:grid;grid-template-columns:1.9fr 1fr;gap:20px;align-items:start}
@media(max-width:980px){main{grid-template-columns:1fr}}
section{background:var(--card);border:1px solid var(--bd);border-radius:18px;padding:18px;margin-top:16px;box-shadow:var(--sh)}
h2{margin:0 0 12px;font-size:16px}.pane{display:none}.pane.on{display:block}
.fila{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}
.fila input,.fila select{flex:1 1 130px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:14px}
.libro{border:1px solid var(--bd);border-radius:16px;overflow:hidden;background:var(--card);display:flex;flex-direction:column;transition:.15s}
.libro:hover{transform:translateY(-3px);box-shadow:var(--sh)}
.portada{height:104px;display:grid;place-items:center;font-size:44px;position:relative;color:#fff}
.portada .fmt{position:absolute;top:8px;left:8px;font-size:11px;font-weight:700;background:rgba(0,0,0,.28);padding:2px 9px;border-radius:99px}
.cuerpo{padding:12px;display:flex;flex-direction:column;gap:6px;flex:1}
.tit{font-weight:700;line-height:1.25}.aut{font-size:13px;color:var(--mu)}
.chip{font-size:11.5px;padding:2px 9px;border-radius:99px;background:var(--ib);color:var(--ac);font-weight:600}
.meta{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.m{color:var(--mu);font-size:12.5px}
.badge{font-size:11.5px;padding:2px 9px;border-radius:99px;font-weight:700}
.item .badge{margin-left:6px}
.Disponible,.Cumplida{background:var(--okb);color:var(--ok)}
.Prestado,.Vencido,.Vencida,.Cancelada{background:var(--bb);color:var(--bad)}
.Reservado,.Notificada,.Pendiente{background:var(--wb);color:var(--warn)}
.acc{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:auto}
.acc input[type=number]{width:62px;padding:6px 8px}
.item{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:11px 0;border-top:1px solid var(--bd)}
.item:first-child{border-top:0}.item b{display:block}
ul,ol{margin:0;padding:0;list-style:none}
.noti{background:var(--ib);border-radius:12px;padding:10px 12px;margin-bottom:8px;font-size:14px;border-left:0}
.vacio{color:var(--mu);font-size:14px;padding:6px 0}
.log li{color:var(--mu);font-size:12.5px;font-family:ui-monospace,Consolas,monospace;padding:5px 0;border-top:1px solid var(--bd)}
.arbol ul{margin-left:16px;padding-left:10px;border-left:2px dashed var(--bd)}
.arbol .col{font-weight:700;margin-top:8px}.arbol .lib{font-size:14px;padding:3px 0}
label.chk{display:flex;gap:6px;align-items:center;font-size:14px;background:var(--ib);padding:6px 11px;border-radius:99px}
label.chk input{flex:none;padding:0}
#toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:var(--bad);color:#fff;padding:11px 18px;border-radius:12px;display:none;max-width:90%;z-index:9;box-shadow:var(--sh)}
.tip{font-size:13px;color:var(--mu);margin:0 0 12px}
</style></head><body>
<div class="hero"><div class="hero-in">
 <div><h1>📚 Biblioteca Pública</h1><p>Sistema de gestión de catálogo, préstamos, reservas y colecciones</p>
  <div class="chips"><span>Factory Method</span><span>State</span><span>Observer</span><span>Composite</span><span>Decorator</span></div></div>
 <div class="quien"><label for="usuario">👤 Actuar como</label><select id="usuario"></select>
  <button id="reiniciar">↺ Reiniciar demo</button></div>
</div></div>
<div class="wrap">
 <div class="stats" id="stats"></div>
 <nav id="tabs"></nav>
 <main>
 <div>
  <div class="pane" id="p-catalogo">
   <section><h2>📖 Catálogo</h2>
    <div class="fila"><input id="q" placeholder="🔎 Buscar por título o autor…"><select id="fcat"></select><select id="fest"></select></div>
    <div class="grid" id="libros"></div></section>
   <section><h2>➕ Registrar libro (Factory Method)</h2>
    <div class="fila"><select id="r-tipo"><option value="fisico">Físico</option><option value="digital">Digital</option><option value="audiolibro">Audiolibro</option></select>
     <input id="r-isbn" placeholder="ISBN"><input id="r-titulo" placeholder="Título"></div>
    <div class="fila"><input id="r-autor" placeholder="Autor"><select id="r-cat"></select><input id="r-anio" placeholder="Año" type="number">
     <button class="p" id="r-ok">Registrar</button></div></section>
   <section><h2>🏷 Categorías</h2><div id="cats"></div>
    <div class="fila" style="margin-top:10px"><input id="c-nombre" placeholder="Nueva categoría"><input id="c-desc" placeholder="Descripción">
     <button class="p" id="c-ok">Crear</button></div></section>
  </div>

  <div class="pane" id="p-prestamos">
   <section><h2>🔁 Nuevo préstamo (State)</h2>
    <p class="tip">Elige un libro disponible (o apartado para ti) y, si quieres, servicios adicionales (Decorator).</p>
    <div class="fila"><select id="p-libro"></select></div>
    <div class="fila" id="p-servs"></div>
    <button class="p" id="p-ok">Prestar</button></section>
   <section><h2>📌 Préstamos activos</h2>
    <p class="tip">«Retraso» simula cuántos días después del vencimiento se devuelve (0 = a tiempo).</p>
    <div id="activos"></div></section>
   <section><h2>⏱ Simular el paso del tiempo (State)</h2>
    <p class="tip">Los libros prestados que superen su fecha límite pasan al estado <b>Vencido</b>.</p>
    <div class="fila"><input id="s-dias" type="number" min="0" value="30" placeholder="Días"><button class="p" id="s-ok">Avanzar días</button></div></section>
   <section><h2>🧾 Historial</h2><div id="historial"></div></section>
   <section><h2>👥 Usuarios y multas (Factory Method de políticas)</h2><div id="usuarios"></div>
    <div class="fila" style="margin-top:10px"><input id="u-nombre" placeholder="Nuevo usuario"><select id="u-tipo"></select><button id="u-ok">Agregar</button></div></section>
  </div>

  <div class="pane" id="p-reservas">
   <section><h2>⏳ Reservar libro (Observer)</h2>
    <p class="tip">Solo se pueden reservar libros que no estén disponibles. Al devolverse, el primero de la cola recibe una notificación.</p>
    <div class="fila"><select id="v-libro"></select><button class="p" id="v-ok">Reservar</button></div></section>
   <section><h2>📋 Reservas</h2><div id="reservas"></div></section>
  </div>

  <div class="pane" id="p-colecciones">
   <section><h2>🗂 Colecciones (Composite)</h2><div class="arbol" id="arbol"></div></section>
   <section><h2>Nueva colección</h2>
    <div class="fila"><input id="k-nombre" placeholder="Nombre"><select id="k-padre"></select><button class="p" id="k-ok">Crear</button></div></section>
   <section><h2>Agregar libro a una colección</h2>
    <div class="fila"><select id="a-libro"></select><select id="a-col"></select><button class="p" id="a-ok">Agregar</button></div></section>
  </div>
 </div>

 <aside>
  <section><h2>🔔 Notificaciones de <span id="nombre"></span></h2><ul id="bandeja"></ul></section>
  <section><h2>📜 Registro de eventos</h2><ol id="log" class="log"></ol></section>
 </aside>
 </main>
</div>
<div id="toast"></div>
<script>
const $=id=>document.getElementById(id);
let S=null, TAB='catalogo';
const TABS=[['catalogo','📖 Catálogo'],['prestamos','🔁 Préstamos'],['reservas','⏳ Reservas'],['colecciones','🗂 Colecciones']];
const PAL=[['#6366f1','#8b5cf6'],['#ec4899','#f43f5e'],['#06b6d4','#3b82f6'],['#f59e0b','#ef4444'],
 ['#10b981','#14b8a6'],['#a855f7','#d946ef'],['#84cc16','#22c55e'],['#f97316','#eab308']];
const EMO={'programación':'💻','novela':'📖','ciencia':'🔬','historia':'🏛️','infantil':'🧸','autoayuda':'🌱','arte':'🎨'};
const soles=n=>'S/ '+Number(n).toFixed(2);
function look(cat){const i=S.categorias.findIndex(c=>c.nombre===cat),p=PAL[(i<0?0:i)%PAL.length];
  return {bg:'linear-gradient(135deg,'+p[0]+','+p[1]+')',emo:EMO[cat.toLowerCase()]||'📚',c:p[0]}}
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e}
function btn(txt,fn,cls){const b=el('button',cls,txt);b.onclick=fn;return b}
function badge(t){return el('span','badge '+t,t)}
function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';clearTimeout(t._t);t._t=setTimeout(()=>t.style.display='none',3800)}
async function enviar(d){
  try{
    const r=await fetch('/api/accion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
    const j=await r.json(); if(j.error){toast(j.error);return false}
    await cargar(); return true;
  }catch(e){toast('Error de conexión');return false}
}
async function cargar(){S=await (await fetch('/api/estado')).json();pintar()}
function fill(id,items,vacio){
  const s=$(id),prev=s.value;s.replaceChildren();
  if(!items.length&&vacio)s.add(new Option(vacio,''));
  items.forEach(([v,t])=>s.add(new Option(t,v)));
  if(items.some(([v])=>v===prev))s.value=prev;
}
function yo(){return $('usuario').value}
function item(left,right){const r=el('div','item'),l=el('div');left.forEach(x=>l.appendChild(x));r.appendChild(l);if(right)r.appendChild(right);return r}
function titulo(t,badges){const b=el('b',null,t);(badges||[]).forEach(x=>b.appendChild(x));return b}
function vacio(c,t){c.appendChild(el('div','vacio',t))}

function pintar(){
  const sel=$('usuario'),act=sel.value;
  fill('usuario',S.usuarios.map(u=>[u.nombre,u.nombre+' ('+u.tipo+')']));
  if(!act&&sel.options.length)sel.value=sel.options[0].value;
  $('nombre').textContent=yo();
  fill('u-tipo',S.tipos.map(t=>[t,t.charAt(0).toUpperCase()+t.slice(1)]));

  // --- resumen
  const n=e=>S.libros.filter(l=>l.estado===e).length;
  const activasRes=S.reservas.filter(r=>r.activa).length, deuda=S.usuarios.reduce((a,u)=>a+u.deuda,0);
  const cards=[['📚',S.libros.length,'Libros en catálogo','#ede9fe'],['✅',n('Disponible'),'Disponibles','#d1fae5'],
    ['📕',n('Prestado')+n('Vencido'),'En préstamo ('+n('Vencido')+' vencidos)','#fee2e2'],
    ['⏳',activasRes,'Reservas activas','#fef3c7'],['💰',soles(deuda),'Multas pendientes','#fce7f3']];
  const ST=$('stats');ST.replaceChildren();
  cards.forEach(([ic,v,t,c])=>{const d=el('div','stat'),i=el('div','ic',ic);i.style.background=c;d.appendChild(i);
    const x=el('div');x.appendChild(el('b',null,String(v)));x.appendChild(el('span',null,t));d.appendChild(x);ST.appendChild(d)});

  const nav=$('tabs');nav.replaceChildren();
  TABS.forEach(([k,t])=>nav.appendChild(btn(t,()=>{TAB=k;pintar()},k===TAB?'on':'')));
  document.querySelectorAll('.pane').forEach(p=>p.classList.toggle('on',p.id==='p-'+TAB));

  // --- catálogo
  fill('fcat',[['','Todas las categorías'],...S.categorias.map(c=>[c.nombre,c.nombre])]);
  fill('fest',[['','Todos los estados'],...['Disponible','Prestado','Vencido','Reservado'].map(e=>[e,e])]);
  fill('r-cat',S.categorias.map(c=>[c.nombre,c.nombre]),'(crea una categoría)');
  const q=$('q').value.toLowerCase(),fc=$('fcat').value,fe=$('fest').value;
  const L=$('libros');L.replaceChildren();
  const vis=S.libros.filter(l=>(!fc||l.categoria===fc)&&(!fe||l.estado===fe)&&(!q||l.titulo.toLowerCase().includes(q)||l.autor.toLowerCase().includes(q)));
  if(!vis.length)vacio(L,'Sin resultados');
  vis.forEach(l=>{
    const lk=look(l.categoria),card=el('div','libro'),por=el('div','portada',lk.emo);por.style.background=lk.bg;
    por.appendChild(el('span','fmt',l.formato));card.appendChild(por);
    const c=el('div','cuerpo');c.appendChild(el('div','tit',l.titulo));
    c.appendChild(el('div','aut',l.autor+(l.anio?' · '+l.anio:'')));
    const meta=el('div','meta');meta.appendChild(el('span','chip',l.categoria));meta.appendChild(badge(l.estado));c.appendChild(meta);
    let det='';
    if(l.prestado_a)det+='Lo tiene '+l.prestado_a+'. ';
    if(l.reservado_para)det+='Apartado para '+l.reservado_para+'. ';
    if(l.en_cola)det+=l.en_cola+' en cola. ';
    if(det)c.appendChild(el('div','m',det));
    const acc=el('div','acc');
    if(l.estado==='Disponible'){acc.appendChild(btn('Prestar a '+yo(),()=>enviar({accion:'prestar',isbn:l.isbn,usuario:yo()}),'p s'));
      acc.appendChild(btn('🗑',()=>enviar({accion:'eliminar_libro',isbn:l.isbn}),'d s'))}
    else if(l.estado==='Reservado'&&l.reservado_para===yo())acc.appendChild(btn('Retirar',()=>enviar({accion:'prestar',isbn:l.isbn,usuario:yo()}),'p s'));
    else acc.appendChild(btn('Reservar como '+yo(),()=>enviar({accion:'reservar',isbn:l.isbn,usuario:yo()}),'s'));
    c.appendChild(acc);card.appendChild(c);L.appendChild(card);
  });
  const C=$('cats');C.replaceChildren();
  S.categorias.forEach(c=>{
    const acc=el('div','acc');acc.appendChild(btn('Eliminar',()=>enviar({accion:'eliminar_categoria',nombre:c.nombre}),'d s'));
    const t=titulo(c.nombre);t.insertBefore(document.createTextNode(look(c.nombre).emo+' '),t.firstChild);
    C.appendChild(item([t,el('span','m',(c.descripcion||'Sin descripción')+' · '+c.libros+' libros')],acc));
  });

  // --- préstamos
  const disp=S.libros.filter(l=>l.estado==='Disponible'||(l.estado==='Reservado'&&l.reservado_para===yo()));
  fill('p-libro',disp.map(l=>[l.isbn,l.titulo+' ('+l.estado+')']),'No hay libros disponibles');
  const ps=$('p-servs');
  if(!ps.children.length)S.servicios.forEach(s=>{
    const lb=el('label','chk'),cb=document.createElement('input');cb.type='checkbox';cb.value=s.key;
    lb.appendChild(cb);lb.appendChild(document.createTextNode(s.nombre+' (+'+soles(s.costo)+')'));ps.appendChild(lb);
  });
  $('p-ok').textContent='Prestar a '+yo();
  const A=$('activos');A.replaceChildren();
  const act2=S.prestamos.filter(p=>p.activo);
  if(!act2.length)vacio(A,'No hay préstamos activos');
  act2.forEach(p=>{
    const inp=document.createElement('input');inp.type='number';inp.min='0';inp.value='0';inp.title='Días de retraso';
    const acc=el('div','acc');acc.appendChild(el('span','m','Retraso:'));acc.appendChild(inp);
    acc.appendChild(btn('Devolver',()=>enviar({accion:'devolver',id:p.id,retraso:inp.value||0}),'p s'));
    const ven=p.vencido?[badge('Vencido')]:[];
    A.appendChild(item([titulo(p.titulo,ven),
      el('span','m',p.usuario+' · '+p.desde+' → vence '+p.hasta+' · '+p.servicios+(p.costo?' ('+soles(p.costo)+')':''))],acc));
  });
  const H=$('historial');H.replaceChildren();
  const hist=S.prestamos.filter(p=>!p.activo).reverse();
  if(!hist.length)vacio(H,'Aún no hay devoluciones');
  hist.forEach(p=>H.appendChild(item([titulo(p.titulo),el('span','m',p.usuario+' · multa '+soles(p.multa)+' · servicios '+soles(p.costo))])));
  const U=$('usuarios');U.replaceChildren();
  S.usuarios.forEach(u=>{
    const acc=el('div','acc');if(u.deuda>0)acc.appendChild(btn('Pagar '+soles(u.deuda),()=>enviar({accion:'pagar',usuario:u.nombre}),'p s'));
    U.appendChild(item([titulo(u.nombre,[el('span','badge Reservado',u.tipo)]),el('span','m',u.politica+' · '+(u.deuda>0?'Debe '+soles(u.deuda):'Sin deuda'))],acc));
  });

  // --- reservas
  fill('v-libro',S.libros.filter(l=>l.estado!=='Disponible').map(l=>[l.isbn,l.titulo+' ('+l.estado+')']),'No hay libros ocupados');
  $('v-ok').textContent='Reservar como '+yo();
  const R=$('reservas');R.replaceChildren();
  if(!S.reservas.length)vacio(R,'Aún no hay reservas');
  S.reservas.forEach(r=>{
    const acc=el('div','acc');
    if(r.activa){acc.appendChild(btn('Cancelar',()=>enviar({accion:'cancelar',id:r.id}),'s'));
      if(r.estado==='Notificada')acc.appendChild(btn('Vencer',()=>enviar({accion:'vencer',id:r.id}),'s'))}
    R.appendChild(item([titulo(r.usuario+' · '+r.libro,[badge(r.estado)])],acc));
  });

  // --- colecciones
  const T=$('arbol');T.replaceChildren();
  const nodo=n=>{
    const li=el('li'),h=el('div','col','🗂 '+n.nombre+' ('+n.total+' libros)');li.appendChild(h);
    const ul=el('ul');n.libros.forEach(b=>{const x=el('li','lib','📖 '+b.titulo+' ');x.appendChild(badge(b.estado));ul.appendChild(x)});
    n.subs.forEach(s=>ul.appendChild(nodo(s)));li.appendChild(ul);return li};
  const raiz=el('ul');raiz.style.cssText='margin:0;border:0;padding:0';raiz.appendChild(nodo(S.arbol));T.appendChild(raiz);
  fill('k-padre',S.colecciones.map(n=>[n,n]));
  fill('a-col',S.colecciones.map(n=>[n,n]));
  fill('a-libro',S.libros.map(l=>[l.isbn,l.titulo]),'(sin libros)');

  // --- lateral
  const B=$('bandeja');B.replaceChildren();
  const u=S.usuarios.find(x=>x.nombre===yo());
  if(!u||!u.bandeja.length)B.appendChild(el('li','vacio','Sin notificaciones'));
  else u.bandeja.slice().reverse().forEach(m=>B.appendChild(el('li','noti',m)));
  const G=$('log');G.replaceChildren();S.log.forEach(x=>G.appendChild(el('li',null,x)));
}

$('usuario').onchange=pintar;
$('reiniciar').onclick=()=>enviar({accion:'reiniciar'});
$('q').oninput=pintar;$('fcat').onchange=pintar;$('fest').onchange=pintar;
$('r-ok').onclick=async()=>{
  if(await enviar({accion:'registrar_libro',tipo:$('r-tipo').value,isbn:$('r-isbn').value,titulo:$('r-titulo').value,
    autor:$('r-autor').value,categoria:$('r-cat').value,anio:$('r-anio').value}))
    ['r-isbn','r-titulo','r-autor','r-anio'].forEach(i=>$(i).value='')};
$('c-ok').onclick=async()=>{if(await enviar({accion:'crear_categoria',nombre:$('c-nombre').value,descripcion:$('c-desc').value}))
  {$('c-nombre').value='';$('c-desc').value=''}};
$('p-ok').onclick=()=>enviar({accion:'prestar',usuario:yo(),isbn:$('p-libro').value,
  servicios:[...document.querySelectorAll('#p-servs input:checked')].map(c=>c.value)});
$('u-ok').onclick=async()=>{if(await enviar({accion:'nuevo_usuario',nombre:$('u-nombre').value,tipo:$('u-tipo').value}))$('u-nombre').value=''};
$('s-ok').onclick=()=>enviar({accion:'simular_dias',dias:$('s-dias').value});
$('v-ok').onclick=()=>enviar({accion:'reservar',usuario:yo(),isbn:$('v-libro').value});
$('k-ok').onclick=async()=>{if(await enviar({accion:'crear_coleccion',nombre:$('k-nombre').value,padre:$('k-padre').value}))$('k-nombre').value=''};
$('a-ok').onclick=()=>enviar({accion:'agregar_a_coleccion',coleccion:$('a-col').value,isbn:$('a-libro').value});
cargar();
</script></body></html>
"""


class Manejador(BaseHTTPRequestHandler):
    def _enviar(self, codigo: int, cuerpo: bytes, tipo: str) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, obj: dict, codigo: int = 200) -> None:
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                     "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path == "/api/estado":
            with DEMO.lock:
                return self._json(DEMO.estado())
        if self.path in ("/", "/index.html"):
            return self._enviar(200, PAGINA.encode("utf-8"), "text/html; charset=utf-8")
        self._enviar(404, b"No encontrado", "text/plain")

    def do_POST(self) -> None:
        if self.path != "/api/accion":
            return self._enviar(404, b"No encontrado", "text/plain")
        try:
            datos = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            with DEMO.lock:
                DEMO.accion(datos)
            self._json({"ok": True})
        except (BibliotecaError, KeyError, IndexError, ValueError) as e:
            self._json({"error": str(e) or "Operación no válida"}, 400)

    def log_message(self, *args) -> None:
        pass


def main() -> None:
    for puerto in range(8000, 8011):
        try:
            servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
            break
        except OSError:
            continue
    else:
        raise SystemExit("No hay puertos libres entre 8000 y 8010")
    url = f"http://localhost:{puerto}"
    print(f"Interfaz lista en {url}  (Ctrl+C para cerrar)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrado.")


if __name__ == "__main__":
    main()
