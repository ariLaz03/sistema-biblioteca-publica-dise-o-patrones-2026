# Sistema de Biblioteca Pública – Patrones de diseño

Proyecto en Python 3.10+ (proyecto 9 del enunciado) que aplica 5 patrones de diseño integrados.

| Integrante | Módulo | Patrón |
|---|---|---|
| 1 – Libros y catálogo | `biblioteca/libros/`, `biblioteca/politicas/` | **Factory Method**: tipos de libro y **políticas de préstamo por tipo de usuario** |
| 2 – Préstamos y devoluciones | `biblioteca/prestamos/` | **State**: Disponible, Prestado, Vencido, Reservado + multas |
| 3 – Reservas y notificaciones | `biblioteca/reservas/` | **Observer** |
| 4 – Colecciones y servicios | `biblioteca/colecciones/`, `biblioteca/servicios/` | **Composite** y **Decorator** |

## Instalación y uso
```bash
pip install -r requirements.txt     # solo pytest
py main.py                          # demo por consola (Windows) · python main.py en Linux/Mac
py interfaz.py                      # interfaz web en http://localhost:8000
py -m pytest                        # 63 pruebas
```

## Cómo se conectan los patrones
- **Factory Method (políticas):** `creador_politica_para("docente").crear_usuario("Marta")` crea un usuario con su política (días extra de plazo, máximo de libros y factor de multa). Un nuevo tipo de usuario se agrega **sin modificar código existente**: basta una clase política y un creador con `@registrar_tipo("jubilado")` (ver `tests/test_politicas.py`).
- **Factory Method (libros):** `creador_para("digital").registrar(catalogo, ...)` crea libros físicos, digitales o audiolibros.
- **State:** `Libro` es el contexto. Estados: `Disponible → Prestado → Vencido` y `Reservado`. Cada estado define qué operaciones permite (un libro vencido solo se puede devolver).
- **Observer:** al devolverse un libro, `notificar_disponible()` avisa al `ObservadorReservas`, que aparta el libro (`Reservado`) para el primero de la cola FIFO y le envía la notificación.
- **Decorator:** `Prestamo` guarda un `DetallePrestamo` envuelto por servicios (renovación prioritaria, entrega a domicilio, seguro) que suman costo y días.
- **Composite:** `Coleccion` agrupa libros y subcolecciones de forma recursiva.

## Reglas de negocio (moneda: soles, S/)
| Tipo de usuario | Días extra de plazo | Máx. libros | Multa |
|---|---|---|---|
| Estándar (por defecto) | +0 | 3 | ×1.0 |
| Estudiante | +7 | 4 | ×1.0 |
| Docente | +14 | 6 | ×0.5 |
| Externo | +0 | 2 | ×1.5 |

- Plazo = días del formato del libro (físico 7, digital 14, audiolibro 10) + días de la política + días de servicios extra.
- Multa = días de retraso × tarifa del formato (físico S/ 1.00, digital S/ 0.50, audiolibro S/ 0.75 por día) × factor de la política, con tope de 30 días.
- Con multa pendiente no se puede pedir otro libro.
- `ServicioPrestamos.actualizar_vencidos(hoy)` pasa a *Vencido* los préstamos fuera de plazo y avisa al usuario.
- Un libro reservado solo lo retira quien recibió la notificación; si no lo retira, la reserva vence y pasa al siguiente.

## Estructura
```
biblioteca/  libros/ politicas/ prestamos/ reservas/ colecciones/ servicios/
tests/       libros, politicas, prestamos, vencido, reservas, observer, colecciones, servicios
main.py      interfaz.py      pytest.ini      requirements.txt
```
