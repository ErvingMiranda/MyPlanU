import React from 'react';
import { SafeAreaView, Text, View, StyleSheet } from 'react-native';

function PantallaInicio(): JSX.Element {
  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>MyPlanU</Text>
      <Text>Bienvenido a v0.1</Text>
    </View>
  );
}

export default function AplicacionMovil(): JSX.Element {
  return (
    <SafeAreaView style={Estilos.Contenedor}>
      <PantallaInicio />
    </SafeAreaView>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  Titulo: { fontSize: 24, fontWeight: '600' }
});
