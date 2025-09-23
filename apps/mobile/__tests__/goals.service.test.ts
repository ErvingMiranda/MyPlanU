import MockAdapter from 'axios-mock-adapter';
import { http } from '../src/api/http';
import { listGoals } from '../src/services/goals';
import { __clearOfflineForTests } from '../src/offline';

describe('goals service', () => {
  const mock = new MockAdapter(http);

  afterEach(async () => {
    mock.reset();
    await __clearOfflineForTests();
  });

  it('lists goals successfully', async () => {
    mock.onGet('/metas').reply(200, [{ Id: 1, PropietarioId: 1, Titulo: 'A', TipoMeta: 'OTRA' }]);
    const metas = await listGoals();
    expect(metas.length).toBe(1);
    expect(metas[0].Titulo).toBe('A');
  });

  it('normalizes 404 error', async () => {
    mock.onGet('/metas').reply(404, { detail: 'No hay metas' });
    await expect(listGoals()).rejects.toMatchObject({ code: 404, message: 'No hay metas' });
  });

  it('maps timeout to TIMEOUT', async () => {
    mock.onGet('/metas').timeout();
    await expect(listGoals()).rejects.toMatchObject({ code: 'TIMEOUT' });
  });
});
