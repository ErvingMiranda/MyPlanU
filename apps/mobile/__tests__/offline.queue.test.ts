import MockAdapter from 'axios-mock-adapter';
import { http } from '../src/api/http';
import { __clearOfflineForTests, getQueue, processPending, enqueue, setCachedMetas, getCachedMetas } from '../src/offline';
import { createGoal, updateGoal, listGoals } from '../src/services/goals';

/** Util para crear meta base fake en cache */
async function seedCache(goal: any) { await setCachedMetas([goal]); }

const mock = new MockAdapter(http);

describe('offline queue JSON body', () => {
  beforeEach(async () => { mock.reset(); await __clearOfflineForTests(); });

  it('flujo base: create en offline -> encola y luego sync', async () => {
    // Simular fallo de red en POST /metas
    mock.onPost('/metas').networkError();
    const goal = await createGoal({ PropietarioId: 1, Titulo: 'Meta Offline', TipoMeta: 'Individual' });
    expect(goal.Id).toBeLessThan(0); // tempId
    let q = await getQueue();
    expect(q.length).toBe(1);
    // Ahora la red responde OK
    mock.reset();
    mock.onPost('/metas').reply(201, { Id: 10, PropietarioId: 1, Titulo: 'Meta Offline', TipoMeta: 'Individual', CreadoEn: new Date().toISOString() });
    const res = await processPending(http);
    expect(res.ok).toBe(1);
    q = await getQueue();
    expect(q.length).toBe(0);
    const cache = await getCachedMetas();
    expect(cache?.[0].Id).toBe(10);
  });

  it('retry parcial: primera falla, segunda ok', async () => {
    // Seed dos operaciones (create y create) simulando offline inicial
    await enqueue({ kind: 'create', entity: 'Meta', tempId: -1, payload: { PropietarioId: 1, Titulo: 'A', TipoMeta: 'Individual' } });
    await enqueue({ kind: 'create', entity: 'Meta', tempId: -2, payload: { PropietarioId: 1, Titulo: 'B', TipoMeta: 'Individual' } });
    // Primera falla con 409, segunda éxito
    mock.onPost('/metas').replyOnce(409, { detail: 'Duplicado' }).onPost('/metas').reply(201, { Id: 22, PropietarioId: 1, Titulo: 'B', TipoMeta: 'Individual', CreadoEn: new Date().toISOString() });
    const r = await processPending(http);
    expect(r.ok).toBe(1);
    expect(r.fail).toBe(1);
    const q = await getQueue();
    expect(q.length).toBe(1);
    expect(q[0].kind).toBe('create');
    expect((q[0] as any).tempId).toBe(-1); // la fallida persiste
  });

  it('orden de ejecucion: create luego update sobre misma meta', async () => {
    // create offline
    mock.onPost('/metas').networkError();
    const g = await createGoal({ PropietarioId: 1, Titulo: 'G1', TipoMeta: 'Individual' });
    // update offline (meta aun con tempId)
    mock.onPatch(/\/metas\//).networkError();
    const updated = await updateGoal(g.Id, { Titulo: 'G1-Edit' });
    expect(updated.Titulo).toBe('G1-Edit');
    let q = await getQueue();
    expect(q.length).toBe(2);
    // Sincronizar: create -> server asigna Id=100; luego update aplica sobre ese Id
    mock.reset();
    mock.onPost('/metas').reply(201, { Id: 100, PropietarioId: 1, Titulo: 'G1', TipoMeta: 'Individual', CreadoEn: new Date().toISOString() });
    mock.onPatch('/metas/100').reply(200, { Id: 100, PropietarioId: 1, Titulo: 'G1-Edit', TipoMeta: 'Individual', CreadoEn: new Date().toISOString(), ActualizadoEn: new Date().toISOString() });
    const res = await processPending(http);
    expect(res.ok).toBe(2);
    q = await getQueue();
    expect(q.length).toBe(0);
    const cache = await getCachedMetas();
    expect(cache?.[0].Titulo).toBe('G1-Edit');
  });

  it('persistencia cola: elementos siguen tras reinicio simulado', async () => {
    await enqueue({ kind: 'create', entity: 'Meta', tempId: -5, payload: { PropietarioId: 9, Titulo: 'Persist', TipoMeta: 'Individual' } });
    // Simular "reinicio": simplemente re-leer queue
    const q = await getQueue();
    expect(q.length).toBe(1);
  });
});
