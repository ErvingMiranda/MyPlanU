from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.services.UsuariosService import UsuariosService
from app.services.MetasService import MetasService
from app.schemas import MetaCrear, MetaActualizar, MetaRespuesta
from app.views.AuthView import get_current_user
from app.models.Goal import Usuario


Router = APIRouter()
Usuarios = UsuariosService()
Metas = MetasService()


@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()


# Usuarios
@Router.get("/usuarios")
def ListarUsuarios(SesionBD: Session = Depends(ObtenerSesion)):
    return Usuarios.Listar(SesionBD)


# Nota: registro de usuarios se mueve a /auth/registro (este endpoint se mantiene para compatibilidad interna)
@Router.post("/usuarios")
def CrearUsuario(Correo: str, Nombre: str, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Usuarios.Crear(SesionBD, Correo=Correo, Nombre=Nombre)
    if Entidad is None:
        raise HTTPException(status_code=409, detail="Correo ya existe")
    return Entidad


@Router.get("/usuarios/{Id}")
def ObtenerUsuario(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Usuarios.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Entidad


@Router.patch("/usuarios/{Id}")
def ActualizarUsuario(
    Id: int,
    Correo: Optional[str] = None,
    Nombre: Optional[str] = None,
    ZonaHoraria: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesion),
):
    Entidad = Usuarios.Actualizar(SesionBD, Id, Correo=Correo, Nombre=Nombre, ZonaHoraria=ZonaHoraria)
    if Entidad is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Entidad


@Router.delete("/usuarios/{Id}")
def EliminarUsuario(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Exito = Usuarios.Eliminar(SesionBD, Id)
    if not Exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}


# Metas
@Router.get("/metas")
def ListarMetas(SesionBD: Session = Depends(ObtenerSesion)):
    return Metas.ListarMetas(SesionBD)


@Router.post("/metas", response_model=MetaRespuesta, status_code=201)
def CrearMeta(MetaIn: MetaCrear, SesionBD: Session = Depends(ObtenerSesion), UsuarioActual: Usuario = Depends(get_current_user)):
    # Forzar PropietarioId al usuario autenticado
    Entidad = Metas.CrearMeta(
        SesionBD,
        PropietarioId=UsuarioActual.Id,
        Titulo=MetaIn.Titulo,
        TipoMeta=MetaIn.TipoMeta,
        Descripcion=MetaIn.Descripcion,
    )
    if Entidad is None:
        raise HTTPException(status_code=400, detail="MetaInvalida: PropietarioId inexistente o usuario no existe")
    return Entidad


@Router.get("/metas/{Id}")
def ObtenerMeta(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Metas.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    return Entidad


@Router.patch("/metas/{Id}", response_model=MetaRespuesta)
def ActualizarMeta(Id: int, Cambios: MetaActualizar, SesionBD: Session = Depends(ObtenerSesion), UsuarioActual: Usuario = Depends(get_current_user)):
    EntidadExistente = Metas.Obtener(SesionBD, Id)
    if not EntidadExistente or EntidadExistente.PropietarioId != UsuarioActual.Id:
        raise HTTPException(status_code=403, detail="Forbidden")
    Entidad = Metas.ActualizarMeta(
        SesionBD,
        Id,
        Titulo=Cambios.Titulo,
        Descripcion=Cambios.Descripcion,
        TipoMeta=Cambios.TipoMeta,
    )
    if Entidad is None:
        raise HTTPException(status_code=404, detail="MetaInvalida: no encontrada o eliminada")
    return Entidad


@Router.delete("/metas/{Id}")
def EliminarMeta(Id: int, SesionBD: Session = Depends(ObtenerSesion), UsuarioActual: Usuario = Depends(get_current_user)):
    EntidadExistente = Metas.Obtener(SesionBD, Id)
    if not EntidadExistente or EntidadExistente.PropietarioId != UsuarioActual.Id:
        raise HTTPException(status_code=403, detail="Forbidden")
    Exito = Metas.EliminarMeta(SesionBD, Id)
    if not Exito:
        raise HTTPException(status_code=404, detail="MetaInvalida: no encontrada o ya eliminada")
    return {"ok": True}


@Router.post("/metas/{Id}/recuperar")
def RecuperarMeta(Id: int, SesionBD: Session = Depends(ObtenerSesion), UsuarioActual: Usuario = Depends(get_current_user)):
    EntidadExistente = Metas.Obtener(SesionBD, Id)
    if not EntidadExistente or EntidadExistente.PropietarioId != UsuarioActual.Id:
        raise HTTPException(status_code=403, detail="Forbidden")
    Entidad = Metas.RecuperarMeta(SesionBD, Id)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="MetaInvalida: no se puede recuperar (inexistente o activa)")
    return Entidad
