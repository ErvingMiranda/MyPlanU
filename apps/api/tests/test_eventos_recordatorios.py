from fastapi.testclient import TestClient
from app.main import Aplicacion
from sqlmodel import Session
from app.core.Database import ObtenerEngine, IniciarTablas

client = TestClient(Aplicacion)

# Helpers

def crear_usuario(correo: str, nombre: str):
    r = client.post(f"/usuarios?Correo={correo}&Nombre={nombre}")
    assert r.status_code in (200,201,409)


def crear_meta(propietario_id: int, titulo: str = "Meta X"):
    r = client.post("/metas", json={"PropietarioId": propietario_id, "Titulo": titulo, "TipoMeta": "Individual"})
    return r


def test_meta_invalida():
    # Usuario inexistente -> MetaInvalida
    r = client.post("/metas", json={"PropietarioId": 9999, "Titulo": "Meta Err", "TipoMeta": "Individual"})
    assert r.status_code == 400
    assert "MetaInvalida" in r.json()["detail"]


def test_evento_invalido_intervalo_negativo():
    crear_usuario("u1@example.com","U1")
    # Crear meta valida
    r_meta = crear_meta(1)
    assert r_meta.status_code == 201
    # Intentar crear evento repetitivo con intervalo negativo
    payload = {
        "MetaId": r_meta.json()["Id"],
        "PropietarioId": 1,
        "Titulo": "Evt repetitivo",
        "Inicio": "2030-01-01T10:00:00",
        "Fin": "2030-01-01T11:00:00",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": -1,
        "DiasSemana": ["Lun","Mie"]
    }
    r = client.post("/eventos", json=payload)
    # Service retorna None => EventoInvalido
    assert r.status_code == 400
    assert "EventoInvalido" in r.json()["detail"]


def test_evento_repeticion_semana_proyeccion():
    crear_usuario("u2@example.com","U2")
    r_meta = crear_meta(1, titulo="Estudio")
    meta_id = r_meta.json()["Id"]
    payload = {
        "MetaId": meta_id,
        "PropietarioId": 1,
        "Titulo": "Estudio Semanal",
        "Inicio": "2030-02-03T14:00:00",  # Domingo (para comprobar calculo)
        "Fin": "2030-02-03T15:00:00",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": 1,
        "DiasSemana": ["Lun","Mie"]
    }
    r = client.post("/eventos", json=payload)
    assert r.status_code == 201, r.text
    ev = r.json()
    assert ev["DiasSemana"] == ["Lun","Mie"]

    # Consultar proyeccion para esa semana (Lun-Dom)
    rango_desde = "2030-02-05T00:00:00"  # Martes
    rango_hasta = "2030-02-12T00:00:00"  # Siguiente Martes
    r_proj = client.get(f"/eventos/proximos?Desde={rango_desde}&Hasta={rango_hasta}")
    assert r_proj.status_code == 200
    ocurrencias = r_proj.json()
    # Debe haber ocurrencias en lunes y miercoles dentro del rango
    dias_encontrados = set()
    for o in ocurrencias:
        if o["EventoId"] == ev["Id"]:
            # Obtener dia semana en UTC iso parse simplificado
            from datetime import datetime
            dt = datetime.fromisoformat(o["Inicio"])  # timezone aware / naive segun config
            dias_encontrados.add(dt.weekday())
    # Lunes=0, Miercoles=2
    assert 0 in dias_encontrados and 2 in dias_encontrados


def test_recordatorio_invalido_intervalo_negativo():
    crear_usuario("u3@example.com","U3")
    r_meta = crear_meta(1, titulo="Meta Rec")
    meta_id = r_meta.json()["Id"]
    # Crear evento base valido
    ev_payload = {
        "MetaId": meta_id,
        "PropietarioId": 1,
        "Titulo": "Evt Base",
        "Inicio": "2030-03-01T10:00:00",
        "Fin": "2030-03-01T11:00:00"
    }
    r_ev = client.post("/eventos", json=ev_payload)
    assert r_ev.status_code == 201
    evento_id = r_ev.json()["Id"]
    # Recordatorio con intervalo negativo
    rec_payload = {
        "EventoId": evento_id,
        "FechaHora": "2030-03-01T09:50:00",
        "Canal": "Local",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": -2,
        "DiasSemana": ["Lun"]
    }
    r_rec = client.post("/recordatorios", json=rec_payload)
    assert r_rec.status_code == 400
    assert "RecordatorioInvalido" in r_rec.json()["detail"] or "fecha pasada" in r_rec.json()["detail"]


def test_recordatorio_dias_semana_persistencia():
    crear_usuario("u4@example.com","U4")
    r_meta = crear_meta(1)
    meta_id = r_meta.json()["Id"]
    r_ev = client.post("/eventos", json={
        "MetaId": meta_id,
        "PropietarioId": 1,
        "Titulo": "Evt",
        "Inicio": "2030-04-01T10:00:00",
        "Fin": "2030-04-01T11:00:00"
    })
    evento_id = r_ev.json()["Id"]
    rec_payload = {
        "EventoId": evento_id,
        "FechaHora": "2030-04-01T09:50:00",
        "Canal": "Local",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": 1,
        "DiasSemana": ["Lun","Mie"]
    }
    r_rec = client.post("/recordatorios", json=rec_payload)
    assert r_rec.status_code == 201
    data = r_rec.json()
    assert data["DiasSemana"] == ["Lun","Mie"]

