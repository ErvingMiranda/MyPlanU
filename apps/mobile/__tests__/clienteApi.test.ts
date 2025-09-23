import { ObtenerRecordatoriosProximos, RecuperarMeta } from '../src/api/ClienteApi';

describe('ClienteApi with manual fetch mocks', () => {
  const originalFetch = global.fetch;

  afterEach(() => { global.fetch = originalFetch as any; });

  it('gets proximos recordatorios', async () => {
    global.fetch = jest.fn(async (url: any) => {
      const u = new URL(String(url));
      if (u.pathname.endsWith('/recordatorios/proximos')) {
        return new Response(JSON.stringify([
          { Id: 1, EventoId: 99, FechaHora: new Date(Date.now() + 3600_000).toISOString(), Canal: 'Local', Enviado: false, CreadoEn: new Date().toISOString() }
        ]), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }
      return new Response('', { status: 404 });
    }) as any;

    const items = await ObtenerRecordatoriosProximos(3, 1);
    expect(items.length).toBeGreaterThan(0);
    expect(items[0]).toHaveProperty('FechaHora');
  });

  it('maps 409 from recuperar meta', async () => {
    global.fetch = jest.fn(async (url: any, init?: RequestInit) => {
      const u = new URL(String(url));
      if (u.pathname.match(/\/metas\/\d+\/recuperar$/) && init?.method === 'POST') {
        return new Response(JSON.stringify({ detail: 'Meta padre eliminada' }), { status: 409, headers: { 'Content-Type': 'application/json' } });
      }
      return new Response('', { status: 404 });
    }) as any;

    await expect(RecuperarMeta(123)).rejects.toMatchObject({ code: 409, message: 'Meta padre eliminada' });
  });
});
