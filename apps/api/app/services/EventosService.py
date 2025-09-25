from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models.Evento import Evento, Recordatorio
from app.models.Goal import Meta
from app.services.UsuariosService import UsuariosService
from app.core.Permisos import RolParticipante


class EventosService:
    def __init__(self) -> None:
        self.Usuarios = UsuariosService()

    def _ListaADiasCSV(self, dias: Optional[List[str]]) -> Optional[str]:
        if not dias:
            return None
        # Normalizar eliminando espacios y conservando orden
        return ",".join([d.strip() for d in dias if d and d.strip()]) or None

    def _DiasCSV_ALista(self, csv: Optional[str]) -> Optional[List[str]]:
        if not csv:
            return None
        return [d.strip() for d in csv.split(',') if d.strip()]

    def CrearEvento(
        self,
        SesionBD: Session,
        MetaId: int,
        PropietarioId: int,
        Titulo: str,
        Inicio: datetime,
        Fin: datetime,
        Descripcion: Optional[str] = None,
        Ubicacion: Optional[str] = None,
        FrecuenciaRepeticion: Optional[str] = None,
        IntervaloRepeticion: Optional[int] = None,
        DiasSemana: Optional[List[str]] = None,
        Rol: RolParticipante = RolParticipante.Dueno,
    ) -> Optional[Evento]:
        # Permisos: Dueno/Colaborador pueden crear; Lector no
        if Rol == RolParticipante.Lector:
            return None
        # Validaciones: Inicio < Fin
        if not (Inicio < Fin):
            return None
        # Validacion repeticion
        if FrecuenciaRepeticion and (IntervaloRepeticion is not None) and IntervaloRepeticion <= 0:
            return None
        # Validar existencia de Meta y Usuario (no eliminados)
        MetaEntidad = SesionBD.get(Meta, MetaId)
        if not MetaEntidad or MetaEntidad.EliminadoEn is not None:
            return None
        if not self.Usuarios.Existe(SesionBD, Id=PropietarioId):
            return None

        Entidad = Evento(
            MetaId=MetaId,
            PropietarioId=PropietarioId,
            Titulo=Titulo,
            Descripcion=Descripcion,
            Inicio=Inicio,
            Fin=Fin,
            Ubicacion=Ubicacion,
            FrecuenciaRepeticion=FrecuenciaRepeticion,
            IntervaloRepeticion=IntervaloRepeticion,
            DiasSemana=self._ListaADiasCSV(DiasSemana),
        )
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def ListarEventos(self, SesionBD: Session) -> List[Evento]:
        Consulta = select(Evento).where(Evento.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def ListarEventosEliminados(
        self,
        SesionBD: Session,
        PropietarioId: Optional[int] = None,
        MetaId: Optional[int] = None,
        Desde: Optional[datetime] = None,
        Hasta: Optional[datetime] = None,
    ) -> List[Evento]:
        Consulta = select(Evento).where(Evento.EliminadoEn.is_not(None))
        if PropietarioId is not None:
            Consulta = Consulta.where(Evento.PropietarioId == PropietarioId)
        if MetaId is not None:
            Consulta = Consulta.where(Evento.MetaId == MetaId)
        if Desde is not None:
            Consulta = Consulta.where(Evento.EliminadoEn >= Desde)
        if Hasta is not None:
            Consulta = Consulta.where(Evento.EliminadoEn <= Hasta)
        return list(SesionBD.exec(Consulta))

    def _ParseDiasSemana(self, dias_csv: Optional[str]) -> List[int]:
        mapa = {
            'Lun': 0,
            'Mar': 1,
            'Mie': 2,
            'Jue': 3,
            'Vie': 4,
            'Sab': 5,
            'Dom': 6,
        }
        if not dias_csv:
            return []
        return [mapa[d.strip()] for d in dias_csv.split(',') if d.strip() in mapa]

    def ProyectarOcurrencias(
        self,
        SesionBD: Session,
        Desde: datetime,
        Hasta: datetime,
    ) -> List[Dict[str, Any]]:
        if Hasta <= Desde:
            return []
        ahora = datetime.utcnow()
        # Consideramos eventos no eliminados
        eventos = self.ListarEventos(SesionBD)
        ocurrencias: List[Dict[str, Any]] = []
        for ev in eventos:
            # Ocurrencia base (no repetido)
            base_ini = ev.Inicio
            base_fin = ev.Fin
            # Validacion de ventana
            if base_ini >= base_fin:
                continue
            freq = ev.FrecuenciaRepeticion
            intervalo = ev.IntervaloRepeticion or 1
            if not freq:
                # Evento simple: incluir si cruza el rango
                if base_fin >= Desde and base_ini <= Hasta and base_fin >= ahora:
                    ocurrencias.append({
                        'Titulo': ev.Titulo,
                        'Inicio': base_ini,
                        'Fin': base_fin,
                        'EventoId': ev.Id,
                    })
                continue
            # Expandir segun frecuencia
            cur_ini = base_ini
            cur_fin = base_fin
            # Empujar cur_ini a >= Desde si posible por saltos de intervalo
            # Iterar con limite de seguridad
            max_iters = 1000
            if freq == 'Diaria':
                delta = timedelta(days=intervalo)
                # avanzar hasta el rango
                while cur_fin < Desde and max_iters > 0:
                    cur_ini += delta
                    cur_fin += delta
                    max_iters -= 1
                while cur_ini <= Hasta and max_iters > 0:
                    if cur_fin >= Desde and cur_fin >= ahora:
                        ocurrencias.append({'Titulo': ev.Titulo, 'Inicio': cur_ini, 'Fin': cur_fin, 'EventoId': ev.Id})
                    cur_ini += delta
                    cur_fin += delta
                    max_iters -= 1
            elif freq == 'Semanal':
                dias = self._ParseDiasSemana(ev.DiasSemana)
                if not dias:
                    dias = [base_ini.weekday()]  # si no hay lista, usa el del inicio
                # Encontrar la primera semana que cae en rango
                semana_delta = timedelta(weeks=intervalo)
                # anclar a inicio de semana del base_ini (lunes=0)
                base_week_start = base_ini - timedelta(days=base_ini.weekday())
                cur_week_start = base_week_start
                while cur_week_start + timedelta(days=6) < Desde and max_iters > 0:
                    cur_week_start += semana_delta
                    max_iters -= 1
                while cur_week_start <= Hasta and max_iters > 0:
                    for d in dias:
                        occ_ini = cur_week_start + timedelta(days=d, hours=base_ini.hour, minutes=base_ini.minute, seconds=base_ini.second)
                        dur = base_fin - base_ini
                        occ_fin = occ_ini + dur
                        if occ_fin >= Desde and occ_ini <= Hasta and occ_fin >= ahora:
                            ocurrencias.append({'Titulo': ev.Titulo, 'Inicio': occ_ini, 'Fin': occ_fin, 'EventoId': ev.Id})
                    cur_week_start += semana_delta
                    max_iters -= 1
            elif freq == 'Mensual':
                # aproximacion simple por meses de 30 dias
                delta = timedelta(days=30 * intervalo)
                while cur_fin < Desde and max_iters > 0:
                    cur_ini += delta
                    cur_fin += delta
                    max_iters -= 1
                while cur_ini <= Hasta and max_iters > 0:
                    if cur_fin >= Desde and cur_fin >= ahora:
                        ocurrencias.append({'Titulo': ev.Titulo, 'Inicio': cur_ini, 'Fin': cur_fin, 'EventoId': ev.Id})
                    cur_ini += delta
                    cur_fin += delta
                    max_iters -= 1
        # ordenar por inicio
        ocurrencias.sort(key=lambda x: x['Inicio'])
        return ocurrencias

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Evento]:
        return SesionBD.get(Evento, Id)

    def ActualizarEvento(
        self,
        SesionBD: Session,
        Id: int,
        Titulo: Optional[str] = None,
        Descripcion: Optional[str] = None,
        Inicio: Optional[datetime] = None,
        Fin: Optional[datetime] = None,
        Ubicacion: Optional[str] = None,
        FrecuenciaRepeticion: Optional[str] = None,
        IntervaloRepeticion: Optional[int] = None,
        DiasSemana: Optional[List[str]] = None,
        Rol: RolParticipante = RolParticipante.Dueno,
    ) -> Optional[Evento]:
        # Permisos: Dueno/Colaborador pueden actualizar; Lector no
        if Rol == RolParticipante.Lector:
            return None
        Entidad = SesionBD.get(Evento, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if Inicio is not None:
            Entidad.Inicio = Inicio
        if Fin is not None:
            Entidad.Fin = Fin
        # Validar ventana de tiempo si ambos estan seteados o cambiaron
        if Entidad.Inicio >= Entidad.Fin:
            return None
        if FrecuenciaRepeticion is not None:
            if FrecuenciaRepeticion and (IntervaloRepeticion is not None) and IntervaloRepeticion <= 0:
                return None
        if Titulo is not None:
            Entidad.Titulo = Titulo
        if Descripcion is not None:
            Entidad.Descripcion = Descripcion
        if Ubicacion is not None:
            Entidad.Ubicacion = Ubicacion
        if FrecuenciaRepeticion is not None:
            Entidad.FrecuenciaRepeticion = FrecuenciaRepeticion
        if IntervaloRepeticion is not None:
            Entidad.IntervaloRepeticion = IntervaloRepeticion
        if DiasSemana is not None:
            Entidad.DiasSemana = self._ListaADiasCSV(DiasSemana)
        Entidad.ActualizadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def EliminarEvento(self, SesionBD: Session, Id: int, Rol: RolParticipante = RolParticipante.Dueno) -> bool:
        # Permisos: solo Dueno puede eliminar
        if Rol != RolParticipante.Dueno:
            return False
        Entidad = SesionBD.get(Evento, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        # Soft delete del evento
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        # Cascada logica: marcar recordatorios relacionados
        Consulta = select(Recordatorio).where(Recordatorio.EventoId == Id, Recordatorio.EliminadoEn.is_(None))
        for Rec in SesionBD.exec(Consulta):
            Rec.EliminadoEn = datetime.utcnow()
            SesionBD.add(Rec)
        # TODO: Notificar a participantes del evento sobre la eliminacion (integrar mecanismo de notificaciones)
        SesionBD.commit()
        return True

    def RecuperarEvento(self, SesionBD: Session, Id: int) -> Optional[Evento]:
        Entidad = SesionBD.get(Evento, Id)
        if not Entidad:
            return None
        if Entidad.EliminadoEn is None:
            return Entidad
        # Validar que la Meta no este eliminada
        MetaEntidad = SesionBD.get(Meta, Entidad.MetaId)
        if not MetaEntidad or MetaEntidad.EliminadoEn is not None:
            return None
        # TODO(bitacora): registrar quien y cuando recupera
        Entidad.EliminadoEn = None
        Entidad.ActualizadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad


class RecordatoriosService:
    def _ListaADiasCSV(self, dias: Optional[List[str]]) -> Optional[str]:
        if not dias:
            return None
        return ",".join([d.strip() for d in dias if d and d.strip()]) or None

    def _DiasCSV_ALista(self, csv: Optional[str]) -> Optional[List[str]]:
        if not csv:
            return None
        return [d.strip() for d in csv.split(',') if d.strip()]

    def CrearRecordatorio(
        self,
        SesionBD: Session,
        EventoId: int,
        FechaHora: datetime,
        Canal: str,
        Mensaje: Optional[str] = None,
        FrecuenciaRepeticion: Optional[str] = None,
        IntervaloRepeticion: Optional[int] = None,
        DiasSemana: Optional[List[str]] = None,
        Rol: RolParticipante = RolParticipante.Dueno,
    ) -> Optional[Recordatorio]:
        # Permisos: Dueno/Colaborador pueden crear; Lector no
        if Rol == RolParticipante.Lector:
            return None
        # No crear en el pasado
        if FechaHora < datetime.utcnow():
            return None
        if FrecuenciaRepeticion and (IntervaloRepeticion is not None) and IntervaloRepeticion <= 0:
            return None
        # Validar evento existe y no eliminado
        EventoEntidad = SesionBD.get(Evento, EventoId)
        if not EventoEntidad or EventoEntidad.EliminadoEn is not None:
            return None
        Entidad = Recordatorio(
            EventoId=EventoId,
            FechaHora=FechaHora,
            Canal=Canal,
            Mensaje=Mensaje,
            FrecuenciaRepeticion=FrecuenciaRepeticion,
            IntervaloRepeticion=IntervaloRepeticion,
            DiasSemana=self._ListaADiasCSV(DiasSemana),
        )
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def ListarRecordatorios(self, SesionBD: Session) -> List[Recordatorio]:
        Consulta = select(Recordatorio).where(Recordatorio.EliminadoEn.is_(None))
        return list(SesionBD.exec(Consulta))

    def ListarRecordatoriosEliminados(
        self,
        SesionBD: Session,
        EventoId: Optional[int] = None,
        Desde: Optional[datetime] = None,
        Hasta: Optional[datetime] = None,
    ) -> List[Recordatorio]:
        Consulta = select(Recordatorio).where(Recordatorio.EliminadoEn.is_not(None))
        if EventoId is not None:
            Consulta = Consulta.where(Recordatorio.EventoId == EventoId)
        if Desde is not None:
            Consulta = Consulta.where(Recordatorio.EliminadoEn >= Desde)
        if Hasta is not None:
            Consulta = Consulta.where(Recordatorio.EliminadoEn <= Hasta)
        return list(SesionBD.exec(Consulta))

    def Obtener(self, SesionBD: Session, Id: int) -> Optional[Recordatorio]:
        return SesionBD.get(Recordatorio, Id)

    def ActualizarRecordatorio(
        self,
        SesionBD: Session,
        Id: int,
        FechaHora: Optional[datetime] = None,
        Canal: Optional[str] = None,
        Enviado: Optional[bool] = None,
        Mensaje: Optional[str] = None,
        FrecuenciaRepeticion: Optional[str] = None,
        IntervaloRepeticion: Optional[int] = None,
        DiasSemana: Optional[List[str]] = None,
        Rol: RolParticipante = RolParticipante.Dueno,
    ) -> Optional[Recordatorio]:
        # Permisos: Dueno/Colaborador pueden actualizar; Lector no
        if Rol == RolParticipante.Lector:
            return None
        Entidad = SesionBD.get(Recordatorio, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return None
        if FechaHora is not None:
            if FechaHora < datetime.utcnow():
                return None
            Entidad.FechaHora = FechaHora
        if Canal is not None:
            Entidad.Canal = Canal
        if Enviado is not None:
            Entidad.Enviado = Enviado
        if Mensaje is not None:
            Entidad.Mensaje = Mensaje
        if FrecuenciaRepeticion is not None:
            Entidad.FrecuenciaRepeticion = FrecuenciaRepeticion
        if IntervaloRepeticion is not None:
            Entidad.IntervaloRepeticion = IntervaloRepeticion
        if DiasSemana is not None:
            Entidad.DiasSemana = self._ListaADiasCSV(DiasSemana)
        if Entidad.FrecuenciaRepeticion and Entidad.IntervaloRepeticion is not None and Entidad.IntervaloRepeticion <= 0:
            return None
        # No hay actualizadoEn en recordatorio por requerimiento
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad

    def CalcularProximasFechas(
        self,
        Entidad: Recordatorio,
        Desde: datetime,
        Hasta: datetime,
    ) -> List[datetime]:
        if Hasta <= Desde:
            return []
        ahora = datetime.utcnow()
        fechas: List[datetime] = []
        freq = Entidad.FrecuenciaRepeticion
        if not freq:
            if Entidad.FechaHora >= Desde and Entidad.FechaHora <= Hasta and Entidad.FechaHora >= ahora:
                return [Entidad.FechaHora]
            return []
        intervalo = Entidad.IntervaloRepeticion or 1
        base = Entidad.FechaHora
        max_iters = 1000
        if freq == 'Diaria':
            delta = timedelta(days=intervalo)
            cur = base
            while cur < Desde and max_iters > 0:
                cur += delta
                max_iters -= 1
            while cur <= Hasta and max_iters > 0:
                if cur >= Desde and cur >= ahora:
                    fechas.append(cur)
                cur += delta
                max_iters -= 1
        elif freq == 'Semanal':
            dias = EventosService()._ParseDiasSemana(Entidad.DiasSemana)
            if not dias:
                dias = [base.weekday()]
            semana_delta = timedelta(weeks=intervalo)
            base_week_start = base - timedelta(days=base.weekday())
            cur_week_start = base_week_start
            while cur_week_start + timedelta(days=6) < Desde and max_iters > 0:
                cur_week_start += semana_delta
                max_iters -= 1
            while cur_week_start <= Hasta and max_iters > 0:
                for d in dias:
                    occ = cur_week_start + timedelta(days=d, hours=base.hour, minutes=base.minute, seconds=base.second)
                    if occ >= Desde and occ <= Hasta and occ >= ahora:
                        fechas.append(occ)
                cur_week_start += semana_delta
                max_iters -= 1
        elif freq == 'Mensual':
            delta = timedelta(days=30 * intervalo)
            cur = base
            while cur < Desde and max_iters > 0:
                cur += delta
                max_iters -= 1
            while cur <= Hasta and max_iters > 0:
                if cur >= Desde and cur >= ahora:
                    fechas.append(cur)
                cur += delta
                max_iters -= 1
        return fechas

    def ListarProximos(self, SesionBD: Session, dias: int = 7) -> List[Recordatorio]:
        ahora = datetime.utcnow().replace(microsecond=0)
        futuro = ahora + timedelta(days=dias)
        Consulta = select(Recordatorio).where(
            Recordatorio.EliminadoEn.is_(None),
            Recordatorio.FechaHora >= ahora,
            Recordatorio.FechaHora <= futuro,
        )
        return list(SesionBD.exec(Consulta))

    def EliminarRecordatorio(self, SesionBD: Session, Id: int, Rol: RolParticipante = RolParticipante.Dueno) -> bool:
        # Permisos: por defecto solo Dueno puede eliminar
        if Rol != RolParticipante.Dueno:
            return False
        Entidad = SesionBD.get(Recordatorio, Id)
        if not Entidad or Entidad.EliminadoEn is not None:
            return False
        Entidad.EliminadoEn = datetime.utcnow()
        SesionBD.add(Entidad)
        SesionBD.commit()
        return True

    def RecuperarRecordatorio(self, SesionBD: Session, Id: int) -> Optional[Recordatorio]:
        Entidad = SesionBD.get(Recordatorio, Id)
        if not Entidad:
            return None
        if Entidad.EliminadoEn is None:
            return Entidad
        # Validar que el Evento padre exista y no este eliminado
        EventoEntidad = SesionBD.get(Evento, Entidad.EventoId)
        if not EventoEntidad or EventoEntidad.EliminadoEn is not None:
            return None
        # TODO(bitacora): registrar quien y cuando recupera
        Entidad.EliminadoEn = None
        SesionBD.add(Entidad)
        SesionBD.commit()
        SesionBD.refresh(Entidad)
        return Entidad
