from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models.Bitacora import BitacoraRecuperacion


class BitacoraService:
    def RegistrarRecuperacion(
        self,
        SesionBD: Session,
        TipoEntidad: str,
        EntidadId: int,
        UsuarioId: Optional[int],
        Detalle: Optional[str] = None,
        Momento: Optional[datetime] = None,
    ) -> BitacoraRecuperacion:
        Entrada = BitacoraRecuperacion(
            TipoEntidad=TipoEntidad,
            EntidadId=EntidadId,
            UsuarioId=UsuarioId,
            Detalle=Detalle,
            RegistradoEn=Momento or datetime.utcnow(),
        )
        SesionBD.add(Entrada)
        return Entrada

    def ListarRecuperaciones(
        self,
        SesionBD: Session,
        TipoEntidad: Optional[str] = None,
        UsuarioId: Optional[int] = None,
    ) -> List[BitacoraRecuperacion]:
        Consulta = select(BitacoraRecuperacion)
        if TipoEntidad:
            Consulta = Consulta.where(BitacoraRecuperacion.TipoEntidad == TipoEntidad)
        if UsuarioId is not None:
            Consulta = Consulta.where(BitacoraRecuperacion.UsuarioId == UsuarioId)
        Consulta = Consulta.order_by(BitacoraRecuperacion.RegistradoEn.desc())
        return list(SesionBD.exec(Consulta))
