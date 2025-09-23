from fastapi import APIRouter


Router = APIRouter()


@Router.get("/vivo")
def ObtenerEstado():
    return {"Estado": "ok", "Version": "0.1.0"}
