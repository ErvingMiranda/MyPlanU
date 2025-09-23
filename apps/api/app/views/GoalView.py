from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.services.GoalService import UsuarioServicio, MetaServicio


Router = APIRouter()
Usuarios = UsuarioServicio()
Metas = MetaServicio()


@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()


# Usuarios
@Router.get("/usuarios")
def ListarUsuarios(SesionBD: Session = Depends(ObtenerSesion)):
    return Usuarios.Listar(SesionBD)


@Router.post("/usuarios")
def CrearUsuario(Correo: str, Nombre: str, SesionBD: Session = Depends(ObtenerSesion)):
    return Usuarios.Crear(SesionBD, Correo=Correo, Nombre=Nombre)


@Router.get("/usuarios/{Id}")
def ObtenerUsuario(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Usuarios.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Entidad


@Router.patch("/usuarios/{Id}")
def ActualizarUsuario(Id: int, Correo: Optional[str] = None, Nombre: Optional[str] = None, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Usuarios.Actualizar(SesionBD, Id, Correo=Correo, Nombre=Nombre)
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
    return Metas.Listar(SesionBD)


@Router.post("/metas")
def CrearMeta(PropietarioId: int, Titulo: str, TipoMeta: str, Descripcion: Optional[str] = None, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Metas.Crear(SesionBD, PropietarioId=PropietarioId, Titulo=Titulo, TipoMeta=TipoMeta, Descripcion=Descripcion)
    if Entidad is None:
        raise HTTPException(status_code=400, detail="PropietarioId invalido")
    return Entidad


@Router.get("/metas/{Id}")
def ObtenerMeta(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Metas.Obtener(SesionBD, Id)
    if Entidad is None or Entidad.EliminadoEn is not None:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    return Entidad


@Router.patch("/metas/{Id}")
def ActualizarMeta(Id: int, Titulo: Optional[str] = None, Descripcion: Optional[str] = None, TipoMeta: Optional[str] = None, SesionBD: Session = Depends(ObtenerSesion)):
    Entidad = Metas.Actualizar(SesionBD, Id, Titulo=Titulo, Descripcion=Descripcion, TipoMeta=TipoMeta)
    if Entidad is None:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    return Entidad


@Router.delete("/metas/{Id}")
def EliminarMeta(Id: int, SesionBD: Session = Depends(ObtenerSesion)):
    Exito = Metas.Eliminar(SesionBD, Id)
    if not Exito:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    return {"ok": True}
