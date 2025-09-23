import { http, getNetworkErrorMessage } from '../api/http';

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

export type HttpError = {
  code: number | 'NETWORK' | 'TIMEOUT';
  message: string;
  hint?: string;
};

function normalizeError(e: any): HttpError {
  const isAxios = !!e?.isAxiosError || !!e?.response || !!e?.request;
  if (!isAxios) return { code: 'NETWORK', message: String(e?.message || e) };
  const status: number | undefined = e?.response?.status;
  if (e?.code === 'ECONNABORTED') return { code: 'TIMEOUT', message: 'La solicitud excedió el tiempo de espera.', hint: 'Verifica tu conexión o intenta de nuevo.' };
  if (status === 404) return { code: 404, message: e?.response?.data?.detail || 'Recurso no encontrado.' };
  if (status === 409) return { code: 409, message: e?.response?.data?.detail || 'Conflicto de datos.' };
  if (!status) return { code: 'NETWORK', message: getNetworkErrorMessage(e), hint: 'Revisa API_BASE_URL o tu conexión.' };
  return { code: status, message: e?.response?.data?.detail || e?.message || 'Error de servidor' };
}

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
