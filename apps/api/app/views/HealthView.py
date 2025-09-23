from fastapi import APIRouter


Router = APIRouter()


@Router.get("")
def ObtenerEstado():
    return {"estado": "ok"}
