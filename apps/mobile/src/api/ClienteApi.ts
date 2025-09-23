import { ApiUrl } from '../config';

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

export async function ObtenerEventos(): Promise<Evento[]> {
  const r = await fetch(`${ApiUrl}/eventos`);
  if (!r.ok) throw new Error('Error al cargar eventos');
  return r.json();
}

export async function CrearEvento(datos: Omit<Evento, 'Id'|'CreadoEn'|'ActualizadoEn'|'EliminadoEn'>): Promise<Evento> {
  const params = new URLSearchParams();
  Object.entries(datos).forEach(([k,v]) => params.append(k, String(v)));
  const r = await fetch(`${ApiUrl}/eventos?${params.toString()}`, { method: 'POST' });
  if (!r.ok) throw new Error('Error al crear evento');
  return r.json();
}

export async function ActualizarEvento(Id: number, cambios: Partial<Omit<Evento,'Id'|'CreadoEn'|'EliminadoEn'>>): Promise<Evento> {
  const params = new URLSearchParams();
  Object.entries(cambios).forEach(([k,v]) => {
    if (v !== undefined && v !== null) params.append(k, String(v));
  });
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

export async function ObtenerRecordatorios(): Promise<Recordatorio[]> {
  const r = await fetch(`${ApiUrl}/recordatorios`);
  if (!r.ok) throw new Error('Error al cargar recordatorios');
  return r.json();
}

export async function ObtenerRecordatoriosProximos(dias = 7): Promise<Recordatorio[]> {
  const r = await fetch(`${ApiUrl}/recordatorios/proximos?dias=${dias}`);
  if (!r.ok) throw new Error('Error al cargar recordatorios proximos');
  return r.json();
}

export async function CrearRecordatorio(datos: Omit<Recordatorio,'Id'|'CreadoEn'|'EliminadoEn'|'Enviado'>): Promise<Recordatorio> {
  const params = new URLSearchParams();
  Object.entries(datos).forEach(([k,v]) => params.append(k, String(v)));
  const r = await fetch(`${ApiUrl}/recordatorios?${params.toString()}`, { method: 'POST' });
  if (!r.ok) throw new Error('Error al crear recordatorio');
  return r.json();
}
