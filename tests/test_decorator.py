
import unittest

from colecciones.decorator import (
    PrestamoBasico,
    ExtensionPlazo,
    ProteccionMaterial
)

from colecciones.servicios import crear_prestamo_con_servicios


class TestDecorator(unittest.TestCase):

    def test_prestamo_basico(self):
        prestamo = PrestamoBasico("Los ríos profundos")
        self.assertEqual(prestamo.costo_total(), 0.0)
        self.assertIn("Los ríos profundos", prestamo.descripcion())

    def test_extension_plazo(self):
        prestamo = PrestamoBasico("Tradiciones peruanas")
        prestamo = ExtensionPlazo(prestamo, 7, 5)
        self.assertEqual(prestamo.costo_total(), 5.0)
        self.assertIn("7 días", prestamo.descripcion())

    def test_proteccion_material(self):
        prestamo = PrestamoBasico("Libro de ciencias")
        prestamo = ProteccionMaterial(prestamo, 3)
        self.assertEqual(prestamo.costo_total(), 3.0)
        self.assertIn("Protección especial", prestamo.descripcion())

    def test_combinar_servicios(self):
        prestamo = crear_prestamo_con_servicios(
            libro="Libro de historia",
            extension=True,
            dias_adicionales=10,
            costo_extension=5,
            proteccion=True,
            costo_proteccion=3
        )
        self.assertEqual(prestamo.costo_total(), 8.0)
        self.assertIn("Extensión de 10 días", prestamo.descripcion())
        self.assertIn("Protección especial", prestamo.descripcion())

    def test_no_permitir_costos_negativos(self):
        prestamo = PrestamoBasico("Libro de prueba")
        with self.assertRaises(ValueError):
            ExtensionPlazo(prestamo, costo_adicional=-5)


if __name__ == "__main__":
    unittest.main()
