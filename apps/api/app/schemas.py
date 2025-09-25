from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

# ---- Meta ----
class MetaBase(BaseModel):
    Titulo: str = Field(..., min_length=1)
    TipoMeta: str = Field(..., regex=r"^(Individual|Colectiva)$")
    Descripcion: Optional[str] = None

class MetaCrear(MetaBase):
    PropietarioId: int

class MetaActualizar(BaseModel):
    Titulo: Optional[str] = Field(None, min_length=1)
    TipoMeta: Optional[str] = Field(None, regex=r"^(Individual|Colectiva)$")
    Descripcion: Optional[str] = None

class MetaRespuesta(MetaBase):
    Id: int
    PropietarioId: int
    CreadoEn: datetime
    ActualizadoEn: Optional[datetime]
    EliminadoEn: Optional[datetime]

    class Config:
        from_attributes = True

# ---- Evento ----
class EventoBase(BaseModel):
    MetaId: int
    PropietarioId: int
    Titulo: str
    Inicio: datetime
    Fin: datetime
    Descripcion: Optional[str] = None
    Ubicacion: Optional[str] = None
    FrecuenciaRepeticion: Optional[str] = Field(None, regex=r"^(Diaria|Semanal|Mensual)$")
    IntervaloRepeticion: Optional[int] = Field(None, ge=1)
    DiasSemana: Optional[List[str]] = None  # Se convertirá a CSV en modelo persistente

    @validator("Fin")
    def validar_intervalo(cls, v, values):  # type: ignore
        ini = values.get("Inicio")
        if ini and v <= ini:
            raise ValueError("Fin debe ser mayor que Inicio")
        return v

class EventoCrear(EventoBase):
    pass

class EventoActualizar(BaseModel):
    Titulo: Optional[str] = None
    Inicio: Optional[datetime] = None
    Fin: Optional[datetime] = None
    Descripcion: Optional[str] = None
    Ubicacion: Optional[str] = None
    FrecuenciaRepeticion: Optional[str] = Field(None, regex=r"^(Diaria|Semanal|Mensual)$")
    IntervaloRepeticion: Optional[int] = Field(None, ge=1)
    DiasSemana: Optional[List[str]] = None

    @validator("Fin")
    def validar_fin(cls, v, values):  # type: ignore
        # Validación cruzada se hará en service si solo llega Fin
        return v

class EventoRespuesta(BaseModel):
    Id: int
    MetaId: int
    PropietarioId: int
    Titulo: str
    Descripcion: Optional[str]
    Inicio: datetime
    Fin: datetime
    Ubicacion: Optional[str]
    FrecuenciaRepeticion: Optional[str]
    IntervaloRepeticion: Optional[int]
    DiasSemana: Optional[str]
    CreadoEn: datetime
    ActualizadoEn: Optional[datetime]
    EliminadoEn: Optional[datetime]

    class Config:
        from_attributes = True

# ---- Recordatorio ----
class RecordatorioBase(BaseModel):
    EventoId: int
    FechaHora: datetime
    Canal: str = Field(..., regex=r"^(Local|Push)$")
    Mensaje: Optional[str] = None
    FrecuenciaRepeticion: Optional[str] = Field(None, regex=r"^(Diaria|Semanal|Mensual)$")
    IntervaloRepeticion: Optional[int] = Field(None, ge=1)
    DiasSemana: Optional[List[str]] = None

class RecordatorioCrear(RecordatorioBase):
    pass

class RecordatorioActualizar(BaseModel):
    FechaHora: Optional[datetime] = None
    Canal: Optional[str] = Field(None, regex=r"^(Local|Push)$")
    Mensaje: Optional[str] = None
    Enviado: Optional[bool] = None
    FrecuenciaRepeticion: Optional[str] = Field(None, regex=r"^(Diaria|Semanal|Mensual)$")
    IntervaloRepeticion: Optional[int] = Field(None, ge=1)
    DiasSemana: Optional[List[str]] = None

class RecordatorioRespuesta(BaseModel):
    Id: int
    EventoId: int
    FechaHora: datetime
    Canal: str
    Mensaje: Optional[str]
    FrecuenciaRepeticion: Optional[str]
    IntervaloRepeticion: Optional[int]
    DiasSemana: Optional[str]
    Enviado: bool
    CreadoEn: datetime
    EliminadoEn: Optional[datetime]

    class Config:
        from_attributes = True
