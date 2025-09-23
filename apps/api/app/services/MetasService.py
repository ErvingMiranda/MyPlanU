from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models.Goal import Meta
from app.services.UsuariosService import UsuariosService


class MetasService:
    # TODO(roles): validar permisos por rol (Dueno, Colaborador, Lector)
    # TODO(cascada): definir comportamiento de cascada logica hacia Eventos y Recordatorios cuando se elimine una Meta

    def __init__(self) -> None:
        self.Usuarios = UsuariosService()

    def CrearMeta(self, SesionBD: Session, PropietarioId: int, Titulo: str, TipoMeta: str, Descripcion: Optional[str] = None) -> Optional[Meta]:
        # Validar propietario
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

    def ActualizarMeta(self, SesionBD: Session, Id: int, Titulo: Optional[str] = None, Descripcion: Optional[str] = None, TipoMeta: Optional[str] = None) -> Optional[Meta]:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
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

    def EliminarMeta(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        return True

    def RecuperarMeta(self, SesionBD: Session, Id: int) -> Optional[Meta]:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad:
            return None
        if Entidad.EliminadoEn is None:
            return Entidad  # ya activa
        # Reglas: verificar propietario existe (no eliminamos usuarios en este proyecto)
        # TODO(bitacora): registrar quien y cuando recupera
        Entidad.EliminadoEn = None
        Entidad.ActualizadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad
