from typing import Optional, Dict
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.views.AuthView import get_current_user
from app.models.Goal import Usuario
from app.schemas import BatchRequest, BatchResponse, BatchItemResult
from app.services.MetasService import MetasService
from app.services.EventosService import EventosService
from app.core.Permisos import RolParticipante


Router = APIRouter()
Metas = MetasService()
Eventos = EventosService()


@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()


@Router.post("/sync/metas", response_model=BatchResponse)
def SyncMetas(
    body: BatchRequest,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    results = []
    mappings: Dict[str, int] = {}
    # Ejecutar en orden; si sequential==True y !continueOnError, abortar al primer error
    for idx, op in enumerate(body.operations):
        kind = str(op.kind)
        try:
            if kind == 'create':
                datos = dict(op.data)
                # Forzar PropietarioId al usuario autenticado
                datos['PropietarioId'] = UsuarioActual.Id
                ent = Metas.CrearMeta(
                    SesionBD,
                    PropietarioId=datos['PropietarioId'],
                    Titulo=datos.get('Titulo'),
                    TipoMeta=datos.get('TipoMeta'),
                    Descripcion=datos.get('Descripcion'),
                )
                if ent is None:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, tempId=op.tempId, error="MetaInvalida: datos invalidos o propietario inexistente"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                # Mapear tempId->Id definitivo
                if op.tempId is not None:
                    mappings[str(op.tempId)] = ent.Id  # type: ignore
                results.append(BatchItemResult(index=idx, kind=kind, ok=True, id=ent.Id, tempId=op.tempId))
            elif kind == 'update':
                datos = dict(op.data)
                target_id = op.targetId
                if target_id is None:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, error="MetaInvalida: targetId requerido"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                # Nota: si viene como negativo y existe mapeo previo, traducir
                if target_id < 0:
                    mapped = mappings.get(str(target_id))
                    if mapped:
                        target_id = mapped
                ent_exist = Metas.Obtener(SesionBD, target_id)
                if not ent_exist or ent_exist.PropietarioId != UsuarioActual.Id:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, targetId=op.targetId, error="Forbidden"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                ent = Metas.ActualizarMeta(
                    SesionBD,
                    target_id,
                    Titulo=datos.get('Titulo'),
                    Descripcion=datos.get('Descripcion'),
                    TipoMeta=datos.get('TipoMeta'),
                )
                if ent is None:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, targetId=op.targetId, error="MetaInvalida: no encontrada o eliminada"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                results.append(BatchItemResult(index=idx, kind=kind, ok=True, id=ent.Id, targetId=op.targetId))
            else:
                results.append(BatchItemResult(index=idx, kind=kind, ok=False, error="MetaInvalida: operacion desconocida"))
                if body.sequential and not body.continueOnError:
                    break
        except Exception:
            results.append(BatchItemResult(index=idx, kind=kind, ok=False, error="MetaInvalida: error inesperado"))
            if body.sequential and not body.continueOnError:
                break
    return BatchResponse(results=results, mappings=mappings)


@Router.post("/sync/eventos", response_model=BatchResponse)
def SyncEventos(
    body: BatchRequest,
    ZonaHorariaEntrada: Optional[str] = None,
    Rol: RolParticipante = RolParticipante.Dueno,
    SesionBD: Session = Depends(ObtenerSesion),
    UsuarioActual: Usuario = Depends(get_current_user),
):
    from datetime import timezone
    try:
        from zoneinfo import ZoneInfo
    except Exception:  # pragma: no cover
        ZoneInfo = None  # type: ignore

    def a_utc_naive(dt, zona):
        if dt is None:
            return None
        if getattr(dt, 'tzinfo', None) is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        if zona and ZoneInfo:
            try:
                loc = dt.replace(tzinfo=ZoneInfo(zona))
                return loc.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                pass
        return dt

    results = []
    mappings: Dict[str, int] = {}
    for idx, op in enumerate(body.operations):
        kind = str(op.kind)
        try:
            if kind == 'create':
                d = dict(op.data)
                # Forzar PropietarioId si no viene
                d['PropietarioId'] = d.get('PropietarioId') or UsuarioActual.Id
                ini = d.get('Inicio')
                fin = d.get('Fin')
                ini_utc = a_utc_naive(ini, ZonaHorariaEntrada)
                fin_utc = a_utc_naive(fin, ZonaHorariaEntrada)
                ent = Eventos.CrearEvento(
                    SesionBD,
                    MetaId=d['MetaId'],
                    PropietarioId=d['PropietarioId'],
                    Titulo=d['Titulo'],
                    Inicio=ini_utc,
                    Fin=fin_utc,
                    Descripcion=d.get('Descripcion'),
                    Ubicacion=d.get('Ubicacion'),
                    FrecuenciaRepeticion=d.get('FrecuenciaRepeticion'),
                    IntervaloRepeticion=d.get('IntervaloRepeticion'),
                    DiasSemana=d.get('DiasSemana'),
                    Rol=Rol,
                )
                if ent is None:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, tempId=op.tempId, error="EventoInvalido: datos invalidos, permisos o rango"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                if op.tempId is not None:
                    mappings[str(op.tempId)] = ent.Id  # type: ignore
                results.append(BatchItemResult(index=idx, kind=kind, ok=True, id=ent.Id, tempId=op.tempId))
            elif kind == 'update':
                d = dict(op.data)
                target_id = op.targetId
                if target_id is None:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, error="EventoInvalido: targetId requerido"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                if target_id < 0:
                    mapped = mappings.get(str(target_id))
                    if mapped:
                        target_id = mapped
                ini = d.get('Inicio')
                fin = d.get('Fin')
                ini_utc = a_utc_naive(ini, ZonaHorariaEntrada) if ini is not None else None
                fin_utc = a_utc_naive(fin, ZonaHorariaEntrada) if fin is not None else None
                ent = Eventos.ActualizarEvento(
                    SesionBD,
                    target_id,
                    Titulo=d.get('Titulo'),
                    Descripcion=d.get('Descripcion'),
                    Inicio=ini_utc,
                    Fin=fin_utc,
                    Ubicacion=d.get('Ubicacion'),
                    FrecuenciaRepeticion=d.get('FrecuenciaRepeticion'),
                    IntervaloRepeticion=d.get('IntervaloRepeticion'),
                    DiasSemana=d.get('DiasSemana'),
                    Rol=Rol,
                )
                if ent is None:
                    results.append(BatchItemResult(index=idx, kind=kind, ok=False, targetId=op.targetId, error="EventoInvalido: no encontrado/eliminado o rango/rol invalido"))
                    if body.sequential and not body.continueOnError:
                        break
                    else:
                        continue
                results.append(BatchItemResult(index=idx, kind=kind, ok=True, id=ent.Id, targetId=op.targetId))
            else:
                results.append(BatchItemResult(index=idx, kind=kind, ok=False, error="EventoInvalido: operacion desconocida"))
                if body.sequential and not body.continueOnError:
                    break
        except Exception:
            results.append(BatchItemResult(index=idx, kind=kind, ok=False, error="EventoInvalido: error inesperado"))
            if body.sequential and not body.continueOnError:
                break
    return BatchResponse(results=results, mappings=mappings)


@Router.get("/sync/estado")
def SyncEstado():
    # Placeholder simple: en una version posterior, esto podria leer una tabla de cambios pendientes o versionado
    from datetime import datetime
    return {
        "serverTime": datetime.utcnow().isoformat() + "Z",
        "pending": 0,
        "conflicts": 0,
    }
