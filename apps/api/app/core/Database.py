from typing import Generator

from sqlmodel import Session, SQLModel, create_engine


URLBaseDatos = "sqlite:///./datos.db"
Motor = create_engine(URLBaseDatos, echo=False, connect_args={"check_same_thread": False})


def IniciarTablas() -> None:
    SQLModel.metadata.create_all(Motor)


def ObtenerSesion() -> Generator[Session, None, None]:
    with Session(Motor) as SesionBD:
        yield SesionBD
