from typing import List, Optional, Set
from datetime import datetime

from sqlmodel import Session, select

from app.models.Evento import Evento, ParticipanteEvento
from app.models.Goal import Usuario, Meta
from app.core.Permisos import RolParticipante


class ParticipantesService:
    def ListarPorEvento(self, SesionBD: Session, EventoId: int) -> List[ParticipanteEvento]:
        Consulta = select(ParticipanteEvento).where(ParticipanteEvento.EventoId == EventoId)
        return list(SesionBD.exec(Consulta))

    def _ContarDuenos(self, SesionBD: Session, EventoId: int) -> int:
        Consulta = select(ParticipanteEvento).where(
            ParticipanteEvento.EventoId == EventoId,
            ParticipanteEvento.Rol == RolParticipante.Dueno.value,
        )
        return len(list(SesionBD.exec(Consulta)))

    def AgregarParticipante(
        self,
        SesionBD: Session,
        EventoId: int,
        UsuarioId: int,
        Rol: RolParticipante,
    ) -> Optional[ParticipanteEvento]:
        # Validar existencia
        if SesionBD.get(Evento, EventoId) is None:
            return None
        if SesionBD.get(Usuario, UsuarioId) is None:
            return None
        # Regla: exactamente un Dueno
        if Rol == RolParticipante.Dueno and self._ContarDuenos(SesionBD, EventoId) >= 1:
            return None
        Entidad = ParticipanteEvento(
            EventoId=EventoId,
            UsuarioId=UsuarioId,
            Rol=Rol.value,
            CreadoEn=datetime.utcnow(),
        )
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def CambiarRol(self, SesionBD: Session, Id: int, NuevoRol: RolParticipante) -> Optional[ParticipanteEvento]:
        Entidad = SesionBD.get(ParticipanteEvento, Id)
        if Entidad is None:
            return None
        if NuevoRol == RolParticipante.Dueno and self._ContarDuenos(SesionBD, Entidad.EventoId) >= 1 and Entidad.Rol != 'Dueno':
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

    def ObtenerRolEnEvento(self, SesionBD: Session, EventoId: int, UsuarioId: int) -> Optional[RolParticipante]:
        EventoEntidad = SesionBD.get(Evento, EventoId)
        if EventoEntidad is None or EventoEntidad.EliminadoEn is not None:
            return None
        if EventoEntidad.PropietarioId == UsuarioId:
            return RolParticipante.Dueno
        Consulta = select(ParticipanteEvento).where(
            ParticipanteEvento.EventoId == EventoId,
            ParticipanteEvento.UsuarioId == UsuarioId,
        )
        Participante = SesionBD.exec(Consulta).first()
        if Participante is None:
            return None
        try:
            return RolParticipante(Participante.Rol)
        except ValueError:
            return None

    def RolEnMeta(self, SesionBD: Session, MetaEntidad: Meta, UsuarioId: int) -> Optional[RolParticipante]:
        if MetaEntidad.PropietarioId == UsuarioId:
            return RolParticipante.Dueno
        Consulta = (
            select(ParticipanteEvento)
            .join(Evento, Evento.Id == ParticipanteEvento.EventoId)
            .where(Evento.MetaId == MetaEntidad.Id, ParticipanteEvento.UsuarioId == UsuarioId)
        )
        roles_prioridad: Set[str] = set()
        for registro in SesionBD.exec(Consulta):
            roles_prioridad.add(registro.Rol)
            if registro.Rol == RolParticipante.Colaborador.value:
                return RolParticipante.Colaborador
        if RolParticipante.Dueno.value in roles_prioridad:
            return RolParticipante.Dueno
        if RolParticipante.Lector.value in roles_prioridad:
            return RolParticipante.Lector
        return None

    def MetaTieneColaborador(self, SesionBD: Session, MetaId: int) -> bool:
        Consulta = (
            select(ParticipanteEvento)
            .join(Evento, Evento.Id == ParticipanteEvento.EventoId)
            .where(Evento.MetaId == MetaId, ParticipanteEvento.Rol == RolParticipante.Colaborador.value)
        )
        return SesionBD.exec(Consulta).first() is not None

    def AsegurarDuenoEvento(self, SesionBD: Session, EventoId: int, UsuarioId: int) -> Optional[ParticipanteEvento]:
        Consulta = select(ParticipanteEvento).where(
            ParticipanteEvento.EventoId == EventoId,
            ParticipanteEvento.UsuarioId == UsuarioId,
        )
        existente = SesionBD.exec(Consulta).first()
        if existente:
            if existente.Rol != RolParticipante.Dueno.value:
                existente.Rol = RolParticipante.Dueno.value
                SesionBD.add(existente)
                SesionBD.commit()
                SesionBD.refresh(existente)
            return existente
        return self.AgregarParticipante(SesionBD, EventoId, UsuarioId, RolParticipante.Dueno)
