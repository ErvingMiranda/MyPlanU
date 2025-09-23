import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, Button } from 'react-native';
import { showError, showSuccess, showRetry } from '../ui/toast';
import { logEvent } from '../telemetry';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ObtenerZonaHoraria } from '../userPrefs';
import { RecuperarMeta, RecuperarEvento, RecuperarRecordatorio, ObtenerMetasEliminadas, ObtenerEventosEliminados, ObtenerRecordatoriosEliminados, Meta, Evento, Recordatorio } from '../api/ClienteApi';

function useFetch<T>(key: any[], fetcher: () => Promise<T[]>) {
  const zona = ObtenerZonaHoraria();
  return useQuery<T[]>({ queryKey: [...key, zona], queryFn: fetcher });
}

export default function PapeleraScreen(): React.ReactElement {
  const cliente = useQueryClient();
  const [Tab, setTab] = useState<'Metas'|'Eventos'|'Recordatorios'>('Metas');
  const metas = useFetch<Meta>(['papelera','metas'], () => ObtenerMetasEliminadas());
  const eventos = useFetch<Evento>(['papelera','eventos'], () => ObtenerEventosEliminados());
  const recs = useFetch<Recordatorio>(['papelera','recordatorios'], () => ObtenerRecordatoriosEliminados());

  return (
    <View style={Estilos.Contenedor}>
      <View style={Estilos.Tabs}>
        <Button title="Metas" onPress={() => setTab('Metas')} />
        <Button title="Eventos" onPress={() => setTab('Eventos')} />
        <Button title="Recordatorios" onPress={() => setTab('Recordatorios')} />
      </View>
      {Tab === 'Metas' && (
        <Lista
          titulo="Metas eliminadas"
          loading={metas.isLoading}
          error={metas.isError}
          data={metas.data ?? []}
          renderItem={(m: Meta) => (
            <ItemContainer>
              <Text style={Estilos.ItemTitulo}>{m.Titulo}</Text>
              <Text>EliminadoEn: {m.EliminadoEn ? new Date(m.EliminadoEn).toLocaleString() : '-'}</Text>
              <Button title="Recuperar" onPress={async () => { try { await RecuperarMeta(m.Id); cliente.invalidateQueries({ queryKey: ['papelera'] }); showSuccess('Meta recuperada'); logEvent('recover_success', { tipo: 'Meta', Id: m.Id }); } catch (err: any) { logEvent('recover_error', { tipo: 'Meta', Id: m.Id, message: err?.message }); showRetry(err?.message ?? 'No se pudo recuperar', async () => { try { await RecuperarMeta(m.Id); cliente.invalidateQueries({ queryKey: ['papelera'] }); showSuccess('Meta recuperada'); logEvent('recover_success', { tipo: 'Meta', Id: m.Id, retry: true }); } catch (e: any) { logEvent('recover_error', { tipo: 'Meta', Id: m.Id, message: e?.message, retry: true }); showError(e?.message ?? 'No se pudo recuperar'); } }); } }} />
            </ItemContainer>
          )}
        />
      )}
      {Tab === 'Eventos' && (
        <Lista
          titulo="Eventos eliminados"
          loading={eventos.isLoading}
          error={eventos.isError}
          data={eventos.data ?? []}
          renderItem={(e: Evento) => (
            <ItemContainer>
              <Text style={Estilos.ItemTitulo}>{e.Titulo}</Text>
              <Text>MetaId: {e.MetaId}</Text>
              <Text>EliminadoEn: {e.EliminadoEn ? new Date(e.EliminadoEn).toLocaleString() : '-'}</Text>
              <Button title="Recuperar" onPress={async () => {
                try {
                  await RecuperarEvento(e.Id, e.PropietarioId);
                  cliente.invalidateQueries({ queryKey: ['papelera'] });
                  showSuccess('Evento recuperado');
                  logEvent('recover_success', { tipo: 'Evento', Id: e.Id });
                } catch (err: any) {
                  logEvent('recover_error', { tipo: 'Evento', Id: e.Id, message: err?.message });
                  showRetry(err?.message ?? 'No se pudo recuperar', async () => { try { await RecuperarEvento(e.Id, e.PropietarioId); cliente.invalidateQueries({ queryKey: ['papelera'] }); showSuccess('Evento recuperado'); logEvent('recover_success', { tipo: 'Evento', Id: e.Id, retry: true }); } catch (e: any) { logEvent('recover_error', { tipo: 'Evento', Id: e.Id, message: e?.message, retry: true }); showError(e?.message ?? 'No se pudo recuperar'); } });
                }
              }} />
            </ItemContainer>
          )}
        />
      )}
      {Tab === 'Recordatorios' && (
        <Lista
          titulo="Recordatorios eliminados"
          loading={recs.isLoading}
          error={recs.isError}
          data={recs.data ?? []}
          renderItem={(r: Recordatorio) => (
            <ItemContainer>
              <Text>Recordatorio #{r.Id} de Evento #{r.EventoId}</Text>
              <Text>EliminadoEn: {r.EliminadoEn ? new Date(r.EliminadoEn).toLocaleString() : '-'}</Text>
              <Button title="Recuperar" onPress={async () => {
                try {
                  await RecuperarRecordatorio(r.Id);
                  cliente.invalidateQueries({ queryKey: ['papelera'] });
                  showSuccess('Recordatorio recuperado');
                  logEvent('recover_success', { tipo: 'Recordatorio', Id: r.Id });
                } catch (err: any) {
                  logEvent('recover_error', { tipo: 'Recordatorio', Id: r.Id, message: err?.message });
                  showRetry(err?.message ?? 'No se pudo recuperar', async () => { try { await RecuperarRecordatorio(r.Id); cliente.invalidateQueries({ queryKey: ['papelera'] }); showSuccess('Recordatorio recuperado'); logEvent('recover_success', { tipo: 'Recordatorio', Id: r.Id, retry: true }); } catch (e: any) { logEvent('recover_error', { tipo: 'Recordatorio', Id: r.Id, message: e?.message, retry: true }); showError(e?.message ?? 'No se pudo recuperar'); } });
                }
              }} />
            </ItemContainer>
          )}
        />
      )}
    </View>
  );
}

function Lista({ titulo, loading, error, data, renderItem }: { titulo: string; loading: boolean; error: boolean; data: any[]; renderItem: (x: any) => React.ReactElement }) {
  return (
    <View style={{ flex: 1 }}>
      <Text style={Estilos.Titulo}>{titulo}</Text>
      {loading && <ActivityIndicator />}
      {error && <Text>Ocurrio un error al cargar.</Text>}
      <FlatList data={data} keyExtractor={(it) => String(it.Id)} renderItem={({ item }) => renderItem(item)} ListEmptyComponent={!loading ? <Text>Vacio</Text> : null} />
    </View>
  );
}

function ItemContainer({ children }: { children: React.ReactNode }) {
  return <View style={Estilos.Item}>{children}</View>;
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Tabs: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12 },
  Titulo: { fontSize: 18, fontWeight: '600', marginBottom: 8 },
  Item: { padding: 12, borderRadius: 8, backgroundColor: '#f2f2f2', marginBottom: 8 },
  ItemTitulo: { fontSize: 16, fontWeight: '600' },
});
