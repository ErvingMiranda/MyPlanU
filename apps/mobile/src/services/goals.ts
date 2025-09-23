import { http } from '../api/http';
import { mapHttpError, type HttpError } from '../api/errors';

export type Goal = {
  Id: number;
  PropietarioId: number;
  Titulo: string;
  Descripcion?: string | null;
  TipoMeta: string;
  CreadoEn?: string | null;
  ActualizadoEn?: string | null;
  EliminadoEn?: string | null;
};

export type CreateGoal = {
  PropietarioId: number;
  Titulo: string;
  TipoMeta: string;
  Descripcion?: string | null;
};

export type UpdateGoal = Partial<Pick<CreateGoal, 'Titulo' | 'TipoMeta' | 'Descripcion'>>;

function normalizeError(e: any): HttpError { return mapHttpError(e); }

function toQuery(params: Record<string, any>) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v !== undefined && v !== null && q.append(k, String(v)));
  return q.toString();
}

export async function listGoals(): Promise<Goal[]> {
  try {
    const r = await http.get('/metas');
    return r.data as Goal[];
  } catch (e) {
    throw normalizeError(e);
  }
}

export async function getGoal(Id: number): Promise<Goal> {
  try {
    const r = await http.get(`/metas/${Id}`);
    return r.data as Goal;
  } catch (e) {
    throw normalizeError(e);
  }
}

export async function createGoal(datos: CreateGoal): Promise<Goal> {
  try {
    const r = await http.post(`/metas?${toQuery(datos)}`);
    return r.data as Goal;
  } catch (e) {
    throw normalizeError(e);
  }
}

export async function updateGoal(Id: number, cambios: UpdateGoal): Promise<Goal> {
  try {
    const r = await http.patch(`/metas/${Id}?${toQuery(cambios)}`);
    return r.data as Goal;
  } catch (e) {
    throw normalizeError(e);
  }
}

export async function deleteGoal(Id: number): Promise<{ ok: true }>
{  try {
    const r = await http.delete(`/metas/${Id}`);
    return r.data as { ok: true };
  } catch (e) {
    throw normalizeError(e);
  }
}
