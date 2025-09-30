from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models.Goal import Usuario
from app.models.Evento import ParticipanteEvento


class UsuariosService:
    # TODO(roles): validar permisos por rol (Dueno, Colaborador, Lector)
    # TODO(cascada): definir comportamiento de cascada logica hacia Eventos y Recordatorios

    def Crear(self, SesionBD: Session, Correo: str, Nombre: str, ZonaHoraria: str = 'UTC') -> Optional[Usuario]:
        # Validar existencia por correo para evitar duplicados
        if self.Existe(SesionBD, Correo=Correo):
            return None
        Entidad = Usuario(Correo=Correo, Nombre=Nombre, ZonaHoraria=ZonaHoraria)
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def Listar(self, SesionBD: Session) -> List[Usuario]:
        Consulta = select(Usuario).where(Usuario.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Usuario]:
        return SesionBD.get(Usuario, Id)

    def Actualizar(
        self,
        SesionBD: Session,
        Id: int,
        Correo: Optional[str] = None,
        Nombre: Optional[str] = None,
        ZonaHoraria: Optional[str] = None,
    ) -> Optional[Usuario]:
        Entidad = SesionBD.get(Usuario, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if Correo is not None:
            Entidad.Correo = Correo
        if Nombre is not None:
            Entidad.Nombre = Nombre
        if ZonaHoraria is not None:
            Entidad.ZonaHoraria = ZonaHoraria
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def Eliminar(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(Usuario, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        fecha = datetime.utcnow()
        Entidad.EliminadoEn = fecha
        SesionBD.add(Entidad)
        from app.services.MetasService import MetasService  # import tardio para evitar ciclo

        metas = MetasService()
        metas.CascadaPorUsuario(SesionBD, Id, fecha)
        ConsultaParticipantes = select(ParticipanteEvento).where(ParticipanteEvento.UsuarioId == Id)
        for participante in SesionBD.exec(ConsultaParticipantes):
            SesionBD.delete(participante)
        SesionBD.commit()
        return True

    def BuscarPorCorreo(self, SesionBD: Session, Correo: str) -> Optional[Usuario]:
        Consulta = select(Usuario).where(Usuario.Correo == Correo, Usuario.EliminadoEn.is_(None))
        return SesionBD.exec(Consulta).first()

    def Existe(self, SesionBD: Session, Id: Optional[int] = None, Correo: Optional[str] = None) -> bool:
        if Id is not None:
            Entidad = SesionBD.get(Usuario, Id)
            return Entidad is not None and Entidad.EliminadoEn is None
        if Correo is not None:
            return self.BuscarPorCorreo(SesionBD, Correo) is not None
        return False
