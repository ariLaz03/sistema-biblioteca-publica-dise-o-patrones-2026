
from colecciones.composite import Libro, Coleccion

# Crear colección principal
biblioteca = Coleccion(
    "Biblioteca Pública",
    "Colección general"
)

# Crear subcolecciones
literatura = Coleccion("Literatura")
ciencias = Coleccion("Ciencias")

literatura_peruana = Coleccion("Literatura peruana")

# Crear libros
libro1 = Libro("Los ríos profundos", "José María Arguedas")
libro2 = Libro("Tradiciones peruanas", "Ricardo Palma")
libro3 = Libro("Introducción a la física", "Varios autores")

# Organizar las colecciones
biblioteca.agregar(literatura)
biblioteca.agregar(ciencias)

literatura.agregar(literatura_peruana)
literatura_peruana.agregar(libro1)
literatura_peruana.agregar(libro2)

ciencias.agregar(libro3)

# Mostrar toda la biblioteca
biblioteca.mostrar()
