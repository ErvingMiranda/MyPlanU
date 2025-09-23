from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.Database import ObtenerSesion, IniciarTablas
from app.services.GoalService import MetaServicio


Router = APIRouter()
Servicio = MetaServicio()


@Router.on_event("startup")
def AlIniciar():
    IniciarTablas()


@Router.get("/")
def ListarMetas(SesionBD: Session = Depends(ObtenerSesion)):
    return Servicio.Listar(SesionBD)


@Router.post("/")
def CrearMeta(Titulo: str, Descripcion: Optional[str] = None, SesionBD: Session = Depends(ObtenerSesion)):
    return Servicio.Crear(SesionBD, Titulo=Titulo, Descripcion=Descripcion)
