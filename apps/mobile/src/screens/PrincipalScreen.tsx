import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Button } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { ObtenerMetas, Meta } from '../api/ClienteApi';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<any, any>;

export default function PrincipalScreen({ navigation }: Props): JSX.Element {
  const { data, isLoading, isError, refetch } = useQuery({ queryKey: ['metas'], queryFn: ObtenerMetas });

  return (
    <View style={Estilos.Contenedor}>
      <View style={Estilos.BarraAcciones}>
        <Button title="+" onPress={() => navigation.navigate('CrearEditarMeta')} />
  <Button title="VerEventos" onPress={() => navigation.navigate('ListaEventos')} />
  <Button title="Notificaciones" onPress={() => navigation.navigate('Notificaciones')} />
        <Button title="Configuracion" onPress={() => navigation.navigate('Configuracion')} />
        <Button title="CerrarSesion" onPress={() => navigation.replace('LoginRegistro')} />
      </View>
      {isLoading && <ActivityIndicator />} 
      {isError && <Text>Ocurrió un error al cargar las metas.</Text>}
      <FlatList
        data={data ?? []}
        keyExtractor={(item) => String(item.Id)}
        renderItem={({ item }) => (
          <TouchableOpacity style={Estilos.Item} onPress={() => navigation.navigate('DetalleMeta', { meta: item })}>
            <Text style={Estilos.Titulo}>{item.Titulo}</Text>
            <Text style={Estilos.Subtitulo}>Tipo: {item.TipoMeta}</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={!isLoading ? <Text>No hay metas aún.</Text> : null}
      />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  BarraAcciones: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  Item: { padding: 12, borderRadius: 8, backgroundColor: '#f2f2f2', marginBottom: 8 },
  Titulo: { fontSize: 18, fontWeight: '600' },
  Subtitulo: { fontSize: 14, color: '#444' }
});
