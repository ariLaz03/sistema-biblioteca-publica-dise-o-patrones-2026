# 📚 Sistema de Biblioteca Pública – Patrones de Diseño

Sistema de gestión de una biblioteca pública (catálogo, préstamos, devoluciones, multas por atraso y reservas) desarrollado en **Python** como **Proyecto Final de Diseño de Patrones (proyecto N.º 9)**. Aplica de forma intencional **5 patrones de diseño** (creacional, estructurales y de comportamiento) siguiendo principios SOLID, bajo acoplamiento y alta cohesión.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-63%20passed-brightgreen)
![Patrones](https://img.shields.io/badge/patrones-5-orange)

---

## 📑 Contenido

1. [Descripción](#-descripción)
2. [Equipo y patrones](#-equipo-y-patrones)
3. [Requisitos](#-requisitos)
4. [Instalación y uso](#-instalación-y-uso)
5. [Funcionalidades](#-funcionalidades)
6. [Patrones de diseño aplicados](#-patrones-de-diseño-aplicados)
7. [Reglas de negocio](#-reglas-de-negocio)
8. [Estructura del proyecto](#-estructura-del-proyecto)
9. [Pruebas](#-pruebas)
10. [Cómo extender el sistema](#-cómo-extender-el-sistema)

---

## 📖 Descripción

La biblioteca necesita controlar su catálogo de libros (físicos, digitales y audiolibros), prestarlos a usuarios con distintas reglas según su tipo (estudiante, docente, externo), calcular multas por atraso y permitir **reservar** ejemplares que están prestados, avisando al usuario cuando el libro vuelve a estar disponible.

**Actores:** usuario/lector (estudiante, docente, externo) y bibliotecario/administrador.

## 👥 Equipo y patrones

| Integrante | Módulo | Patrón |
|---|---|---|
| 1 – Libros y catálogo | `biblioteca/libros/`, `biblioteca/politicas/` | **Factory Method**: tipos de libro y políticas de préstamo por tipo de usuario |
| 2 – Préstamos y devoluciones | `biblioteca/prestamos/` | **State**: Disponible, Prestado, Vencido, Reservado + multas |
| 3 – Reservas y notificaciones | `biblioteca/reservas/` | **Observer** |
| 4 – Colecciones y servicios | `biblioteca/colecciones/`, `biblioteca/servicios/` | **Composite** y **Decorator** |

## ⚙️ Requisitos

- Python **3.10 o superior**
- `pytest` (solo para ejecutar las pruebas)
- La demo por consola y la interfaz web **no requieren instalar nada más** (solo usan la librería estándar).

## 🚀 Instalación y uso

```bash
# 1. Clonar el repositorio
git clone https://github.com/ariLaz03/sistema-biblioteca-publica-dise-o-patrones-2026.git
cd sistema-biblioteca-publica-dise-o-patrones-2026

# 2. (Opcional) crear entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / Mac

# 3. Instalar dependencias (solo pytest)
pip install -r requirements.txt
```

| Acción | Windows | Linux / Mac |
|---|---|---|
| Demo por consola | `py main.py` | `python main.py` |
| Interfaz web (http://localhost:8000) | `py interfaz.py` | `python interfaz.py` |
| Ejecutar pruebas | `py -m pytest` | `python -m pytest` |

## ✅ Funcionalidades

1. Registrar libros en el catálogo (físico, digital o audiolibro) con categoría, año y ubicación.
2. Buscar libros por título, autor o categoría y listarlos ordenados.
3. Registrar usuarios con una política según su tipo (estudiante, docente, externo).
4. Prestar un libro respetando el plazo y el máximo de libros de la política del usuario.
5. Devolver libros y calcular la multa por atraso.
6. Bloquear nuevos préstamos si el usuario tiene una multa pendiente; permitir pagarla.
7. Marcar automáticamente como *Vencido* los préstamos fuera de plazo y avisar al usuario.
8. Reservar un libro prestado (cola FIFO) y notificar al primero de la cola cuando se devuelve.
9. Organizar los libros en colecciones y subcolecciones.
10. Agregar servicios extra al préstamo: renovación prioritaria, entrega a domicilio y seguro.

## 🧩 Patrones de diseño aplicados

### 1. Factory Method (creacional)
- **Libros:** `creador_para("digital").registrar(catalogo, ...)` crea libros físicos, digitales o audiolibros (`biblioteca/libros/factory.py`).
- **Políticas de préstamo:** `creador_politica_para("docente").crear_usuario("Marta")` crea un usuario con su política (días extra, máximo de libros, factor de multa) (`biblioteca/politicas/factory.py`).
- **Por qué:** agregar un tipo nuevo no obliga a modificar el código existente (principio abierto/cerrado).

### 2. State (comportamiento)
- `Libro` es el contexto. Estados: `Disponible → Prestado → Vencido` y `Reservado` (`biblioteca/prestamos/estados.py`).
- Cada estado define qué operaciones permite; por ejemplo, un libro *Vencido* solo se puede devolver.
- **Por qué:** elimina los `if/else` sobre el estado y concentra las reglas de transición.

### 3. Observer (comportamiento)
- Al devolverse un libro, `notificar_disponible()` avisa al `ObservadorReservas`, que aparta el libro (*Reservado*) para el primero de la cola FIFO y le envía la notificación (`biblioteca/reservas/`).
- **Por qué:** el libro no conoce el sistema de reservas; ambos quedan desacoplados.

### 4. Decorator (estructural)
- `Prestamo` guarda un `DetallePrestamo` envuelto por servicios (`RenovacionPrioritaria`, `EntregaDomicilio`, `SeguroDanio`) que suman costo y días (`biblioteca/servicios/decorators.py`).
- **Por qué:** combina servicios extra libremente sin crear una clase por cada combinación.

### 5. Composite (estructural)
- `Coleccion` agrupa libros (`LibroHoja`) y otras subcolecciones de forma recursiva, tratando a ambos de manera uniforme (`biblioteca/colecciones/composite.py`).
- **Por qué:** permite recorrer y contar libros de una jerarquía sin distinguir hojas de contenedores.

## 💼 Reglas de negocio

Moneda: soles (S/).

| Tipo de usuario | Días extra de plazo | Máx. libros | Multa |
|---|---|---|---|
| Estándar (por defecto) | +0 | 3 | ×1.0 |
| Estudiante | +7 | 4 | ×1.0 |
| Docente | +14 | 6 | ×0.5 |
| Externo | +0 | 2 | ×1.5 |

- **Plazo** = días del formato del libro (físico 7, digital 14, audiolibro 10) + días de la política + días de servicios extra.
- **Multa** = días de retraso × tarifa del formato (físico S/ 1.00, digital S/ 0.50, audiolibro S/ 0.75 por día) × factor de la política, con tope de 30 días.
- Con multa pendiente **no se puede pedir otro libro**.
- `ServicioPrestamos.actualizar_vencidos(hoy)` pasa a *Vencido* los préstamos fuera de plazo y avisa al usuario.
- Un libro reservado solo lo retira quien recibió la notificación; si no lo retira, la reserva vence y pasa al siguiente.

## 🗂️ Estructura del proyecto

```
.
├── biblioteca/
│   ├── errores.py          # BibliotecaError, OperacionInvalida
│   ├── usuarios.py         # Usuario
│   ├── libros/             # Libro, catálogo, categorías, Factory Method
│   ├── politicas/          # Políticas por tipo de usuario (Factory Method)
│   ├── prestamos/          # Préstamo, estados (State), multas, servicio
│   ├── reservas/           # Reservas y Observer
│   ├── colecciones/        # Composite
│   └── servicios/          # Decorator (servicios extra del préstamo)
├── tests/                  # 63 pruebas con pytest
├── main.py                 # Demo por consola
├── interfaz.py             # Interfaz web local (librería estándar)
├── pytest.ini
└── requirements.txt
```

## 🧪 Pruebas

```bash
py -m pytest
```

63 pruebas que cubren: libros, políticas, préstamos, vencimientos, reservas, observer, colecciones y servicios extra.

## 🔧 Cómo extender el sistema

**Agregar un nuevo tipo de usuario sin modificar código existente** (Factory Method):

```python
from biblioteca.politicas import registrar_tipo, PoliticaCreator

@registrar_tipo("jubilado")
class JubiladoCreator(PoliticaCreator):
    ...  # define su política (días extra, máximo de libros, factor de multa)
```

Ver el ejemplo completo en `tests/test_politicas.py`.

**Agregar un servicio extra al préstamo** (Decorator): crear una subclase de `ServicioAdicional` en `biblioteca/servicios/decorators.py`.

---

📌 **Repositorio:** https://github.com/ariLaz03/sistema-biblioteca-publica-dise-o-patrones-2026
