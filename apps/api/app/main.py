from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os

from app.views.HealthView import Router as SaludRouter, RouterHealth as HealthRouter
from app.views.GoalView import Router as MetasRouter
from app.views.EventoView import Router as EventosRouter
from app.views.PapeleraView import Router as PapeleraRouter
from app.views.AuthView import RouterAuth, get_current_user
from app.core.Database import IniciarTablas


def CrearAplicacion() -> FastAPI:
    # Version alineada con el changelog (v0.14.x). Mantener sincronizada al liberar.
    Aplicacion = FastAPI(title="MyPlanU API", version="0.16.0")

    # Asegurar creacion de tablas al construir la app (idempotente)
    IniciarTablas()

    # CORS parametrizable: MYPLANU_CORS_ORIGINS="https://app.example.com,https://admin.example.com"
    oris_env = os.getenv("MYPLANU_CORS_ORIGINS", "*")
    if oris_env.strip() == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in oris_env.split(",") if o.strip()]
    Aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @Aplicacion.on_event("startup")
    def AlIniciarAplicacion():
        IniciarTablas()

    # Rutas
    Aplicacion.include_router(SaludRouter, prefix="/salud", tags=["salud"])
    Aplicacion.include_router(HealthRouter, prefix="/health", tags=["health"])
    # GoalView maneja /usuarios y /metas, EventoView maneja /eventos y /recordatorios
    Aplicacion.include_router(RouterAuth, tags=["auth"])
    Aplicacion.include_router(MetasRouter, tags=["usuarios", "metas"], dependencies=[Depends(get_current_user)])
    Aplicacion.include_router(EventosRouter, tags=["eventos", "recordatorios"], dependencies=[Depends(get_current_user)])
    Aplicacion.include_router(PapeleraRouter, tags=["papelera"], dependencies=[Depends(get_current_user)])

    return Aplicacion


Aplicacion = CrearAplicacion()
