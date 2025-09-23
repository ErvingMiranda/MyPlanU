import React, { useMemo, useState } from 'react';
import { View, Text, Button, StyleSheet, FlatList, TextInput, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { CrearRecordatorio, ObtenerRecordatoriosProximos, Recordatorio } from '../api/ClienteApi';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ObtenerZonaHoraria } from '../userPrefs';

function FormatearTiempoRestante(iso: string): string {
  const ahora = new Date();
  const objetivo = new Date(iso);
  const diffMs = objetivo.getTime() - ahora.getTime();
  if (diffMs <= 0) return 'vencido';
  const minutos = Math.floor(diffMs / 60000);
  if (minutos < 60) return `${minutos} min`;
  const horas = Math.floor(minutos / 60);
  const remMin = minutos % 60;
  return remMin > 0 ? `${horas} h ${remMin} min` : `${horas} h`;
}

export default function NotificacionesScreen(): JSX.Element {
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const clienteQuery = useQueryClient();
  const dias = 7;
  const zona = ObtenerZonaHoraria();
  const { data, isLoading, isError } = useQuery({ queryKey: ['proximos', dias, zona], queryFn: () => ObtenerRecordatoriosProximos(dias, 1) });

  const [EventoId, EstablecerEventoId] = useState('');
  const [FechaHora, EstablecerFechaHora] = useState('');
  const [Mensaje, EstablecerMensaje] = useState('');

  const mutacion = useMutation({
    mutationFn: async () => {
      const eventoId = parseInt(EventoId, 10);
      if (!eventoId || !FechaHora) throw new Error('EventoId y FechaHora son obligatorios');
      return CrearRecordatorio({ EventoId: eventoId, FechaHora, Canal: 'Local', Mensaje, UsuarioId: 1 });
    },
    onSuccess: () => {
      clienteQuery.invalidateQueries({ queryKey: ['proximos'] });
      EstablecerEventoId('');
      EstablecerFechaHora('');
      EstablecerMensaje('');
    }
  });

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>Notificaciones (Recordatorios proximos)</Text>
      <View style={Estilos.Formulario}>
        <Text style={Estilos.Seccion}>Crear recordatorio rapido</Text>
        <Text>EventoId</Text>
        <TextInput style={Estilos.Input} keyboardType="numeric" value={EventoId} onChangeText={EstablecerEventoId} placeholder="Ej. 1" />
        <Text>FechaHora (ISO futuro)</Text>
        <TextInput style={Estilos.Input} value={FechaHora} onChangeText={EstablecerFechaHora} placeholder="YYYY-MM-DDTHH:mm:ss" />
        <Text>Mensaje (opcional)</Text>
        <TextInput style={Estilos.Input} value={Mensaje} onChangeText={EstablecerMensaje} placeholder="Ej. 'Revisar tarea'" />
        <Button title={mutacion.isPending ? 'Creando...' : 'Crear recordatorio'} onPress={() => mutacion.mutate()} disabled={mutacion.isPending} />
      </View>
      <View style={{ height: 12 }} />
      {isLoading && <ActivityIndicator />}
      {isError && <Text>Ocurrio un error al cargar recordatorios.</Text>}
      <FlatList
        data={data ?? []}
        keyExtractor={(item) => String(item.Id)}
        renderItem={({ item }) => (
          <View style={Estilos.Item}>
            <Text style={Estilos.ItemTitulo}>Evento #{item.EventoId}</Text>
            <Text>{new Date(item.FechaHora).toLocaleString()} — {FormatearTiempoRestante(item.FechaHora)}</Text>
            {item.Mensaje ? <Text style={Estilos.Mensaje}>"{item.Mensaje}"</Text> : null}
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No hay recordatorios proximos.</Text> : null}
      />
      <View style={{ height: 8 }} />
  <Button title="Volver" onPress={() => navigation.navigate('HomeTabs')} />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 18, fontWeight: '600', marginBottom: 8 },
  Seccion: { fontSize: 16, fontWeight: '600', marginBottom: 8 },
  Formulario: { padding: 12, borderWidth: 1, borderColor: '#ddd', borderRadius: 8 },
  Input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 8 },
  Item: { padding: 12, borderRadius: 8, backgroundColor: '#f2f2f2', marginBottom: 8 },
  ItemTitulo: { fontSize: 16, fontWeight: '600' },
  Mensaje: { fontStyle: 'italic', color: '#333' }
});
