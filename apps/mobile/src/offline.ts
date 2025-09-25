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
const K_QUEUE = 'OFFLINE_QUEUE';

export type GoalCache = Array<{ Id: number; PropietarioId: number; Titulo: string; TipoMeta: string; Descripcion?: string | null; CreadoEn?: string | null; ActualizadoEn?: string | null; EliminadoEn?: string | null }>

export type PendingOp =
  | { kind: 'create'; entity: 'Meta'; tempId: number; payload: any }
  | { kind: 'update'; entity: 'Meta'; targetId: number; payload: any };

export async function getCachedMetas(): Promise<GoalCache | null> {
  const raw = await getItem(K_METAS);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

export async function setCachedMetas(metas: GoalCache): Promise<void> {
  await setItem(K_METAS, JSON.stringify(metas));
}

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

export async function processPending(http: import('axios').AxiosInstance): Promise<{ ok: number; fail: number }> {
  let ok = 0, fail = 0;
  const q = await getQueue();
  if (q.length === 0) return { ok, fail };
  let metas = (await getCachedMetas()) ?? [];
  const next: PendingOp[] = [];
  for (const op of q) {
    try {
      if (op.entity === 'Meta' && op.kind === 'create') {
        const r = await http.post(`/metas`, op.payload); // JSON body
        const created = r.data;
        metas = metas.map(m => (m.Id === op.tempId ? created : m));
        ok++;
      } else if (op.entity === 'Meta' && op.kind === 'update') {
        const r = await http.patch(`/metas/${op.targetId}`, op.payload); // JSON body
        const updated = r.data;
        metas = metas.map(m => (m.Id === op.targetId ? { ...m, ...updated } : m));
        ok++;
      }
    } catch {
      // keep for next round
      next.push(op);
      fail++;
    }
  }
  await setQueue(next);
  await setCachedMetas(metas);
  return { ok, fail };
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
      await AsyncStorage.removeItem(K_QUEUE);
    } else {
      mem.delete(K_METAS);
      mem.delete(K_QUEUE);
    }
  } catch {
    mem.delete(K_METAS);
    mem.delete(K_QUEUE);
  }
}
