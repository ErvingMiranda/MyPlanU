import { http } from '../api/http';

export type Goal = {
  Id: number;
  PropietarioId: number;
  Titulo: string;
  Descripcion?: string | null;
  TipoMeta: string;
};

export async function createGoal(datos: Omit<Goal, 'Id'>): Promise<Goal> {
  // Minimal implementation for v0.13.3 to replace placeholder
  const params = new URLSearchParams();
  Object.entries(datos).forEach(([k, v]) => v !== undefined && v !== null && params.append(k, String(v)));
  const r = await http.post('/metas?' + params.toString());
  return r.data;
}
