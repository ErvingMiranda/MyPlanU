import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Button } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Evento, ObtenerEventos } from '../api/ClienteApi';
import { getCachedEventos, setCachedEventos } from '../offline';
import { ObtenerZonaHoraria } from '../userPrefs';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<any, any>;

export default function ListaEventosScreen({ navigation }: Props): React.ReactElement {
  const zona = ObtenerZonaHoraria();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['eventos', zona],
    queryFn: async () => {
      try {
        const evs = await ObtenerEventos(1);
        // cache on success
        await setCachedEventos(evs as any);
        return evs;
      } catch (e) {
        const cached = await getCachedEventos();
        if (cached && cached.length > 0) return cached as any;
        throw e;
      }
    }
  });

  return (
    <View style={Estilos.Contenedor}>
      <View style={Estilos.BarraAcciones}>
        <Button title="Crear" onPress={() => navigation.navigate('CrearEditarEvento')} />
        <Button title="Refrescar" onPress={() => refetch()} />
      </View>
      {isLoading && <ActivityIndicator />}
  {isError && <Text>Ocurrio un error al cargar eventos.</Text>}
      <FlatList
        data={data ?? []}
        keyExtractor={(item) => String(item.Id)}
        renderItem={({ item }) => (
          <TouchableOpacity style={Estilos.Item} onPress={() => navigation.navigate('DetalleEvento', { evento: item })}>
            <Text style={Estilos.Titulo}>{item.Titulo}</Text>
            <Text style={Estilos.Subtitulo}>{new Date(item.Inicio).toLocaleString()} → {new Date(item.Fin).toLocaleString()}</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={!isLoading ? <Text>No hay eventos.</Text> : null}
      />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  BarraAcciones: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  Item: { padding: 12, borderRadius: 8, backgroundColor: '#f2f2f2', marginBottom: 8 },
  Titulo: { fontSize: 18, fontWeight: '600' },
  Subtitulo: { fontSize: 12, color: '#444' }
});
