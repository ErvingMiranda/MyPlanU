from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship


class Evento(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    MetaId: int = Field(foreign_key="meta.Id")
    PropietarioId: int = Field(foreign_key="usuario.Id")
    Titulo: str
    Descripcion: Optional[str] = None
    Inicio: datetime
    Fin: datetime
    Ubicacion: Optional[str] = None
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
    ActualizadoEn: Optional[datetime] = None
    EliminadoEn: Optional[datetime] = None

    Recordatorios: list["Recordatorio"] = Relationship(back_populates="EventoRef")


class Recordatorio(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    EventoId: int = Field(foreign_key="evento.Id")
    FechaHora: datetime
    Canal: str = Field(regex="^(Local|Push)$")
    Mensaje: Optional[str] = None
    Enviado: bool = False
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
    EliminadoEn: Optional[datetime] = None

    EventoRef: Optional[Evento] = Relationship(back_populates="Recordatorios")
