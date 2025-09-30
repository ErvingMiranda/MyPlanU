from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class BitacoraRecuperacion(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    TipoEntidad: str = Field(index=True)
    EntidadId: int = Field(index=True)
    UsuarioId: Optional[int] = Field(default=None, foreign_key="usuario.Id", index=True)
    Detalle: Optional[str] = None
    RegistradoEn: datetime = Field(default_factory=datetime.utcnow, index=True)
