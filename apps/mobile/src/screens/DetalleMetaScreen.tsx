import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';
import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Meta } from '../api/ClienteApi';

type Parametros = { DetalleMeta: { meta: Meta } };

export default function DetalleMetaScreen(): JSX.Element {
  const ruta = useRoute<RouteProp<Parametros, 'DetalleMeta'>>();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const meta = ruta.params?.meta;

  if (!meta) {
    return (
      <View style={Estilos.Contenedor}> 
        <Text>No se encontró la meta.</Text>
      </View>
    );
  }

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>{meta.Titulo}</Text>
      {meta.Descripcion ? <Text style={Estilos.Campo}>Descripcion: {meta.Descripcion}</Text> : null}
      <Text style={Estilos.Campo}>Tipo: {meta.TipoMeta}</Text>
      <Text style={Estilos.Campo}>PropietarioId: {meta.PropietarioId}</Text>
      {meta.CreadoEn ? <Text style={Estilos.Campo}>CreadoEn: {meta.CreadoEn}</Text> : null}
      {meta.ActualizadoEn ? <Text style={Estilos.Campo}>ActualizadoEn: {meta.ActualizadoEn}</Text> : null}
      <View style={{ height: 12 }} />
      <Button title="Editar" onPress={() => navigation.navigate('CrearEditarMeta')} />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 22, fontWeight: '700', marginBottom: 12 },
  Campo: { fontSize: 16, marginBottom: 6 }
});
