from fastapi import APIRouter


# Mantener /salud
Router = APIRouter()


@Router.get("")
def ObtenerEstado():
    return {"estado": "ok"}


# Nuevo alias /health
RouterHealth = APIRouter()


@RouterHealth.get("")
def HealthCheck():
    return {"status": "ok"}
