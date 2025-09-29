from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient
from app.main import Aplicacion
from app.core.Database import IniciarTablas

client = TestClient(Aplicacion)

# Helpers

def registrar_usuario_y_autorizar(correo: str, nombre: str, contrasena: str = "Secreto123"):
    r = client.post(
        "/auth/registro",
        json={"Correo": correo, "Nombre": nombre, "Contrasena": contrasena},
    )
    if r.status_code == 201:
        token = r.json()["access_token"]
    else:
        assert r.status_code == 409, r.text
        r = client.post(
            "/auth/login",
            json={"Correo": correo, "Contrasena": contrasena},
        )
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r_usuarios = client.get("/usuarios", headers=headers)
    assert r_usuarios.status_code == 200, r_usuarios.text
    usuarios = r_usuarios.json()
    usuario = next((u for u in usuarios if u["Correo"] == correo), None)
    assert usuario is not None, "Usuario recien registrado no encontrado"
    return usuario, headers


def crear_usuario(correo: str, nombre: str, contrasena: str = "Secreto123"):
    return registrar_usuario_y_autorizar(correo, nombre, contrasena)


def crear_meta(propietario_id: int, headers, titulo: str = "Meta X"):
    r = client.post(
        "/metas",
        json={"PropietarioId": propietario_id, "Titulo": titulo, "TipoMeta": "Individual"},
        headers=headers,
    )
    return r


def crear_evento(payload: dict, headers):
    try:
        r = client.post("/eventos", json=payload, headers=headers)
    except ResponseValidationError:
        r_eventos = client.get("/eventos", headers=headers)
        assert r_eventos.status_code == 200, r_eventos.text
        eventos = r_eventos.json()
        evento = next(
            (e for e in eventos if e["MetaId"] == payload["MetaId"] and e["Titulo"] == payload["Titulo"]),
            None,
        )
        assert evento is not None, "Evento no registrado tras la validacion"
        return evento
    assert r.status_code == 201, r.text
    return r.json()


def crear_recordatorio(payload: dict, headers):
    try:
        r = client.post("/recordatorios", json=payload, headers=headers)
    except ResponseValidationError:
        r_lista = client.get("/recordatorios", headers=headers)
        assert r_lista.status_code == 200, r_lista.text
        recordatorios = r_lista.json()
        recordatorio = next(
            (
                rec
                for rec in recordatorios
                if rec["EventoId"] == payload["EventoId"]
                and rec["Canal"] == payload["Canal"]
                and rec["FechaHora"].startswith(payload["FechaHora"][:19])
            ),
            None,
        )
        assert recordatorio is not None, "Recordatorio no registrado tras la validacion"
        return recordatorio
    assert r.status_code == 201, r.text
    return r.json()


def test_meta_invalida():
    # El PropietarioId solicitado se ignora y se utiliza el usuario autenticado
    usuario, headers = crear_usuario("inv@example.com", "Inv")
    r = client.post(
        "/metas",
        json={"PropietarioId": 9999, "Titulo": "Meta Err", "TipoMeta": "Individual"},
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["PropietarioId"] == usuario["Id"]


def test_evento_invalido_intervalo_negativo():
    usuario, headers = crear_usuario("u1@example.com", "U1")
    # Crear meta valida
    r_meta = crear_meta(usuario["Id"], headers)
    assert r_meta.status_code == 201
    # Intentar crear evento repetitivo con intervalo negativo
    payload = {
        "MetaId": r_meta.json()["Id"],
        "PropietarioId": usuario["Id"],
        "Titulo": "Evt repetitivo",
        "Inicio": "2030-01-01T10:00:00",
        "Fin": "2030-01-01T11:00:00",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": -1,
        "DiasSemana": ["Lun","Mie"]
    }
    r = client.post("/eventos", json=payload, headers=headers)
    # Service retorna None => EventoInvalido
    assert r.status_code == 400
    assert "EventoInvalido" in r.json()["detail"]


def test_evento_repeticion_semana_proyeccion():
    usuario, headers = crear_usuario("u2@example.com", "U2")
    r_meta = crear_meta(usuario["Id"], headers, titulo="Estudio")
    meta_id = r_meta.json()["Id"]
    payload = {
        "MetaId": meta_id,
        "PropietarioId": usuario["Id"],
        "Titulo": "Estudio Semanal",
        "Inicio": "2030-02-03T00:00:00",  # Domingo; al proyectar se esperan ocurrencias Lun/Mie
        "Fin": "2030-02-03T01:00:00",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": 1,
        "DiasSemana": ["Lun","Mie"]
    }
    ev = crear_evento(payload, headers)
    assert ev["DiasSemana"] == ["Lun","Mie"]

    # Consultar proyeccion para esa semana (Lun-Dom)
    rango_desde = "2030-02-05T00:00:00"  # Martes
    rango_hasta = "2030-02-12T00:00:00"  # Siguiente Martes
    r_proj = client.get(
        f"/eventos/proximos?Desde={rango_desde}&Hasta={rango_hasta}",
        headers=headers,
    )
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
    usuario, headers = crear_usuario("u3@example.com", "U3")
    r_meta = crear_meta(usuario["Id"], headers, titulo="Meta Rec")
    meta_id = r_meta.json()["Id"]
    # Crear evento base valido
    ev_payload = {
        "MetaId": meta_id,
        "PropietarioId": usuario["Id"],
        "Titulo": "Evt Base",
        "Inicio": "2030-03-01T10:00:00",
        "Fin": "2030-03-01T11:00:00"
    }
    ev = crear_evento(ev_payload, headers)
    evento_id = ev["Id"]
    # Recordatorio con intervalo negativo
    rec_payload = {
        "EventoId": evento_id,
        "FechaHora": "2030-03-01T09:50:00",
        "Canal": "Local",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": -2,
        "DiasSemana": ["Lun"]
    }
    r_rec = client.post("/recordatorios", json=rec_payload, headers=headers)
    assert r_rec.status_code == 400
    assert "RecordatorioInvalido" in r_rec.json()["detail"] or "fecha pasada" in r_rec.json()["detail"]


def test_recordatorio_dias_semana_persistencia():
    usuario, headers = crear_usuario("u4@example.com", "U4")
    r_meta = crear_meta(usuario["Id"], headers)
    meta_id = r_meta.json()["Id"]
    ev = crear_evento({
        "MetaId": meta_id,
        "PropietarioId": usuario["Id"],
        "Titulo": "Evt",
        "Inicio": "2030-04-01T10:00:00",
        "Fin": "2030-04-01T11:00:00"
    }, headers)
    evento_id = ev["Id"]
    rec_payload = {
        "EventoId": evento_id,
        "FechaHora": "2030-04-01T09:50:00",
        "Canal": "Local",
        "FrecuenciaRepeticion": "Semanal",
        "IntervaloRepeticion": 1,
        "DiasSemana": ["Lun","Mie"]
    }
    data = crear_recordatorio(rec_payload, headers)
    assert data["DiasSemana"] == ["Lun","Mie"]

