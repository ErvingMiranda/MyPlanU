from datetime import datetime
from typing import Iterable, List, Optional, Set

from sqlmodel import Session, select

from app.models.Notificacion import NotificacionSistema


class NotificacionesService:
    def RegistrarEventoEliminado(
        self,
        SesionBD: Session,
        EventoId: int,
        UsuariosDestino: Iterable[int],
        Mensaje: str,
        Momento: Optional[datetime] = None,
    ) -> None:
        vistos: Set[int] = set()
        instante = Momento or datetime.utcnow()
        for usuario_id in UsuariosDestino:
            if usuario_id in vistos:
                continue
            vistos.add(usuario_id)
            entrada = NotificacionSistema(
                UsuarioId=usuario_id,
                Tipo="EventoEliminado",
                ReferenciaId=EventoId,
                Mensaje=Mensaje,
                CreadoEn=instante,
            )
            SesionBD.add(entrada)

    def ListarPendientes(
        self,
        SesionBD: Session,
        UsuarioId: int,
        SoloNoLeidas: bool = True,
    ) -> List[NotificacionSistema]:
        Consulta = select(NotificacionSistema).where(NotificacionSistema.UsuarioId == UsuarioId)
        if SoloNoLeidas:
            Consulta = Consulta.where(NotificacionSistema.LeidaEn.is_(None))
        Consulta = Consulta.order_by(NotificacionSistema.CreadoEn.desc())
        return list(SesionBD.exec(Consulta))

    def MarcarLeida(self, SesionBD: Session, Id: int) -> bool:
        Entidad = SesionBD.get(NotificacionSistema, Id)
        if Entidad is None:
            return False
        if Entidad.LeidaEn is None:
            Entidad.LeidaEn = datetime.utcnow()
            SesionBD.add(Entidad)
        return True
