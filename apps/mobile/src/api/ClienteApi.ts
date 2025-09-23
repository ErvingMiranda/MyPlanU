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
