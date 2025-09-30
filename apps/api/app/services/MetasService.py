from typing import List, Optional, Set
from datetime import datetime

from sqlmodel import Session, select

from app.models.Goal import Meta
from app.models.Evento import Evento, Recordatorio
from app.services.UsuariosService import UsuariosService
from app.services.ParticipantesService import ParticipantesService
from app.services.BitacoraService import BitacoraService
from app.core.Permisos import RolParticipante, TienePermiso
from app.services.exceptions import PermisoDenegadoError, ReglaNegocioError


class MetasService:
    def __init__(self) -> None:
        self.Usuarios = UsuariosService()
        self.Participantes = ParticipantesService()
        self.Bitacora = BitacoraService()

    def _ObtenerRolMeta(self, SesionBD: Session, MetaEntidad: Meta, UsuarioId: int) -> Optional[RolParticipante]:
        return self.Participantes.RolEnMeta(SesionBD, MetaEntidad, UsuarioId)

    def _AplicarCascadaMeta(self, SesionBD: Session, MetaEntidad: Meta, Fecha: datetime) -> Set[int]:
        eventos_afectados: Set[int] = set()
        ConsultaEventos = select(Evento).where(Evento.MetaId == MetaEntidad.Id)
        for evento in SesionBD.exec(ConsultaEventos):
            eventos_afectados.add(evento.Id)
            if evento.EliminadoEn is None:
                evento.EliminadoEn = Fecha
                SesionBD.add(evento)
            ConsultaRecordatorios = select(Recordatorio).where(Recordatorio.EventoId == evento.Id)
            for recordatorio in SesionBD.exec(ConsultaRecordatorios):
                if recordatorio.EliminadoEn is None:
                    recordatorio.EliminadoEn = Fecha
                    SesionBD.add(recordatorio)
        return eventos_afectados

    def CascadaPorUsuario(self, SesionBD: Session, UsuarioId: int, Fecha: datetime) -> None:
        ConsultaMetas = select(Meta).where(Meta.PropietarioId == UsuarioId)
        eventos_cascada = set()
        for meta in SesionBD.exec(ConsultaMetas):
            if meta.EliminadoEn is None:
                meta.EliminadoEn = Fecha
                SesionBD.add(meta)
            eventos_cascada.update(self._AplicarCascadaMeta(SesionBD, meta, Fecha))
        ConsultaEventos = select(Evento).where(Evento.PropietarioId == UsuarioId)
        for evento in SesionBD.exec(ConsultaEventos):
            if evento.Id in eventos_cascada:
                continue
            if evento.EliminadoEn is None:
                evento.EliminadoEn = Fecha
                SesionBD.add(evento)
            ConsultaRecordatorios = select(Recordatorio).where(Recordatorio.EventoId == evento.Id)
            for recordatorio in SesionBD.exec(ConsultaRecordatorios):
                if recordatorio.EliminadoEn is None:
                    recordatorio.EliminadoEn = Fecha
                    SesionBD.add(recordatorio)

    def CrearMeta(
        self,
        SesionBD: Session,
        PropietarioId: int,
        Titulo: str,
        TipoMeta: str,
        Descripcion: Optional[str] = None,
        SolicitanteId: Optional[int] = None,
    ) -> Optional[Meta]:
        if SolicitanteId is not None and SolicitanteId != PropietarioId:
            raise PermisoDenegadoError("MetaInvalida: solo puedes crear metas para ti mismo")
        if not self.Usuarios.Existe(SesionBD, Id=PropietarioId):
            return None
        Entidad = Meta(PropietarioId=PropietarioId, Titulo=Titulo, Descripcion=Descripcion, TipoMeta=TipoMeta)
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def ListarMetas(self, SesionBD: Session) -> List[Meta]:
        Consulta = select(Meta).where(Meta.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def ListarMetasEliminadas(
        self,
        SesionBD: Session,
        PropietarioId: Optional[int] = None,
        Desde: Optional[datetime] = None,
        Hasta: Optional[datetime] = None,
    ) -> List[Meta]:
        Consulta = select(Meta).where(Meta.EliminadoEn.is_not(None))
        if PropietarioId is not None:
            Consulta = Consulta.where(Meta.PropietarioId == PropietarioId)
        if Desde is not None:
            Consulta = Consulta.where(Meta.EliminadoEn >= Desde)
        if Hasta is not None:
            Consulta = Consulta.where(Meta.EliminadoEn <= Hasta)
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Meta]:
        return SesionBD.get(Meta, Id)

    def ActualizarMeta(
        self,
        SesionBD: Session,
        Id: int,
        Titulo: Optional[str] = None,
        Descripcion: Optional[str] = None,
        TipoMeta: Optional[str] = None,
        SolicitanteId: Optional[int] = None,
    ) -> Optional[Meta]:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if SolicitanteId is not None:
            rol = self._ObtenerRolMeta(SesionBD, Entidad, SolicitanteId)
            if not TienePermiso(rol, "actualizar"):
                raise PermisoDenegadoError("MetaInvalida: no tienes permisos para actualizar esta meta")
        if Titulo is not None:
            Entidad.Titulo = Titulo
        if Descripcion is not None:
            Entidad.Descripcion = Descripcion
        if TipoMeta is not None:
            Entidad.TipoMeta = TipoMeta
        Entidad.ActualizadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def EliminarMeta(self, SesionBD: Session, Id: int, SolicitanteId: Optional[int] = None) -> bool:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        if SolicitanteId is not None:
            rol = self._ObtenerRolMeta(SesionBD, Entidad, SolicitanteId)
            if rol != RolParticipante.Dueno:
                raise PermisoDenegadoError("MetaInvalida: solo el Dueno puede eliminar la meta")
        if Entidad.TipoMeta == "Colectiva" and not self.Participantes.MetaTieneColaborador(SesionBD, Entidad.Id):
            raise ReglaNegocioError(
                "MetaInvalida: una meta colectiva requiere al menos un colaborador activo antes de cerrarse"
            )
        ahora = datetime.utcnow()
        Entidad.EliminadoEn = ahora
        SesionBD.add(Entidad)
        self._AplicarCascadaMeta(SesionBD, Entidad, ahora)
        SesionBD.commit()
        return True

    def RecuperarMeta(self, SesionBD: Session, Id: int, SolicitanteId: Optional[int] = None) -> Optional[Meta]:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad:
            return None
        if SolicitanteId is not None:
            rol = self._ObtenerRolMeta(SesionBD, Entidad, SolicitanteId)
            if not TienePermiso(rol, "recuperar"):
                raise PermisoDenegadoError("MetaInvalida: no tienes permisos para recuperar esta meta")
        if Entidad.EliminadoEn is None:
            return Entidad
        momento = datetime.utcnow()
        Entidad.EliminadoEn = None
        Entidad.ActualizadoEn = momento
        detalle = (
            f"Recuperada por usuario {SolicitanteId}"
            if SolicitanteId is not None
            else "Recuperacion sin solicitante"
        )
        self.Bitacora.RegistrarRecuperacion(
            SesionBD,
            "Meta",
            Entidad.Id,
            SolicitanteId,
            Detalle=detalle,
            Momento=momento,
        )
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad
