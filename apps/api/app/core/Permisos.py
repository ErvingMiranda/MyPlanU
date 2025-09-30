from enum import Enum
from typing import Set


class RolParticipante(str, Enum):
    Dueno = "Dueno"
    Colaborador = "Colaborador"
    Lector = "Lector"


_PERMISOS_ROL: dict[RolParticipante, Set[str]] = {
    RolParticipante.Dueno: {"crear", "leer", "actualizar", "eliminar", "recuperar"},
    RolParticipante.Colaborador: {"crear", "leer", "actualizar"},
    RolParticipante.Lector: {"leer"},
}


def EsRolValido(valor: str) -> bool:
    return valor in {RolParticipante.Dueno, RolParticipante.Colaborador, RolParticipante.Lector}


def TienePermiso(rol: RolParticipante | None, accion: str) -> bool:
    if rol is None:
        return False
    return accion in _PERMISOS_ROL.get(rol, set())
