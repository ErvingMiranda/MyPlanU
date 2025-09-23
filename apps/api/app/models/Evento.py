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
    # Repeticion (opcional)
    FrecuenciaRepeticion: Optional[str] = Field(default=None, regex="^(Diaria|Semanal|Mensual)$")
    IntervaloRepeticion: Optional[int] = None  # cada N unidades
    DiasSemana: Optional[str] = None  # CSV: "Lun,Mar,Mie" (solo para Semanal)
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
    # Repeticion (opcional)
    FrecuenciaRepeticion: Optional[str] = Field(default=None, regex="^(Diaria|Semanal|Mensual)$")
    IntervaloRepeticion: Optional[int] = None
    DiasSemana: Optional[str] = None
    Enviado: bool = False
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
    EliminadoEn: Optional[datetime] = None

    EventoRef: Optional[Evento] = Relationship(back_populates="Recordatorios")


class ParticipanteEvento(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    EventoId: int = Field(foreign_key="evento.Id")
    UsuarioId: int = Field(foreign_key="usuario.Id")
    Rol: str = Field(regex="^(Dueno|Colaborador|Lector)$")
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
