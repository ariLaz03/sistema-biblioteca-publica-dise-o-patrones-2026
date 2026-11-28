
from colecciones.decorator import (
    PrestamoBasico,
    ExtensionPlazo,
    ProteccionMaterial
)


def crear_prestamo_con_servicios(
    libro,
    costo_base=0.0,
    extension=False,
    dias_adicionales=7,
    costo_extension=0.0,
    proteccion=False,
    costo_proteccion=0.0
):
    # Crear préstamo original
    prestamo = PrestamoBasico(libro, costo_base)

    # Agregar extensión de plazo si fue solicitada
    if extension:
        prestamo = ExtensionPlazo(
            prestamo,
            dias_adicionales,
            costo_extension
        )

    # Agregar protección si fue solicitada
    if proteccion:
        prestamo = ProteccionMaterial(
            prestamo,
            costo_proteccion
        )

    return prestamo
