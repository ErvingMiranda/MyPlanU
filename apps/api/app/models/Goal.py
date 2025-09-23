from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship


class Usuario(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    Correo: str = Field(index=True, unique=True)
    Nombre: str
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
    EliminadoEn: Optional[datetime] = None

    Metas: list["Meta"] = Relationship(back_populates="Propietario")


class Meta(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    PropietarioId: int = Field(foreign_key="usuario.Id")
    Titulo: str
    Descripcion: Optional[str] = None
    TipoMeta: str = Field(regex="^(Individual|Colectiva)$")
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
    ActualizadoEn: Optional[datetime] = None
    EliminadoEn: Optional[datetime] = None

    Propietario: Optional[Usuario] = Relationship(back_populates="Metas")
