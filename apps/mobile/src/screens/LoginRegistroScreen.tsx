import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<any, any>;

export default function LoginRegistroScreen({ navigation }: Props): JSX.Element {
  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>Bienvenido a MyPlanU</Text>
      <Button title="Entrar" onPress={() => navigation.replace('Principal')} />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 },
  Titulo: { fontSize: 22, fontWeight: '600', marginBottom: 16 }
});
