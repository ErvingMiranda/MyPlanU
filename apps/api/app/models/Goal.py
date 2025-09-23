from typing import Optional

from sqlmodel import Field, SQLModel


class Meta(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    Titulo: str
    Descripcion: Optional[str] = None
