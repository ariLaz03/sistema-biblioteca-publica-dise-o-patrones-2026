
import unittest

from colecciones.composite import Libro, Coleccion


class TestColecciones(unittest.TestCase):

    def setUp(self):
        self.biblioteca = Coleccion("Biblioteca")
        self.literatura = Coleccion("Literatura")
        self.libro = Libro("Los ríos profundos", "José María Arguedas")

    def test_agregar_libro(self):
        self.literatura.agregar(self.libro)

        self.assertIn(
            self.libro,
            self.literatura.listar_elementos()
        )

    def test_agregar_subcoleccion(self):
        self.biblioteca.agregar(self.literatura)

        self.assertIn(
            self.literatura,
            self.biblioteca.listar_elementos()
        )

    def test_eliminar_elemento(self):
        self.literatura.agregar(self.libro)

        resultado = self.literatura.eliminar(self.libro)

        self.assertTrue(resultado)
        self.assertNotIn(self.libro, self.literatura.listar_elementos())

    def test_no_permitir_ciclo(self):
        self.biblioteca.agregar(self.literatura)

        with self.assertRaises(ValueError):
            self.literatura.agregar(self.biblioteca)

    def test_no_permitir_elementos_invalidos(self):
        with self.assertRaises(TypeError):
            self.biblioteca.agregar("No es un libro ni una colección")


if __name__ == "__main__":
    unittest.main()
