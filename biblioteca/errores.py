class BibliotecaError(ValueError):
    """Error base del dominio de la biblioteca."""


class OperacionInvalida(BibliotecaError):
    """Operación no permitida en el estado actual."""
