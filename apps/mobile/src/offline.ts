// Minimal offline cache and queue using AsyncStorage with an in-memory fallback for test/runtime without RN.
let AsyncStorage: any;
try { AsyncStorage = require('@react-native-async-storage/async-storage').default; } catch { AsyncStorage = null; }

const mem = new Map<string, string>();
async function getItem(key: string): Promise<string | null> {
  try { return AsyncStorage ? await AsyncStorage.getItem(key) : (mem.get(key) ?? null); } catch { return mem.get(key) ?? null; }
}
async function setItem(key: string, value: string): Promise<void> {
  try { return AsyncStorage ? await AsyncStorage.setItem(key, value) : void mem.set(key, value); } catch { mem.set(key, value); }
}

const K_METAS = 'OFFLINE_METAS_CACHE';
const K_EVENTOS = 'OFFLINE_EVENTOS_CACHE';
const K_QUEUE = 'OFFLINE_QUEUE';
const K_QUEUE_EVENTS = 'OFFLINE_QUEUE_EVENTS';

export type GoalCache = Array<{ Id: number; PropietarioId: number; Titulo: string; TipoMeta: string; Descripcion?: string | null; CreadoEn?: string | null; ActualizadoEn?: string | null; EliminadoEn?: string | null }>
export type EventoCache = Array<{ Id: number; MetaId: number; PropietarioId: number; Titulo: string; Descripcion?: string | null; Inicio: string; Fin: string; Ubicacion?: string | null; CreadoEn?: string | null; ActualizadoEn?: string | null; EliminadoEn?: string | null }>

export type PendingOp =
  | { kind: 'create'; entity: 'Meta'; tempId: number; payload: any }
  | { kind: 'update'; entity: 'Meta'; targetId: number; payload: any };

export type PendingEventOp =
  | { kind: 'create'; entity: 'Evento'; tempId: number; payload: any }
  | { kind: 'update'; entity: 'Evento'; targetId: number; payload: any };

export async function getCachedMetas(): Promise<GoalCache | null> {
  const raw = await getItem(K_METAS);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

export async function setCachedMetas(metas: GoalCache): Promise<void> {
  await setItem(K_METAS, JSON.stringify(metas));
}

export async function getCachedEventos(): Promise<EventoCache | null> {
  const raw = await getItem(K_EVENTOS);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}
export async function setCachedEventos(eventos: EventoCache): Promise<void> { await setItem(K_EVENTOS, JSON.stringify(eventos)); }

export async function getQueue(): Promise<PendingOp[]> {
  const raw = await getItem(K_QUEUE);
  if (!raw) return [];
  try { return JSON.parse(raw); } catch { return []; }
}

export async function setQueue(q: PendingOp[]): Promise<void> {
  await setItem(K_QUEUE, JSON.stringify(q));
}

export async function enqueue(op: PendingOp): Promise<void> {
  const q = await getQueue();
  q.push(op);
  await setQueue(q);
}

// Eventos queue
export async function getEventQueue(): Promise<PendingEventOp[]> {
  const raw = await getItem(K_QUEUE_EVENTS);
  if (!raw) return [];
  try { return JSON.parse(raw); } catch { return []; }
}
export async function setEventQueue(q: PendingEventOp[]): Promise<void> { await setItem(K_QUEUE_EVENTS, JSON.stringify(q)); }
export async function enqueueEvent(op: PendingEventOp): Promise<void> { const q = await getEventQueue(); q.push(op); await setEventQueue(q); }

export async function processPending(http: import('axios').AxiosInstance): Promise<{ ok: number; fail: number }> {
  let ok = 0, fail = 0;
  const q = await getQueue();
  if (q.length === 0) return { ok, fail };
  let metas = (await getCachedMetas()) ?? [];
  const idMap = new Map<number, number>(); // tempId -> realId
  const next: PendingOp[] = [];
  for (const op of q) {
    try {
      if (op.entity === 'Meta' && op.kind === 'create') {
        // Preferir batch cuando hay varias operaciones; si sólo hay una, usar endpoint directo por compatibilidad
        const r = await http.post(`/metas`, op.payload);
        const created = r.data;
        metas = metas.map(m => (m.Id === op.tempId ? created : m));
        // Registrar mapeo de tempId a Id real para operaciones subsecuentes en esta corrida
        if (typeof created?.Id === 'number') {
          idMap.set(op.tempId, created.Id);
        }
        ok++;
      } else if (op.entity === 'Meta' && op.kind === 'update') {
        // Si el targetId es un tempId de esta corrida, usar el Id real
        const target = idMap.get(op.targetId) ?? op.targetId;
        const r = await http.patch(`/metas/${target}`, op.payload);
        const updated = r.data;
        metas = metas.map(m => (m.Id === (idMap.get(op.targetId) ?? op.targetId) ? { ...m, ...updated } : m));
        ok++;
      }
    } catch {
      next.push(op);
      fail++;
    }
  }
  await setQueue(next);
  await setCachedMetas(metas);
  return { ok, fail };
}

// Nueva función: procesar colas por lotes usando /sync
export async function processPendingBatches(http: import('axios').AxiosInstance): Promise<{ metas: { ok: number; fail: number }, eventos: { ok: number; fail: number } }> {
  const metasQueue = await getQueue();
  const eventosQueue = await getEventQueue();
  const res = { metas: { ok: 0, fail: 0 }, eventos: { ok: 0, fail: 0 } };
  // Metas batch
  if (metasQueue.length > 0) {
    const operations = metasQueue.map((op, index) => op.kind === 'create'
      ? ({ kind: 'create', tempId: op.tempId, data: op.payload })
      : ({ kind: 'update', targetId: (op as any).targetId, data: op.payload })
    );
    try {
      const r = await http.post('/sync/metas', { operations, sequential: true, continueOnError: true });
      const data = r.data as { results: Array<any>, mappings: Record<string, number> };
      const mappings = data.mappings || {};
      let metas = (await getCachedMetas()) ?? [];
      for (let i = 0; i < data.results.length; i++) {
        const item = data.results[i];
        if (item.ok) {
          res.metas.ok++;
          if (item.tempId && mappings[String(item.tempId)]) {
            const real = mappings[String(item.tempId)];
            metas = metas.map(m => m.Id === item.tempId ? { ...m, Id: real } as any : m);
          }
        } else {
          res.metas.fail++;
        }
      }
      await setCachedMetas(metas);
      await setQueue([]);
    } catch {
      // dejar cola intacta
    }
  }
  // Eventos batch (placeholder: sólo envía batch, no actualiza caches de eventos en este commit)
  if (eventosQueue.length > 0) {
    const operations = eventosQueue.map(op => op.kind === 'create' ? ({ kind: 'create', tempId: op.tempId, data: op.payload }) : ({ kind: 'update', targetId: (op as any).targetId, data: op.payload }));
    try {
      const r = await http.post('/sync/eventos', { operations, sequential: true, continueOnError: true });
      const data = r.data as { results: Array<any> };
      for (const item of data.results) { if (item.ok) res.eventos.ok++; else res.eventos.fail++; }
      await setEventQueue([]);
    } catch { /* leave queue */ }
  }
  return res;
}

export function toQuery(params: Record<string, any>) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v !== undefined && v !== null && q.append(k, String(v)));
  return q.toString();
}

// Test helpers: clear offline state between tests
export async function __clearOfflineForTests(): Promise<void> {
  try {
    if (AsyncStorage) {
      await AsyncStorage.removeItem(K_METAS);
      await AsyncStorage.removeItem(K_EVENTOS);
      await AsyncStorage.removeItem(K_QUEUE);
      await AsyncStorage.removeItem(K_QUEUE_EVENTS);
    } else {
      mem.delete(K_METAS);
      mem.delete(K_EVENTOS);
      mem.delete(K_QUEUE);
      mem.delete(K_QUEUE_EVENTS);
    }
  } catch {
    mem.delete(K_METAS);
    mem.delete(K_EVENTOS);
    mem.delete(K_QUEUE);
    mem.delete(K_QUEUE_EVENTS);
  }
}
