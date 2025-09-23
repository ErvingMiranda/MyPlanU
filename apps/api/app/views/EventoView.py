from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.services.EventosService import EventosService, RecordatoriosService
from app.services.ParticipantesService import ParticipantesService
from app.core.Permisos import RolParticipante


Router = APIRouter()
Eventos = EventosService()
Recordatorios = RecordatoriosService()
Participantes = ParticipantesService()


@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()


# Eventos
@Router.get("/eventos")
def ListarEventos(SesionBD: Session = Depends(ObtenerSesion)):
    return Eventos.ListarEventos(SesionBD)


@Router.post("/eventos")
def CrearEvento(
    MetaId: int,
    PropietarioId: int,
    Titulo: str,
    Inicio: datetime,
    Fin: datetime,
    Descripcion: Optional[str] = None,
    Ubicacion: Optional[str] = None,
    Rol: RolParticipante = RolParticipante.Dueno,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Eventos.CrearEvento(
        SesionBD,
        MetaId=MetaId,
        PropietarioId=PropietarioId,
        Titulo=Titulo,
        Inicio=Inicio,
        Fin=Fin,
        Descripcion=Descripcion,
        Ubicacion=Ubicacion,
        Rol=Rol,
    )
    if Entidad is None:
        raise HTTPException(status_code=400, detail="Datos invalidos (Meta/Propietario inexistentes o Inicio >= Fin)")
    return Entidad


@Router.get("/eventos/{Id}")
def ObtenerEvento(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Eventos.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return Entidad


@Router.patch("/eventos/{Id}")
def ActualizarEvento(
    Id: int,
    Titulo: Optional[str] = None,
    Descripcion: Optional[str] = None,
    Inicio: Optional[datetime] = None,
    Fin: Optional[datetime] = None,
    Ubicacion: Optional[str] = None,
    Rol: RolParticipante = RolParticipante.Dueno,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Eventos.ActualizarEvento(
        SesionBD, Id, Titulo=Titulo, Descripcion=Descripcion, Inicio=Inicio, Fin=Fin, Ubicacion=Ubicacion, Rol=Rol
    )
    if Entidad is None:
        raise HTTPException(status_code=400, detail="Evento no encontrado o valido (Inicio < Fin)")
    return Entidad


@Router.delete("/eventos/{Id}")
def EliminarEvento(Id: int, Rol: RolParticipante = RolParticipante.Dueno, SesionBD: Session = Depends(ObtenerSesion)):
    Exito = Eventos.EliminarEvento(SesionBD, Id, Rol=Rol)
    if not Exito:
        raise HTTPException(status_code=403, detail="No permitido o evento no encontrado")
    return {"ok": True}


# Recordatorios
@Router.get("/recordatorios")
def ListarRecordatorios(SesionBD: Session = Depends(ObtenerSesion)):
    return Recordatorios.ListarRecordatorios(SesionBD)


@Router.post("/recordatorios")
def CrearRecordatorio(
    EventoId: int,
    FechaHora: datetime,
    Canal: str,
    Mensaje: Optional[str] = None,
    Rol: RolParticipante = RolParticipante.Dueno,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Recordatorios.CrearRecordatorio(
        SesionBD,
        EventoId=EventoId,
        FechaHora=FechaHora,
        Canal=Canal,
        Mensaje=Mensaje,
        Rol=Rol,
    )
    if Entidad is None:
        raise HTTPException(status_code=400, detail="Datos invalidos (evento inexistente o FechaHora en pasado)")
    return Entidad


@Router.get("/recordatorios/{Id}")
def ObtenerRecordatorio(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Recordatorios.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    return Entidad


@Router.patch("/recordatorios/{Id}")
def ActualizarRecordatorio(
    Id: int,
    FechaHora: Optional[datetime] = None,
    Canal: Optional[str] = None,
    Enviado: Optional[bool] = None,
    Mensaje: Optional[str] = None,
    Rol: RolParticipante = RolParticipante.Dueno,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Recordatorios.ActualizarRecordatorio(
        SesionBD,
        Id,
        FechaHora=FechaHora,
        Canal=Canal,
        Enviado=Enviado,
        Mensaje=Mensaje,
        Rol=Rol,
    )
    if Entidad is None:
        raise HTTPException(status_code=400, detail="Recordatorio no encontrado o invalido (FechaHora en pasado)")
    return Entidad


@Router.delete("/recordatorios/{Id}")
def EliminarRecordatorio(Id: int, Rol: RolParticipante = RolParticipante.Dueno, SesionBD: Session = Depends(ObtenerSesion)):
    Exito = Recordatorios.EliminarRecordatorio(SesionBD, Id, Rol=Rol)
    if not Exito:
        raise HTTPException(status_code=403, detail="No permitido o recordatorio no encontrado")
    return {"ok": True}


@Router.get("/recordatorios/proximos")
def ListarRecordatoriosProximos(dias: int = 7, SesionBD: Session = Depends(ObtenerSesion)):
    if dias <= 0:
        dias = 7
    return Recordatorios.ListarProximos(SesionBD, dias=dias)


# Participantes de Evento
@Router.get("/eventos/{EventoId}/participantes")
def ListarParticipantes(EventoId: int, SesionBD: Session = Depends(ObtenerSesion)):
    return Participantes.ListarPorEvento(SesionBD, EventoId)


@Router.post("/eventos/{EventoId}/participantes")
def AgregarParticipante(EventoId: int, UsuarioId: int, Rol: RolParticipante, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Participantes.AgregarParticipante(SesionBD, EventoId=EventoId, UsuarioId=UsuarioId, Rol=Rol)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="No se pudo agregar participante (valida Dueno unico/evento/usuario)")
    return Entidad


@Router.patch("/participantes/{Id}")
def CambiarRolParticipante(Id: int, Rol: RolParticipante, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Participantes.CambiarRol(SesionBD, Id, Rol)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="No se pudo cambiar rol (Dueno unico o participante inexistente)")
    return Entidad


@Router.delete("/participantes/{Id}")
def QuitarParticipante(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Exito = Participantes.QuitarParticipante(SesionBD, Id)
    if not Exito:
        raise HTTPException(status_code=400, detail="No se pudo quitar (no se puede eliminar Dueno sin transferencia)")
    return {"ok": True}
