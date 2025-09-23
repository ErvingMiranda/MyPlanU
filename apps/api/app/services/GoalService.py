from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models.Goal import Usuario, Meta


class UsuarioServicio:
    def Crear(self, SesionBD: Session, Correo: str, Nombre: str) -> Usuario:
        UsuarioNuevo = Usuario(Correo=Correo, Nombre=Nombre)
        SesionBD.add(UsuarioNuevo)
        SesionBD.commit()
        SesionBD.refresh(UsuarioNuevo)
        return UsuarioNuevo

    def Listar(self, SesionBD: Session) -> List[Usuario]:
        Consulta = select(Usuario).where(Usuario.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Usuario]:
        return SesionBD.get(Usuario, Id)

    def Actualizar(self, SesionBD: Session, Id: int, Correo: Optional[str] = None, Nombre: Optional[str] = None) -> Optional[Usuario]:
        Entidad = SesionBD.get(Usuario, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if Correo is not None:
            Entidad.Correo = Correo
        if Nombre is not None:
            Entidad.Nombre = Nombre
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def Eliminar(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(Usuario, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        return True


class MetaServicio:
    def Crear(self, SesionBD: Session, PropietarioId: int, Titulo: str, TipoMeta: str, Descripcion: Optional[str] = None) -> Optional[Meta]:
        # Validar que el propietario exista y no este eliminado
        Propietario = SesionBD.get(Usuario, PropietarioId)
        if Propietario is None or Propietario.EliminadoEn is not None:
            return None
        MetaNueva = Meta(PropietarioId=PropietarioId, Titulo=Titulo, Descripcion=Descripcion, TipoMeta=TipoMeta)
        SesionBD.add(MetaNueva)
        SesionBD.commit()
        SesionBD.refresh(MetaNueva)
        return MetaNueva

    def Listar(self, SesionBD: Session) -> List[Meta]:
        Consulta = select(Meta).where(Meta.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Meta]:
        return SesionBD.get(Meta, Id)

    def Actualizar(self, SesionBD: Session, Id: int, Titulo: Optional[str] = None, Descripcion: Optional[str] = None, TipoMeta: Optional[str] = None) -> Optional[Meta]:
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

    def Eliminar(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(Meta, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        return True
