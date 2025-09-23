from enum import Enum


class RolParticipante(str, Enum):
    Dueno = "Dueno"
    Colaborador = "Colaborador"
    Lector = "Lector"


def EsRolValido(valor: str) -> bool:
    return valor in {RolParticipante.Dueno, RolParticipante.Colaborador, RolParticipante.Lector}
