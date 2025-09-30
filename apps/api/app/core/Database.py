from typing import Generator

from sqlmodel import Session, SQLModel, create_engine


URLBaseDatos = "sqlite:///./datos.db"
Motor = create_engine(URLBaseDatos, echo=False, connect_args={"check_same_thread": False})


def ObtenerEngine():
    return Motor


def IniciarTablas() -> None:
    # Importar modelos para registrar metadata antes de crear tablas
    from app.models import Goal  # noqa: F401  # Usuario, Meta
    from app.models.Evento import Evento, Recordatorio, ParticipanteEvento  # noqa: F401
    from app.models.Bitacora import BitacoraRecuperacion  # noqa: F401
    from app.models.Notificacion import NotificacionSistema  # noqa: F401
    SQLModel.metadata.create_all(Motor)
    # Migracion simple para agregar columna 'Mensaje' en 'recordatorio' si no existe (SQLite)
    try:
        with Motor.connect() as conn:  # type: ignore[attr-defined]
            # Usuario.ZonaHoraria
            res_u = conn.exec_driver_sql("PRAGMA table_info('usuario')").fetchall()
            cols_u = {row[1] for row in res_u} if res_u else set()
            if 'ZonaHoraria' not in cols_u:
                conn.exec_driver_sql("ALTER TABLE usuario ADD COLUMN ZonaHoraria VARCHAR NULL")
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
            # BitacoraRecuperacion table columns (no-op if table exists)
            conn.exec_driver_sql(
                "CREATE TABLE IF NOT EXISTS bitacorarecuperacion ("
                "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "TipoEntidad VARCHAR NOT NULL,"
                "EntidadId INTEGER NOT NULL,"
                "UsuarioId INTEGER NULL,"
                "Detalle VARCHAR NULL,"
                "RegistradoEn DATETIME NOT NULL,"
                "FOREIGN KEY(UsuarioId) REFERENCES usuario(Id)"
                ")"
            )
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_bitacora_tipo ON bitacorarecuperacion(TipoEntidad)")
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_bitacora_usuario ON bitacorarecuperacion(UsuarioId)")
            conn.exec_driver_sql(
                "CREATE TABLE IF NOT EXISTS notificacionsistema ("
                "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "UsuarioId INTEGER NOT NULL,"
                "Tipo VARCHAR NOT NULL,"
                "ReferenciaId INTEGER NOT NULL,"
                "Mensaje VARCHAR NOT NULL,"
                "CreadoEn DATETIME NOT NULL,"
                "LeidaEn DATETIME NULL,"
                "FOREIGN KEY(UsuarioId) REFERENCES usuario(Id)"
                ")"
            )
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_notifs_usuario ON notificacionsistema(UsuarioId)")
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_notifs_tipo ON notificacionsistema(Tipo)")
    except Exception:
        # Fallback silencioso; en entornos limpios la tabla se crea con la columna
        pass


def ObtenerSesion() -> Generator[Session, None, None]:
    with Session(Motor) as SesionBD:
        yield SesionBD
