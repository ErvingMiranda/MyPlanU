import { ApiUrl } from '../config';
import { ObtenerZonaHoraria } from '../userPrefs';
import { fetchJson, type HttpError } from './errors';

export type Meta = { Id: number; PropietarioId: number; Titulo: string; Descripcion?: string | null; TipoMeta: string; CreadoEn: string; ActualizadoEn?: string | null; EliminadoEn?: string | null };

export async function ObtenerMetas(): Promise<Meta[]> { return fetchJson<Meta[]>(`${ApiUrl}/metas`, undefined, 'Error al cargar metas'); }

export type Evento = { Id: number; MetaId: number; PropietarioId: number; Titulo: string; Descripcion?: string | null; Inicio: string; Fin: string; Ubicacion?: string | null; CreadoEn: string; ActualizadoEn?: string | null; EliminadoEn?: string | null };

export async function ObtenerEventos(UsuarioId?: number): Promise<Evento[]> {
  const params = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const q = params.toString();
  return fetchJson<Evento[]>(`${ApiUrl}/eventos${q ? `?${q}` : ''}`, undefined, 'Error al cargar eventos');
}

// Nuevos contratos JSON
export type CrearEventoBody = { MetaId: number; PropietarioId: number; Titulo: string; Descripcion?: string | null; Inicio: string; Fin: string; Ubicacion?: string | null; Repeticion?: { Frecuencia?: string | null; Intervalo?: number | null; DiasSemana?: string[] | null } ; ZonaHorariaEntrada?: string; UsuarioId?: number };
export type ActualizarEventoBody = Partial<Omit<CrearEventoBody,'MetaId'|'PropietarioId'>> & { ZonaHorariaEntrada?: string; UsuarioId?: number };

export async function CrearEvento(datos: CrearEventoBody): Promise<Evento> {
  const zona = ObtenerZonaHoraria();
  const body = { ...datos } as any;
  if (!body.ZonaHorariaEntrada && zona) body.ZonaHorariaEntrada = zona;
  if (zona && !body.ZonaHoraria) body.ZonaHoraria = zona;
  return fetchJson<Evento>(`${ApiUrl}/eventos`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, 'Error al crear evento');
}

export async function ActualizarEvento(Id: number, cambios: ActualizarEventoBody): Promise<Evento> {
  const zona = ObtenerZonaHoraria();
  const body = { ...cambios } as any;
  if (!body.ZonaHorariaEntrada && zona) body.ZonaHorariaEntrada = zona;
  if (zona && !body.ZonaHoraria) body.ZonaHoraria = zona;
  return fetchJson<Evento>(`${ApiUrl}/eventos/${Id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, 'Error al actualizar evento');
}

export type Recordatorio = { Id: number; EventoId: number; FechaHora: string; Canal: 'Local' | 'Push'; Mensaje?: string | null; Enviado: boolean; CreadoEn: string; EliminadoEn?: string | null };

export async function ObtenerRecordatorios(UsuarioId?: number): Promise<Recordatorio[]> {
  const params = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const q = params.toString();
  return fetchJson<Recordatorio>(`${ApiUrl}/recordatorios${q ? `?${q}` : ''}` as any, undefined, 'Error al cargar recordatorios') as any;
}

export async function ObtenerRecordatoriosProximos(dias = 7, UsuarioId?: number): Promise<Recordatorio[]> {
  const params = new URLSearchParams();
  params.append('dias', String(dias));
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  return fetchJson<Recordatorio[]>(`${ApiUrl}/recordatorios/proximos?${params.toString()}`, undefined, 'Error al cargar recordatorios proximos');
}

export type CrearRecordatorioBody = { EventoId: number; FechaHora: string; Canal: 'Local' | 'Push'; Mensaje?: string | null; ZonaHorariaEntrada?: string; UsuarioId?: number };
export type ActualizarRecordatorioBody = Partial<Omit<CrearRecordatorioBody,'EventoId'>> & { ZonaHorariaEntrada?: string; UsuarioId?: number };

export async function CrearRecordatorio(datos: CrearRecordatorioBody): Promise<Recordatorio> {
  const zona = ObtenerZonaHoraria();
  const body = { ...datos } as any;
  if (!body.ZonaHorariaEntrada && zona) body.ZonaHorariaEntrada = zona;
  if (zona && !body.ZonaHoraria) body.ZonaHoraria = zona;
  return fetchJson<Recordatorio>(`${ApiUrl}/recordatorios`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, 'Error al crear recordatorio');
}

export async function ActualizarRecordatorio(Id: number, cambios: ActualizarRecordatorioBody): Promise<Recordatorio> {
  const zona = ObtenerZonaHoraria();
  const body = { ...cambios } as any;
  if (!body.ZonaHorariaEntrada && zona) body.ZonaHorariaEntrada = zona;
  if (zona && !body.ZonaHoraria) body.ZonaHoraria = zona;
  return fetchJson<Recordatorio>(`${ApiUrl}/recordatorios/${Id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, 'Error al actualizar recordatorio');
}

// Usuarios API (para actualizar zona horaria)
export type Usuario = { Id: number; Correo: string; Nombre: string; ZonaHoraria: string; CreadoEn: string; EliminadoEn?: string | null };
export async function ActualizarUsuario(Id: number, cambios: Partial<Pick<Usuario,'Correo'|'Nombre'|'ZonaHoraria'>>): Promise<Usuario> {
  const params = new URLSearchParams();
  Object.entries(cambios).forEach(([k,v]) => v !== undefined && v !== null && params.append(k, String(v)));
  return fetchJson<Usuario>(`${ApiUrl}/usuarios/${Id}?${params.toString()}`, { method: 'PATCH' }, 'Error al actualizar usuario');
}

export async function RecuperarMeta(Id: number): Promise<Meta> { return fetchJson<Meta>(`${ApiUrl}/metas/${Id}/recuperar`, { method: 'POST' }, 'No se pudo recuperar meta'); }
export async function RecuperarEvento(Id: number, UsuarioId?: number): Promise<Evento> {
  const params = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const q = params.toString();
  return fetchJson<Evento>(`${ApiUrl}/eventos/${Id}/recuperar${q ? `?${q}` : ''}`, { method: 'POST' }, 'No se pudo recuperar evento');
}
export async function RecuperarRecordatorio(Id: number, UsuarioId?: number): Promise<Recordatorio> {
  const params = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const q = params.toString();
  return fetchJson<Recordatorio>(`${ApiUrl}/recordatorios/${Id}/recuperar${q ? `?${q}` : ''}`, { method: 'POST' }, 'No se pudo recuperar recordatorio');
}

export async function ObtenerMetasEliminadas(params?: { PropietarioId?: number; Desde?: string; Hasta?: string; UsuarioId?: number }): Promise<Meta[]> {
  const q = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (params?.PropietarioId) q.append('PropietarioId', String(params.PropietarioId));
  if (params?.Desde) q.append('Desde', params.Desde);
  if (params?.Hasta) q.append('Hasta', params.Hasta);
  if (params?.UsuarioId) q.append('UsuarioId', String(params.UsuarioId));
  if (zona) q.append('ZonaHoraria', zona);
  return fetchJson<Meta[]>(`${ApiUrl}/papelera/metas?${q.toString()}`, undefined, 'Error al cargar metas eliminadas');
}
export async function ObtenerEventosEliminados(params?: { PropietarioId?: number; MetaId?: number; Desde?: string; Hasta?: string; UsuarioId?: number }): Promise<Evento[]> {
  const q = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (params?.PropietarioId) q.append('PropietarioId', String(params.PropietarioId));
  if (params?.MetaId) q.append('MetaId', String(params.MetaId));
  if (params?.Desde) q.append('Desde', params.Desde);
  if (params?.Hasta) q.append('Hasta', params.Hasta);
  if (params?.UsuarioId) q.append('UsuarioId', String(params.UsuarioId));
  if (zona) q.append('ZonaHoraria', zona);
  return fetchJson<Evento[]>(`${ApiUrl}/papelera/eventos?${q.toString()}`, undefined, 'Error al cargar eventos eliminados');
}
export async function ObtenerRecordatoriosEliminados(params?: { EventoId?: number; Desde?: string; Hasta?: string; UsuarioId?: number }): Promise<Recordatorio[]> {
  const q = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (params?.EventoId) q.append('EventoId', String(params.EventoId));
  if (params?.Desde) q.append('Desde', params.Desde);
  if (params?.Hasta) q.append('Hasta', params.Hasta);
  if (params?.UsuarioId) q.append('UsuarioId', String(params.UsuarioId));
  if (zona) q.append('ZonaHoraria', zona);
  return fetchJson<Recordatorio[]>(`${ApiUrl}/papelera/recordatorios?${q.toString()}`, undefined, 'Error al cargar recordatorios eliminados');
}
