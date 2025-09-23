from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.views.HealthView import Router as SaludRouter
from app.views.GoalView import Router as MetasRouter
from app.views.EventoView import Router as EventosRouter
from app.core.Database import IniciarTablas


def CrearAplicacion() -> FastAPI:
    Aplicacion = FastAPI(title="MyPlanU API", version="0.2.0")

    # Asegurar creacion de tablas al construir la app (idempotente)
    IniciarTablas()

    Aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @Aplicacion.on_event("startup")
    def AlIniciarAplicacion():
        IniciarTablas()

    # Rutas
    Aplicacion.include_router(SaludRouter, prefix="/salud", tags=["salud"])
    # GoalView maneja /usuarios y /metas, EventoView maneja /eventos y /recordatorios
    Aplicacion.include_router(MetasRouter, tags=["usuarios", "metas"])
    Aplicacion.include_router(EventosRouter, tags=["eventos", "recordatorios"])

    return Aplicacion


Aplicacion = CrearAplicacion()
