import { http, HttpResponse } from 'msw';

const API = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const handlers = [
  http.get(`${API}/recordatorios/proximos`, ({ request }) => {
    const url = new URL(request.url);
    const dias = url.searchParams.get('dias');
    if (!dias) return HttpResponse.json({ detail: 'dias requerido' }, { status: 400 });
    return HttpResponse.json([
      { Id: 1, EventoId: 99, FechaHora: new Date(Date.now() + 3600_000).toISOString(), Canal: 'Local', Enviado: false, CreadoEn: new Date().toISOString() }
    ]);
  }),
  http.post(`${API}/metas/:id/recuperar`, () => HttpResponse.json({ Id: 42, PropietarioId: 1, Titulo: 'Meta', TipoMeta: 'OTRA', CreadoEn: new Date().toISOString() })),
  http.post(`${API}/eventos/:id/recuperar`, () => HttpResponse.json({ Id: 77, MetaId: 42, PropietarioId: 1, Titulo: 'Ev', Inicio: new Date().toISOString(), Fin: new Date(Date.now()+3600_000).toISOString(), CreadoEn: new Date().toISOString() })),
];
