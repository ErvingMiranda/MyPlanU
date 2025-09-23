from typing import Generator

from sqlmodel import Session, SQLModel, create_engine


URLBaseDatos = "sqlite:///./datos.db"
Motor = create_engine(URLBaseDatos, echo=False, connect_args={"check_same_thread": False})


def IniciarTablas() -> None:
    # Importar modelos para registrar metadata antes de crear tablas
    from app.models import Goal  # noqa: F401  # Usuario, Meta
    from app.models.Evento import Evento, Recordatorio, ParticipanteEvento  # noqa: F401
    SQLModel.metadata.create_all(Motor)
    # Migracion simple para agregar columna 'Mensaje' en 'recordatorio' si no existe (SQLite)
    try:
        with Motor.connect() as conn:  # type: ignore[attr-defined]
            res = conn.exec_driver_sql("PRAGMA table_info('recordatorio')").fetchall()
            columnas = {row[1] for row in res} if res else set()
            if 'Mensaje' not in columnas:
                conn.exec_driver_sql("ALTER TABLE recordatorio ADD COLUMN Mensaje VARCHAR NULL")
            # Repeticion en recordatorio
            if 'FrecuenciaRepeticion' not in columnas:
                conn.exec_driver_sql("ALTER TABLE recordatorio ADD COLUMN FrecuenciaRepeticion VARCHAR NULL")
            if 'IntervaloRepeticion' not in columnas:
                conn.exec_driver_sql("ALTER TABLE recordatorio ADD COLUMN IntervaloRepeticion INTEGER NULL")
            if 'DiasSemana' not in columnas:
                conn.exec_driver_sql("ALTER TABLE recordatorio ADD COLUMN DiasSemana VARCHAR NULL")
            # Repeticion en evento
            res_e = conn.exec_driver_sql("PRAGMA table_info('evento')").fetchall()
            cols_e = {row[1] for row in res_e} if res_e else set()
            if 'FrecuenciaRepeticion' not in cols_e:
                conn.exec_driver_sql("ALTER TABLE evento ADD COLUMN FrecuenciaRepeticion VARCHAR NULL")
            if 'IntervaloRepeticion' not in cols_e:
                conn.exec_driver_sql("ALTER TABLE evento ADD COLUMN IntervaloRepeticion INTEGER NULL")
            if 'DiasSemana' not in cols_e:
                conn.exec_driver_sql("ALTER TABLE evento ADD COLUMN DiasSemana VARCHAR NULL")
    except Exception:
        # Fallback silencioso; en entornos limpios la tabla se crea con la columna
        pass


def ObtenerSesion() -> Generator[Session, None, None]:
    with Session(Motor) as SesionBD:
        yield SesionBD
