import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Button } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { APP_VERSION } from '../version';
// Se migra a servicio offline-aware de metas
import { listGoals, type Goal } from '../services/goals';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<any, any>;

export default function PrincipalScreen({ navigation }: Props): React.ReactElement {
  const { data, isLoading, isError } = useQuery({ queryKey: ['metas'], queryFn: listGoals });

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Version}>MyPlanU {APP_VERSION}</Text>
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
  data={(data as Goal[] | undefined) ?? []}
  keyExtractor={(item: Goal) => String(item.Id)}
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
  Version: { fontSize: 12, color: '#666', marginBottom: 6, textAlign: 'right' },
  BarraAcciones: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  Item: { padding: 12, borderRadius: 8, backgroundColor: '#f2f2f2', marginBottom: 8 },
  Titulo: { fontSize: 18, fontWeight: '600' },
  Subtitulo: { fontSize: 14, color: '#444' }
});
