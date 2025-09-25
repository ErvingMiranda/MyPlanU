import { http } from '../api/http';
import { mapHttpError, type HttpError } from '../api/errors';
import { getCachedMetas, setCachedMetas, enqueue } from '../offline';

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

export async function listGoals(): Promise<Goal[]> {
  try {
    const r = await http.get('/metas');
    const metas = r.data as Goal[];
    // cache on success
    await setCachedMetas(metas as any);
    return metas;
  } catch (e) {
    const err = normalizeError(e);
    // On network-only errors, return cached if available and non-empty
    if (err.code === 'NETWORK' || err.code === 'TIMEOUT') {
      const cached = await getCachedMetas();
      if (cached && cached.length > 0) return cached as any;
    }
    throw err;
  }
}

export async function getGoal(Id: number): Promise<Goal> {
  try { const r = await http.get(`/metas/${Id}`); return r.data as Goal; } catch (e) { throw normalizeError(e); }
}

export async function createGoal(datos: CreateGoal): Promise<Goal> {
  try {
    const r = await http.post(`/metas`, datos); // JSON body
    return r.data as Goal;
  } catch (e) {
    const err = normalizeError(e);
    if (err.code === 'NETWORK' || err.code === 'TIMEOUT') {
      // optimistic local create with temp Id (negative)
      const tempId = -Math.floor(Math.random() * 1_000_000) - 1;
      const now = new Date().toISOString();
      const optimistic: Goal = { Id: tempId, PropietarioId: datos.PropietarioId, Titulo: datos.Titulo, TipoMeta: datos.TipoMeta, Descripcion: datos.Descripcion ?? null, CreadoEn: now } as any;
      const cached = (await getCachedMetas()) ?? [];
      await setCachedMetas([optimistic as any, ...cached]);
      await enqueue({ kind: 'create', entity: 'Meta', tempId, payload: datos });
      return optimistic;
    }
    throw err;
  }
}

export async function updateGoal(Id: number, cambios: UpdateGoal): Promise<Goal> {
  try { const r = await http.patch(`/metas/${Id}`, cambios); return r.data as Goal; } catch (e) {
    const err = normalizeError(e);
    if (err.code === 'NETWORK' || err.code === 'TIMEOUT') {
      const cached = (await getCachedMetas()) ?? [];
      const idx = cached.findIndex(m => m.Id === Id);
      if (idx >= 0) {
        const updated = { ...cached[idx], ...cambios, ActualizadoEn: new Date().toISOString() } as any;
        cached[idx] = updated;
        await setCachedMetas(cached as any);
        await enqueue({ kind: 'update', entity: 'Meta', targetId: Id, payload: cambios });
        return updated;
      }
    }
    throw err;
  }
}

export async function deleteGoal(Id: number): Promise<{ ok: true }> {
  try { const r = await http.delete(`/metas/${Id}`); return r.data as { ok: true }; } catch (e) { throw normalizeError(e); }
}
