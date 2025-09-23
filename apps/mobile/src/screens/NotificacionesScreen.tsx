import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Meta } from '../api/ClienteApi';

export default function NotificacionesScreen(): JSX.Element {
  const navigation = useNavigation<NativeStackNavigationProp<any>>();

  const IrADetalleMock = () => {
    const metaMock: Meta = {
      Id: 0,
      PropietarioId: 0,
      Titulo: 'Meta de ejemplo (mock)',
      Descripcion: 'Generada desde Notificaciones',
      TipoMeta: 'OTRA',
      CreadoEn: new Date().toISOString(),
      ActualizadoEn: null,
      EliminadoEn: null
    };
    navigation.navigate('DetalleMeta', { meta: metaMock });
  };

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>Notificaciones</Text>
      <Text>No hay notificaciones por ahora.</Text>
      <View style={{ height: 12 }} />
      <Button title="Ver detalle (mock)" onPress={IrADetalleMock} />
      <View style={{ height: 8 }} />
      <Button title="Volver" onPress={() => navigation.navigate('Principal')} />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 18, fontWeight: '600', marginBottom: 8 }
});
