from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.views.HealthView import Router as SaludRouter
from app.views.GoalView import Router as MetasRouter


def CrearAplicacion() -> FastAPI:
    Aplicacion = FastAPI(title="MyPlanU API", version="0.1.0")

    Aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rutas
    Aplicacion.include_router(SaludRouter, prefix="/salud", tags=["salud"])
    Aplicacion.include_router(MetasRouter, prefix="/metas", tags=["metas"])

    return Aplicacion


Aplicacion = CrearAplicacion()
