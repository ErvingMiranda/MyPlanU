import { ApiUrl } from '../config';
import { ObtenerZonaHoraria } from '../userPrefs';

export type Meta = {
  Id: number;
  PropietarioId: number;
  Titulo: string;
  Descripcion?: string | null;
  TipoMeta: string;
  CreadoEn: string;
  ActualizadoEn?: string | null;
  EliminadoEn?: string | null;
};

export async function ObtenerMetas(): Promise<Meta[]> {
  const r = await fetch(`${ApiUrl}/metas`);
  if (!r.ok) throw new Error('Error al cargar metas');
  return r.json();
}

export type Evento = {
  Id: number;
  MetaId: number;
  PropietarioId: number;
  Titulo: string;
  Descripcion?: string | null;
  Inicio: string; // ISO
  Fin: string; // ISO
  Ubicacion?: string | null;
  CreadoEn: string;
  ActualizadoEn?: string | null;
  EliminadoEn?: string | null;
};

export async function ObtenerEventos(UsuarioId?: number): Promise<Evento[]> {
  const params = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const q = params.toString();
  const r = await fetch(`${ApiUrl}/eventos${q ? `?${q}` : ''}`);
  if (!r.ok) throw new Error('Error al cargar eventos');
  return r.json();
}

export async function CrearEvento(datos: Omit<Evento, 'Id'|'CreadoEn'|'ActualizadoEn'|'EliminadoEn'> & { ZonaHorariaEntrada?: string; UsuarioId?: number }): Promise<Evento> {
  const params = new URLSearchParams();
  Object.entries(datos).forEach(([k,v]) => v !== undefined && v !== null && params.append(k, String(v)));
  const zona = ObtenerZonaHoraria();
  if (!datos.ZonaHorariaEntrada && zona) params.append('ZonaHorariaEntrada', zona);
  if (datos.UsuarioId) params.append('UsuarioId', String(datos.UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const r = await fetch(`${ApiUrl}/eventos?${params.toString()}`, { method: 'POST' });
  if (!r.ok) throw new Error('Error al crear evento');
  return r.json();
}

export async function ActualizarEvento(Id: number, cambios: Partial<Omit<Evento,'Id'|'CreadoEn'|'EliminadoEn'>> & { ZonaHorariaEntrada?: string; UsuarioId?: number }): Promise<Evento> {
  const params = new URLSearchParams();
  Object.entries(cambios).forEach(([k,v]) => {
    if (v !== undefined && v !== null) params.append(k, String(v));
  });
  const zona = ObtenerZonaHoraria();
  if (!cambios.ZonaHorariaEntrada && zona) params.append('ZonaHorariaEntrada', zona);
  if (cambios.UsuarioId) params.append('UsuarioId', String(cambios.UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const r = await fetch(`${ApiUrl}/eventos/${Id}?${params.toString()}`, { method: 'PATCH' });
  if (!r.ok) throw new Error('Error al actualizar evento');
  return r.json();
}

export type Recordatorio = {
  Id: number;
  EventoId: number;
  FechaHora: string; // ISO
  Canal: 'Local' | 'Push';
  Mensaje?: string | null;
  Enviado: boolean;
  CreadoEn: string;
  EliminadoEn?: string | null;
};

export async function ObtenerRecordatorios(UsuarioId?: number): Promise<Recordatorio[]> {
  const params = new URLSearchParams();
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const q = params.toString();
  const r = await fetch(`${ApiUrl}/recordatorios${q ? `?${q}` : ''}`);
  if (!r.ok) throw new Error('Error al cargar recordatorios');
  return r.json();
}

export async function ObtenerRecordatoriosProximos(dias = 7, UsuarioId?: number): Promise<Recordatorio[]> {
  const params = new URLSearchParams();
  params.append('dias', String(dias));
  const zona = ObtenerZonaHoraria();
  if (UsuarioId) params.append('UsuarioId', String(UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const r = await fetch(`${ApiUrl}/recordatorios/proximos?${params.toString()}`);
  if (!r.ok) throw new Error('Error al cargar recordatorios proximos');
  return r.json();
}

export async function CrearRecordatorio(datos: Omit<Recordatorio,'Id'|'CreadoEn'|'EliminadoEn'|'Enviado'> & { ZonaHorariaEntrada?: string; UsuarioId?: number }): Promise<Recordatorio> {
  const params = new URLSearchParams();
  Object.entries(datos).forEach(([k,v]) => v !== undefined && v !== null && params.append(k, String(v)));
  const zona = ObtenerZonaHoraria();
  if (!datos.ZonaHorariaEntrada && zona) params.append('ZonaHorariaEntrada', zona);
  if (datos.UsuarioId) params.append('UsuarioId', String(datos.UsuarioId));
  if (zona) params.append('ZonaHoraria', zona);
  const r = await fetch(`${ApiUrl}/recordatorios?${params.toString()}`, { method: 'POST' });
  if (!r.ok) throw new Error('Error al crear recordatorio');
  return r.json();
}

// Usuarios API (para actualizar zona horaria)
export type Usuario = {
  Id: number;
  Correo: string;
  Nombre: string;
  ZonaHoraria: string;
  CreadoEn: string;
  EliminadoEn?: string | null;
};

export async function ActualizarUsuario(Id: number, cambios: Partial<Pick<Usuario,'Correo'|'Nombre'|'ZonaHoraria'>>): Promise<Usuario> {
  const params = new URLSearchParams();
  Object.entries(cambios).forEach(([k,v]) => v !== undefined && v !== null && params.append(k, String(v)));
  const r = await fetch(`${ApiUrl}/usuarios/${Id}?${params.toString()}`, { method: 'PATCH' });
  if (!r.ok) throw new Error('Error al actualizar usuario');
  return r.json();
}
