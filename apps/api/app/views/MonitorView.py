from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.Database import ObtenerSesion
from app.views.AuthView import get_current_user
from app.models.Goal import Usuario
from app.models.Notificacion import NotificacionSistema
from app.services.BitacoraService import BitacoraService
from app.services.NotificacionesService import NotificacionesService

Router = APIRouter()
Bitacora = BitacoraService()
Notificaciones = NotificacionesService()


@Router.get("/bitacora/recuperaciones")
def ListarRecuperaciones(
    TipoEntidad: Optional[str] = None,
    SoloPropias: bool = True,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    usuario_id = UsuarioActual.Id if SoloPropias else None
    registros = Bitacora.ListarRecuperaciones(
        SesionBD,
        TipoEntidad=TipoEntidad,
        UsuarioId=usuario_id,
    )
    return [registro.model_dump() for registro in registros]


@Router.get("/notificaciones/sistema")
def ListarNotificaciones(
    SoloNoLeidas: bool = True,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    registros = Notificaciones.ListarPendientes(
        SesionBD,
        UsuarioId=UsuarioActual.Id,
        SoloNoLeidas=SoloNoLeidas,
    )
    return [registro.model_dump() for registro in registros]


@Router.post("/notificaciones/{Id}/leer")
def MarcarNotificacionLeida(
    Id: int,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    notificacion = SesionBD.get(NotificacionSistema, Id)
    if not notificacion or notificacion.UsuarioId != UsuarioActual.Id:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    if Notificaciones.MarcarLeida(SesionBD, Id):
        SesionBD.commit()
        return {"ok": True}
    raise HTTPException(status_code=400, detail="No se pudo marcar notificacion")
