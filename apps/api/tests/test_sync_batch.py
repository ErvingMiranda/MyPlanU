from fastapi.testclient import TestClient
from app.main import Aplicacion

client = TestClient(Aplicacion)


def auth_headers():
    # Registrar y loguear usuario para obtener token
    client.post("/auth/registro", json={"Correo":"sync@example.com","Nombre":"Sync","Contrasena":"x"})
    r = client.post("/auth/login", json={"Correo":"sync@example.com","Contrasena":"x"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_sync_metas_create_update_flow():
    h = auth_headers()
    # Crear meta via batch con tempId
    body = {
        "operations": [
            {"kind":"create","tempId":-1,"data":{"Titulo":"M1","TipoMeta":"Individual","Descripcion":"D"}},
            {"kind":"update","targetId":-1,"data":{"Titulo":"M1-Edit"}},
        ],
        "sequential": True,
        "continueOnError": True,
    }
    r = client.post("/sync/metas", json=body, headers=h)
    assert r.status_code == 200, r.text
    data = r.json()
    # Debe mapear -1 → Id real y aplicar update
    mapping = data.get("mappings", {})
    assert "-1" in mapping
    real_id = mapping["-1"]
    # Obtener meta y verificar titulo editado
    r_get = client.get(f"/metas/{real_id}", headers=h)
    assert r_get.status_code == 200
    assert r_get.json()["Titulo"] == "M1-Edit"


def test_sync_eventos_create_invalid_interval():
    h = auth_headers()
    # Se requiere una meta previa para crear evento
    r_meta = client.post("/metas", json={"PropietarioId":1, "Titulo":"M2", "TipoMeta":"Individual"}, headers=h)
    assert r_meta.status_code == 201
    meta_id = r_meta.json()["Id"]
    body = {
        "operations": [
            {"kind":"create","tempId":-5,"data":{
                "MetaId": meta_id,
                "PropietarioId": 1,
                "Titulo":"EvtBad",
                "Inicio":"2035-01-01T10:00:00",
                "Fin":"2035-01-01T09:00:00",
                "FrecuenciaRepeticion":"Semanal",
                "IntervaloRepeticion": 0,
                "DiasSemana":["Lun"]
            }}
        ]
    }
    r = client.post("/sync/eventos", json=body, headers=h)
    assert r.status_code == 200
    res = r.json()
    assert len(res["results"]) == 1
    assert res["results"][0]["ok"] is False
    assert "EventoInvalido" in res["results"][0]["error"]
