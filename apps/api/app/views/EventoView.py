from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.services.EventosService import EventosService, RecordatoriosService
from app.services.ParticipantesService import ParticipantesService
from app.core.Permisos import RolParticipante
from app.schemas import (
    EventoCrear,
    EventoActualizar,
    EventoRespuesta,
    RecordatorioCrear,
    RecordatorioActualizar,
    RecordatorioRespuesta,
)
from app.services.UsuariosService import UsuariosService
from app.services.exceptions import PermisoDenegadoError, ReglaNegocioError
from app.models.Goal import Usuario
from app.views.AuthView import get_current_user

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


Router = APIRouter()
Eventos = EventosService()
Recordatorios = RecordatoriosService()
Participantes = ParticipantesService()
Usuarios = UsuariosService()


@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()


# Utilidades de zona horaria
def _obtener_tz(SesionBD: Session, UsuarioId: Optional[int], ZonaHoraria: Optional[str]):
    """Resuelve la zona horaria: prioridad ZonaHoraria explicita, luego la del Usuario, si no UTC."""
    zona = ZonaHoraria
    if zona is None and UsuarioId is not None:
        u = Usuarios.Obtener(SesionBD, UsuarioId)
        if u is not None and u.ZonaHoraria:
            zona = u.ZonaHoraria
    try:
        if zona and ZoneInfo:
            return ZoneInfo(zona)
    except Exception:
        pass
    # Por defecto UTC
    return timezone.utc


def _a_utc_naive(
    dt: Optional[datetime],
    ZonaEntrada: Optional[str] = None,
    ZonaFallback: Optional[str] = None,
) -> Optional[datetime]:
    """Convierte un datetime a UTC naive. Usa ZonaEntrada o ZonaFallback para interpretar valores naive."""
    if dt is None:
        return None
    # Si viene con tzinfo, convertir a UTC
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    # Si es naive y se indico ZonaEntrada, interpretarlo en esa zona
    zona_origen = ZonaEntrada or ZonaFallback
    if zona_origen and ZoneInfo:
        try:
            loc = dt.replace(tzinfo=ZoneInfo(zona_origen))
            return loc.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            pass
    # Caso contrario, asumir que ya es UTC naive
    return dt


def _a_zona_iso(dt: Optional[datetime], tz) -> Optional[str]:
    """Toma un datetime UTC naive y devuelve ISO8601 con offset en tz."""
    if dt is None:
        return None
    # Asumimos almacenado en UTC naive
    aware = dt.replace(tzinfo=timezone.utc)
    return aware.astimezone(tz).isoformat()


# Eventos
@Router.get("/eventos")
def ListarEventos(
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    res = Eventos.ListarEventos(SesionBD)
    # Convertir campos de tiempo a la zona objetivo
    salida = []
    for ev in res:
        obj = ev.dict()
        # Convertir DiasSemana CSV -> lista
        if obj.get("DiasSemana"):
            obj["DiasSemana"] = [d for d in obj["DiasSemana"].split(",") if d]
        obj["Inicio"] = _a_zona_iso(ev.Inicio, tz)
        obj["Fin"] = _a_zona_iso(ev.Fin, tz)
        obj["CreadoEn"] = _a_zona_iso(ev.CreadoEn, tz)
        obj["ActualizadoEn"] = _a_zona_iso(ev.ActualizadoEn, tz) if ev.ActualizadoEn else None
        obj["EliminadoEn"] = _a_zona_iso(ev.EliminadoEn, tz) if ev.EliminadoEn else None
        salida.append(obj)
    return salida


@Router.get("/eventos/proximos")
def ListarEventosProximos(
    Desde: datetime,
    Hasta: datetime,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    ZonaHorariaEntrada: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    # Normalizar rango a UTC naive
    desde_utc = _a_utc_naive(Desde, ZonaHorariaEntrada)
    hasta_utc = _a_utc_naive(Hasta, ZonaHorariaEntrada)
    if hasta_utc <= desde_utc:
        raise HTTPException(status_code=400, detail="Rango invalido")
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    ocurrencias = Eventos.ProyectarOcurrencias(SesionBD, Desde=desde_utc, Hasta=hasta_utc)
    # Convertir ocurrencias a zona
    salida = []
    for o in ocurrencias:
        salida.append({
            'Titulo': o['Titulo'],
            'EventoId': o['EventoId'],
            'Inicio': _a_zona_iso(o['Inicio'], tz),
            'Fin': _a_zona_iso(o['Fin'], tz),
        })
    return salida


@Router.post("/eventos", response_model=EventoRespuesta, status_code=201)
def CrearEvento(
    Datos: EventoCrear,
    ZonaHorariaEntrada: Optional[str] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    if Datos.PropietarioId != UsuarioActual.Id:
        raise HTTPException(status_code=403, detail="EventoInvalido: PropietarioId debe coincidir con el usuario autenticado")
    ini_utc = _a_utc_naive(Datos.Inicio, ZonaHorariaEntrada, UsuarioActual.ZonaHoraria)
    fin_utc = _a_utc_naive(Datos.Fin, ZonaHorariaEntrada, UsuarioActual.ZonaHoraria)
    try:
        Entidad = Eventos.CrearEvento(
            SesionBD,
            MetaId=Datos.MetaId,
            PropietarioId=UsuarioActual.Id,
            Titulo=Datos.Titulo,
            Inicio=ini_utc,
            Fin=fin_utc,
            Descripcion=Datos.Descripcion,
            Ubicacion=Datos.Ubicacion,
            FrecuenciaRepeticion=Datos.FrecuenciaRepeticion,
            IntervaloRepeticion=Datos.IntervaloRepeticion,
            DiasSemana=Datos.DiasSemana,
            SolicitanteId=UsuarioActual.Id,
        )
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    except ReglaNegocioError as exc:
        raise HTTPException(status_code=409, detail=exc.detalle)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="EventoInvalido: Meta/Propietario inexistentes, rol no permitido o rango de tiempo")
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    # Formateo manual manteniendo response_model casting
    Entidad.Inicio = Entidad.Inicio  # ya UTC naive
    Entidad.Fin = Entidad.Fin
    return Entidad


@Router.get("/eventos/{Id}")
def ObtenerEvento(
    Id: int,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Eventos.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    obj = Entidad.dict()
    if obj.get("DiasSemana"):
        obj["DiasSemana"] = [d for d in obj["DiasSemana"].split(",") if d]
    obj["Inicio"] = _a_zona_iso(Entidad.Inicio, tz)
    obj["Fin"] = _a_zona_iso(Entidad.Fin, tz)
    obj["CreadoEn"] = _a_zona_iso(Entidad.CreadoEn, tz)
    obj["ActualizadoEn"] = _a_zona_iso(Entidad.ActualizadoEn, tz) if Entidad.ActualizadoEn else None
    obj["EliminadoEn"] = _a_zona_iso(Entidad.EliminadoEn, tz) if Entidad.EliminadoEn else None
    return obj


@Router.patch("/eventos/{Id}", response_model=EventoRespuesta)
def ActualizarEvento(
    Id: int,
    Cambios: EventoActualizar,
    ZonaHorariaEntrada: Optional[str] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    ini_utc = (
        _a_utc_naive(Cambios.Inicio, ZonaHorariaEntrada, UsuarioActual.ZonaHoraria)
        if Cambios.Inicio is not None
        else None
    )
    fin_utc = (
        _a_utc_naive(Cambios.Fin, ZonaHorariaEntrada, UsuarioActual.ZonaHoraria)
        if Cambios.Fin is not None
        else None
    )
    try:
        Entidad = Eventos.ActualizarEvento(
            SesionBD,
            Id,
            Titulo=Cambios.Titulo,
            Descripcion=Cambios.Descripcion,
            Inicio=ini_utc,
            Fin=fin_utc,
            Ubicacion=Cambios.Ubicacion,
            FrecuenciaRepeticion=Cambios.FrecuenciaRepeticion,
            IntervaloRepeticion=Cambios.IntervaloRepeticion,
            DiasSemana=Cambios.DiasSemana,
            SolicitanteId=UsuarioActual.Id,
        )
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    except ReglaNegocioError as exc:
        raise HTTPException(status_code=409, detail=exc.detalle)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="EventoInvalido: no encontrado, eliminado o rango de tiempo invalido")
    return Entidad


@Router.delete("/eventos/{Id}")
def EliminarEvento(Id: int, SesionBD: Session = Depends(ObtenerSesion), UsuarioActual: Usuario = Depends(get_current_user)):
    try:
        Exito = Eventos.EliminarEvento(SesionBD, Id, SolicitanteId=UsuarioActual.Id)
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    if not Exito:
        raise HTTPException(status_code=404, detail="Evento no encontrado o ya eliminado")
    return {"ok": True}


@Router.post("/eventos/{Id}/recuperar")
def RecuperarEvento(
    Id: int,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    try:
        Entidad = Eventos.RecuperarEvento(SesionBD, Id, SolicitanteId=UsuarioActual.Id)
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    except ReglaNegocioError as exc:
        raise HTTPException(status_code=409, detail=exc.detalle)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="No se puede recuperar (evento inexistente o Meta eliminada)")
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    obj = Entidad.dict()
    obj["Inicio"] = _a_zona_iso(Entidad.Inicio, tz)
    obj["Fin"] = _a_zona_iso(Entidad.Fin, tz)
    obj["CreadoEn"] = _a_zona_iso(Entidad.CreadoEn, tz)
    obj["ActualizadoEn"] = _a_zona_iso(Entidad.ActualizadoEn, tz) if Entidad.ActualizadoEn else None
    obj["EliminadoEn"] = _a_zona_iso(Entidad.EliminadoEn, tz) if Entidad.EliminadoEn else None
    return obj


# Recordatorios
@Router.get("/recordatorios")
def ListarRecordatorios(
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    res = Recordatorios.ListarRecordatorios(SesionBD)
    salida = []
    for r in res:
        obj = r.dict()
        if obj.get("DiasSemana"):
            obj["DiasSemana"] = [d for d in obj["DiasSemana"].split(",") if d]
        obj["FechaHora"] = _a_zona_iso(r.FechaHora, tz)
        obj["CreadoEn"] = _a_zona_iso(r.CreadoEn, tz)
        obj["EliminadoEn"] = _a_zona_iso(r.EliminadoEn, tz) if r.EliminadoEn else None
        salida.append(obj)
    return salida


@Router.post("/recordatorios", response_model=RecordatorioRespuesta, status_code=201)
def CrearRecordatorio(
    Datos: RecordatorioCrear,
    ZonaHorariaEntrada: Optional[str] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    fh_utc = _a_utc_naive(Datos.FechaHora, ZonaHorariaEntrada, UsuarioActual.ZonaHoraria)
    try:
        Entidad = Recordatorios.CrearRecordatorio(
            SesionBD,
            EventoId=Datos.EventoId,
            FechaHora=fh_utc,
            Canal=Datos.Canal,
            Mensaje=Datos.Mensaje,
            FrecuenciaRepeticion=Datos.FrecuenciaRepeticion,
            IntervaloRepeticion=Datos.IntervaloRepeticion,
            DiasSemana=Datos.DiasSemana,
            SolicitanteId=UsuarioActual.Id,
        )
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    except ReglaNegocioError as exc:
        raise HTTPException(status_code=409, detail=exc.detalle)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="RecordatorioInvalido: evento inexistente/eliminado, rol no permitido o fecha pasada")
    return Entidad


@Router.get("/recordatorios/{Id}")
def ObtenerRecordatorio(
    Id: int,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Recordatorios.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    obj = Entidad.dict()
    if obj.get("DiasSemana"):
        obj["DiasSemana"] = [d for d in obj["DiasSemana"].split(",") if d]
    obj["FechaHora"] = _a_zona_iso(Entidad.FechaHora, tz)
    obj["CreadoEn"] = _a_zona_iso(Entidad.CreadoEn, tz)
    obj["EliminadoEn"] = _a_zona_iso(Entidad.EliminadoEn, tz) if Entidad.EliminadoEn else None
    return obj


@Router.patch("/recordatorios/{Id}", response_model=RecordatorioRespuesta)
def ActualizarRecordatorio(
    Id: int,
    Cambios: RecordatorioActualizar,
    ZonaHorariaEntrada: Optional[str] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    fh_utc = (
        _a_utc_naive(Cambios.FechaHora, ZonaHorariaEntrada, UsuarioActual.ZonaHoraria)
        if Cambios.FechaHora is not None
        else None
    )
    try:
        Entidad = Recordatorios.ActualizarRecordatorio(
            SesionBD,
            Id,
            FechaHora=fh_utc,
            Canal=Cambios.Canal,
            Enviado=Cambios.Enviado,
            Mensaje=Cambios.Mensaje,
            FrecuenciaRepeticion=Cambios.FrecuenciaRepeticion,
            IntervaloRepeticion=Cambios.IntervaloRepeticion,
            DiasSemana=Cambios.DiasSemana,
            SolicitanteId=UsuarioActual.Id,
        )
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    except ReglaNegocioError as exc:
        raise HTTPException(status_code=409, detail=exc.detalle)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="RecordatorioInvalido: no encontrado/eliminado o fecha/rol invalidos")
    return Entidad


@Router.delete("/recordatorios/{Id}")
def EliminarRecordatorio(Id: int, SesionBD: Session = Depends(ObtenerSesion), UsuarioActual: Usuario = Depends(get_current_user)):
    try:
        Exito = Recordatorios.EliminarRecordatorio(SesionBD, Id, SolicitanteId=UsuarioActual.Id)
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    if not Exito:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado o ya eliminado")
    return {"ok": True}


@Router.post("/recordatorios/{Id}/recuperar")
def RecuperarRecordatorio(
    Id: int,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    try:
        Entidad = Recordatorios.RecuperarRecordatorio(SesionBD, Id, SolicitanteId=UsuarioActual.Id)
    except PermisoDenegadoError as exc:
        raise HTTPException(status_code=403, detail=exc.detalle)
    except ReglaNegocioError as exc:
        raise HTTPException(status_code=409, detail=exc.detalle)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="No se puede recuperar (recordatorio inexistente o Evento eliminado)")
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    obj = Entidad.dict()
    obj["FechaHora"] = _a_zona_iso(Entidad.FechaHora, tz)
    obj["CreadoEn"] = _a_zona_iso(Entidad.CreadoEn, tz)
    obj["EliminadoEn"] = _a_zona_iso(Entidad.EliminadoEn, tz) if Entidad.EliminadoEn else None
    return obj


@Router.get("/recordatorios/proximos")
def ListarRecordatoriosProximos(
    dias: int = 7,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    if dias <= 0:
        dias = 7
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    res = Recordatorios.ListarProximos(SesionBD, dias=dias)
    salida = []
    for r in res:
        obj = r.dict()
        if obj.get("DiasSemana"):
            obj["DiasSemana"] = [d for d in obj["DiasSemana"].split(",") if d]
        obj["FechaHora"] = _a_zona_iso(r.FechaHora, tz)
        obj["CreadoEn"] = _a_zona_iso(r.CreadoEn, tz)
        obj["EliminadoEn"] = _a_zona_iso(r.EliminadoEn, tz) if r.EliminadoEn else None
        salida.append(obj)
    return salida


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
