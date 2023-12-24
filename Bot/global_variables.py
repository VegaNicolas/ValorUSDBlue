from dataclasses import dataclass


@dataclass
class Blue:
    intervalo_blue: float = 0  # Precio del intervalo anterior
    apertura_blue: float = 0
    venta_blue: float = 0


price = Blue()
