from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.services.MetasService import MetasService
from app.services.EventosService import EventosService
from app.services.RecordatoriosService import RecordatoriosService
from app.services.UsuariosService import UsuariosService

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None  # type: ignore

Router = APIRouter()
Metas = MetasService()
Eventos = EventosService()
Recordatorios = RecordatoriosService()
Usuarios = UsuariosService()

@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()

# Utilidades de zona horaria (copiadas de EventoView para consistencia)
def _obtener_tz(SesionBD: Session, UsuarioId: Optional[int], ZonaHoraria: Optional[str]):
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
    return timezone.utc


def _a_utc_naive(dt: Optional[datetime], ZonaEntrada: Optional[str] = None) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    if ZonaEntrada and ZoneInfo:
        try:
            loc = dt.replace(tzinfo=ZoneInfo(ZonaEntrada))
            return loc.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            pass
    return dt


def _a_zona_iso(dt: Optional[datetime], tz) -> Optional[str]:
    if dt is None:
        return None
    aware = dt.replace(tzinfo=timezone.utc)
    return aware.astimezone(tz).isoformat()

# Listados de papelera (solo soft-deleted)
@Router.get("/papelera/metas")
def ListarMetasEliminadas(
    PropietarioId: Optional[int] = None,
    Desde: Optional[datetime] = None,
    Hasta: Optional[datetime] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    ZonaHorariaEntrada: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    desde_utc = _a_utc_naive(Desde, ZonaHorariaEntrada) if Desde else None
    hasta_utc = _a_utc_naive(Hasta, ZonaHorariaEntrada) if Hasta else None
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    res = Metas.ListarMetasEliminadas(SesionBD, PropietarioId=PropietarioId, Desde=desde_utc, Hasta=hasta_utc)
    salida = []
    for m in res:
        obj = m.dict()
        obj["CreadoEn"] = _a_zona_iso(m.CreadoEn, tz)
        obj["ActualizadoEn"] = _a_zona_iso(m.ActualizadoEn, tz) if m.ActualizadoEn else None
        obj["EliminadoEn"] = _a_zona_iso(m.EliminadoEn, tz) if m.EliminadoEn else None
        salida.append(obj)
    return salida


@Router.get("/papelera/eventos")
def ListarEventosEliminados(
    PropietarioId: Optional[int] = None,
    MetaId: Optional[int] = None,
    Desde: Optional[datetime] = None,
    Hasta: Optional[datetime] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    ZonaHorariaEntrada: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    desde_utc = _a_utc_naive(Desde, ZonaHorariaEntrada) if Desde else None
    hasta_utc = _a_utc_naive(Hasta, ZonaHorariaEntrada) if Hasta else None
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    res = Eventos.ListarEventosEliminados(
        SesionBD,
        PropietarioId=PropietarioId,
        MetaId=MetaId,
        Desde=desde_utc,
        Hasta=hasta_utc,
    )
    salida = []
    for ev in res:
        obj = ev.dict()
        obj["Inicio"] = _a_zona_iso(ev.Inicio, tz)
        obj["Fin"] = _a_zona_iso(ev.Fin, tz)
        obj["CreadoEn"] = _a_zona_iso(ev.CreadoEn, tz)
        obj["ActualizadoEn"] = _a_zona_iso(ev.ActualizadoEn, tz) if ev.ActualizadoEn else None
        obj["EliminadoEn"] = _a_zona_iso(ev.EliminadoEn, tz) if ev.EliminadoEn else None
        salida.append(obj)
    return salida


@Router.get("/papelera/recordatorios")
def ListarRecordatoriosEliminados(
    EventoId: Optional[int] = None,
    Desde: Optional[datetime] = None,
    Hasta: Optional[datetime] = None,
    UsuarioId: Optional[int] = None,
    ZonaHoraria: Optional[str] = None,
    ZonaHorariaEntrada: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    desde_utc = _a_utc_naive(Desde, ZonaHorariaEntrada) if Desde else None
    hasta_utc = _a_utc_naive(Hasta, ZonaHorariaEntrada) if Hasta else None
    tz = _obtener_tz(SesionBD, UsuarioId, ZonaHoraria)
    res = Recordatorios.ListarRecordatoriosEliminados(
        SesionBD, EventoId=EventoId, Desde=desde_utc, Hasta=hasta_utc
    )
    salida = []
    for r in res:
        obj = r.dict()
        obj["FechaHora"] = _a_zona_iso(r.FechaHora, tz)
        obj["CreadoEn"] = _a_zona_iso(r.CreadoEn, tz)
        obj["EliminadoEn"] = _a_zona_iso(r.EliminadoEn, tz) if r.EliminadoEn else None
        salida.append(obj)
    return salida
