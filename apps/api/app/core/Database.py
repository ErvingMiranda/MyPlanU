from typing import Generator

from sqlmodel import Session, SQLModel, create_engine


URLBaseDatos = "sqlite:///./datos.db"
Motor = create_engine(URLBaseDatos, echo=False, connect_args={"check_same_thread": False})


def IniciarTablas() -> None:
    # Importar modelos para registrar metadata antes de crear tablas
    from app.models import Goal  # noqa: F401  # Usuario, Meta
    from app.models.Evento import Evento, Recordatorio  # noqa: F401
    SQLModel.metadata.create_all(Motor)
    # Migracion simple para agregar columna 'Mensaje' en 'recordatorio' si no existe (SQLite)
    try:
        with Motor.connect() as conn:  # type: ignore[attr-defined]
            res = conn.exec_driver_sql("PRAGMA table_info('recordatorio')").fetchall()
            columnas = {row[1] for row in res} if res else set()
            if 'Mensaje' not in columnas:
                conn.exec_driver_sql("ALTER TABLE recordatorio ADD COLUMN Mensaje VARCHAR NULL")
    except Exception:
        # Fallback silencioso; en entornos limpios la tabla se crea con la columna
        pass


def ObtenerSesion() -> Generator[Session, None, None]:
    with Session(Motor) as SesionBD:
        yield SesionBD
