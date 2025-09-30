from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class NotificacionSistema(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    UsuarioId: int = Field(foreign_key="usuario.Id", index=True)
    Tipo: str = Field(regex="^(EventoEliminado)$", index=True)
    ReferenciaId: int = Field(index=True)
    Mensaje: str
    CreadoEn: datetime = Field(default_factory=datetime.utcnow)
    LeidaEn: Optional[datetime] = None
