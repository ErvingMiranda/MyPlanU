from typing import List, Optional

from sqlmodel import Session, select

from app.models.Goal import Meta


class MetaServicio:
    def Crear(self, SesionBD: Session, Titulo: str, Descripcion: Optional[str] = None) -> Meta:
        MetaNueva = Meta(Titulo=Titulo, Descripcion=Descripcion)
        SesionBD.add(MetaNueva)
        SesionBD.commit()
        SesionBD.refresh(MetaNueva)
        return MetaNueva

    def Listar(self, SesionBD: Session) -> List[Meta]:
        Consulta = select(Meta)
        return list(SesionBD.exec(Consulta))
