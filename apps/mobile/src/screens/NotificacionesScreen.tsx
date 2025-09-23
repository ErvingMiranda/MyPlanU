import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

export default function NotificacionesScreen(): JSX.Element {
  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>Notificaciones</Text>
      <Text>No hay notificaciones por ahora.</Text>
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 18, fontWeight: '600', marginBottom: 8 }
});
