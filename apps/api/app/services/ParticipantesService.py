from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models.Evento import Evento, ParticipanteEvento
from app.models.Goal import Usuario
from app.core.Permisos import RolParticipante


class ParticipantesService:
    def ListarPorEvento(self, SesionBD: Session, EventoId: int) -> List[ParticipanteEvento]:
        Consulta = select(ParticipanteEvento).where(ParticipanteEvento.EventoId == EventoId)
        return list(SesionBD.exec(Consulta))

    def _ContarDuenos(self, SesionBD: Session, EventoId: int) -> int:
        Consulta = select(ParticipanteEvento).where(ParticipanteEvento.EventoId == EventoId, ParticipanteEvento.Rol == 'Dueno')
        return len(list(SesionBD.exec(Consulta)))

    def AgregarParticipante(self, SesionBD: Session, EventoId: int, UsuarioId: int, Rol: RolParticipante) -> Optional[ParticipanteEvento]:
        # Validar existencia
        if SesionBD.get(Evento, EventoId) is None:
            return None
        if SesionBD.get(Usuario, UsuarioId) is None:
            return None
        # Regla: exactamente un Dueno
        if Rol == RolParticipante.Dueno:
            if self._ContarDuenos(SesionBD, EventoId) >= 1:
                return None
        Entidad = ParticipanteEvento(EventoId=EventoId, UsuarioId=UsuarioId, Rol=Rol.value, CreadoEn=datetime.utcnow())
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def CambiarRol(self, SesionBD: Session, Id: int, NuevoRol: RolParticipante) -> Optional[ParticipanteEvento]:
        Entidad = SesionBD.get(ParticipanteEvento, Id)
        if Entidad is None:
            return None
        if NuevoRol == RolParticipante.Dueno:
            # Asegurar unicidad de Dueno
            if self._ContarDuenos(SesionBD, Entidad.EventoId) >= 1 and Entidad.Rol != 'Dueno':
                return None
        Entidad.Rol = NuevoRol.value
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def QuitarParticipante(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(ParticipanteEvento, Id)
        if Entidad is None:
            return False
        if Entidad.Rol == 'Dueno':
            # No permitir quitar Dueno sin transferencia
            return False
        SesionBD.delete(Entidad)
        SesionBD.commit()
        return True
