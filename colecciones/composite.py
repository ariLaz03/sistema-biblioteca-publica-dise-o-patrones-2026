
from abc import ABC, abstractmethod


# COMPONENT: Elemento base de la biblioteca
class ElementoBiblioteca(ABC):

    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def mostrar(self, nivel=0):
        pass


# LEAF: Representa un libro individual
class Libro(ElementoBiblioteca):

    def __init__(self, titulo, autor, isbn=""):
        super().__init__(titulo)
        self.autor = autor
        self.isbn = isbn

    def mostrar(self, nivel=0):
        espacio = "    " * nivel
        print(f"{espacio}Libro: {self.nombre} - Autor: {self.autor}")


# COMPOSITE: Representa una colección de libros
# y otras subcolecciones
class Coleccion(ElementoBiblioteca):

    def __init__(self, nombre, descripcion=""):
        super().__init__(nombre)
        self.descripcion = descripcion
        self.elementos = []

    def agregar(self, elemento):

        if not isinstance(elemento, ElementoBiblioteca):
            raise TypeError(
                "Solo se pueden agregar libros o colecciones."
            )

        if elemento is self:
            raise ValueError(
                "Una colección no puede contenerse a sí misma."
            )

        if isinstance(elemento, Coleccion) and elemento._contiene(self):
            raise ValueError(
                "No se permiten estructuras circulares."
            )

        if self._contiene(elemento):
            raise ValueError(
                "El elemento ya pertenece a esta estructura."
            )

        self.elementos.append(elemento)

    def eliminar(self, elemento):
        if elemento in self.elementos:
            self.elementos.remove(elemento)
            return True

        return False

    def _contiene(self, elemento):
        for hijo in self.elementos:

            if hijo is elemento:
                return True

            if isinstance(hijo, Coleccion):
                if hijo._contiene(elemento):
                    return True

        return False

    def listar_elementos(self):
        return self.elementos.copy()

    def mostrar(self, nivel=0):
        espacio = "    " * nivel

        print(f"{espacio}Colección: {self.nombre}")

        for elemento in self.elementos:
            elemento.mostrar(nivel + 1)
