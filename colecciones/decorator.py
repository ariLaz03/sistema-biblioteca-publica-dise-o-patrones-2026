
from abc import ABC, abstractmethod


# COMPONENT: Contrato común de los préstamos
class Prestamo(ABC):
    @abstractmethod
    def descripcion(self):
        pass

    @abstractmethod
    def costo_total(self):
        pass


# CONCRETE COMPONENT: Préstamo básico
class PrestamoBasico(Prestamo):
    def __init__(self, libro, costo=0.0):
        self.libro = libro
        self.costo = float(costo)

    def descripcion(self):
        return f"Préstamo básico del libro: {self.libro}"

    def costo_total(self):
        return self.costo


# DECORATOR: Clase base para servicios adicionales
class ServicioAdicional(Prestamo):
    def __init__(self, prestamo, costo_adicional=0.0):
        if not isinstance(prestamo, Prestamo):
            raise TypeError("Se requiere un préstamo válido.")

        self.prestamo = prestamo
        self.costo_adicional = float(costo_adicional)

        if self.costo_adicional < 0:
            raise ValueError("El costo adicional no puede ser negativo.")

    def descripcion(self):
        return self.prestamo.descripcion()

    def costo_total(self):
        return self.prestamo.costo_total() + self.costo_adicional


# CONCRETE DECORATOR: Extensión del plazo
class ExtensionPlazo(ServicioAdicional):
    def __init__(self, prestamo, dias_adicionales=7, costo_adicional=0.0):
        if dias_adicionales <= 0:
            raise ValueError("Los días adicionales deben ser positivos.")

        super().__init__(prestamo, costo_adicional)
        self.dias_adicionales = dias_adicionales

    def descripcion(self):
        return (
            f"{self.prestamo.descripcion()} "
            f"+ Extensión de {self.dias_adicionales} días"
        )


# CONCRETE DECORATOR: Protección especial del material
class ProteccionMaterial(ServicioAdicional):
    def descripcion(self):
        return (
            f"{self.prestamo.descripcion()} "
            "+ Protección especial del material"
        )
