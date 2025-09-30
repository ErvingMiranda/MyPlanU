class PermisoDenegadoError(Exception):
    """Se lanza cuando el usuario autenticado no cumple con los permisos requeridos."""

    def __init__(self, detalle: str = "Permiso denegado") -> None:
        super().__init__(detalle)
        self.detalle = detalle


class ReglaNegocioError(Exception):
    """Se lanza cuando una regla de negocio impide completar la operación."""

    def __init__(self, detalle: str) -> None:
        super().__init__(detalle)
        self.detalle = detalle
