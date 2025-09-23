from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models.Evento import Evento, Recordatorio
from app.models.Goal import Meta
from app.services.UsuariosService import UsuariosService


class EventosService:
    def __init__(self) -> None:
        self.Usuarios = UsuariosService()

    def CrearEvento(
        self,
        SesionBD: Session,
        MetaId: int,
        PropietarioId: int,
        Titulo: str,
        Inicio: datetime,
        Fin: datetime,
        Descripcion: Optional[str] = None,
        Ubicacion: Optional[str] = None,
    ) -> Optional[Evento]:
        # Validaciones: Inicio < Fin
        if not (Inicio < Fin):
            return None
        # Validar existencia de Meta y Usuario (no eliminados)
        MetaEntidad = SesionBD.get(Meta, MetaId)
        if not MetaEntidad or MetaEntidad.EliminadoEn is not None:
            return None
        if not self.Usuarios.Existe(SesionBD, Id=PropietarioId):
            return None

        Entidad = Evento(
            MetaId=MetaId,
            PropietarioId=PropietarioId,
            Titulo=Titulo,
            Descripcion=Descripcion,
            Inicio=Inicio,
            Fin=Fin,
            Ubicacion=Ubicacion,
        )
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def ListarEventos(self, SesionBD: Session) -> List[Evento]:
        Consulta = select(Evento).where(Evento.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Evento]:
        return SesionBD.get(Evento, Id)

    def ActualizarEvento(
        self,
        SesionBD: Session,
        Id: int,
        Titulo: Optional[str] = None,
        Descripcion: Optional[str] = None,
        Inicio: Optional[datetime] = None,
        Fin: Optional[datetime] = None,
        Ubicacion: Optional[str] = None,
    ) -> Optional[Evento]:
        Entidad = SesionBD.get(Evento, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if Inicio is not None:
            Entidad.Inicio = Inicio
        if Fin is not None:
            Entidad.Fin = Fin
        # Validar ventana de tiempo si ambos estan seteados o cambiaron
        if Entidad.Inicio >= Entidad.Fin:
            return None
        if Titulo is not None:
            Entidad.Titulo = Titulo
        if Descripcion is not None:
            Entidad.Descripcion = Descripcion
        if Ubicacion is not None:
            Entidad.Ubicacion = Ubicacion
        Entidad.ActualizadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def EliminarEvento(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(Evento, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        # Soft delete del evento
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        # Cascada logica: marcar recordatorios relacionados
        Consulta = select(Recordatorio).where(Recordatorio.EventoId == Id, Recordatorio.EliminadoEn.is_(None))
        for Rec in SesionBD.exec(Consulta):
            Rec.EliminadoEn = datetime.utcnow()
            SesionBD.add(Rec)
        SesionBD.commit()
        return True


class RecordatoriosService:
    def CrearRecordatorio(
        self,
        SesionBD: Session,
        EventoId: int,
        FechaHora: datetime,
        Canal: str,
    ) -> Optional[Recordatorio]:
        # No crear en el pasado
        if FechaHora < datetime.utcnow():
            return None
        # Validar evento existe y no eliminado
        EventoEntidad = SesionBD.get(Evento, EventoId)
        if not EventoEntidad or EventoEntidad.EliminadoEn is not None:
            return None
        Entidad = Recordatorio(EventoId=EventoId, FechaHora=FechaHora, Canal=Canal)
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def ListarRecordatorios(self, SesionBD: Session) -> List[Recordatorio]:
        Consulta = select(Recordatorio).where(Recordatorio.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Recordatorio]:
        return SesionBD.get(Recordatorio, Id)

    def ActualizarRecordatorio(
        self,
        SesionBD: Session,
        Id: int,
        FechaHora: Optional[datetime] = None,
        Canal: Optional[str] = None,
        Enviado: Optional[bool] = None,
    ) -> Optional[Recordatorio]:
        Entidad = SesionBD.get(Recordatorio, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if FechaHora is not None:
            if FechaHora < datetime.utcnow():
                return None
            Entidad.FechaHora = FechaHora
        if Canal is not None:
            Entidad.Canal = Canal
        if Enviado is not None:
            Entidad.Enviado = Enviado
        # No hay actualizadoEn en recordatorio por requerimiento
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def EliminarRecordatorio(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(Recordatorio, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        return True
