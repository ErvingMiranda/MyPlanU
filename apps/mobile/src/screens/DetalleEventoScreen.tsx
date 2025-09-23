import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';
import { useRoute, RouteProp, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Evento } from '../api/ClienteApi';

type Parametros = { DetalleEvento: { evento: Evento } };

export default function DetalleEventoScreen(): JSX.Element {
  const ruta = useRoute<RouteProp<Parametros, 'DetalleEvento'>>();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const evento = ruta.params?.evento;

  if (!evento) {
    return (
      <View style={Estilos.Contenedor}><Text>No se encontro el evento.</Text></View>
    );
  }

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>{evento.Titulo}</Text>
      <Text style={Estilos.Campo}>Inicio: {new Date(evento.Inicio).toLocaleString()}</Text>
      <Text style={Estilos.Campo}>Fin: {new Date(evento.Fin).toLocaleString()}</Text>
      {evento.Descripcion ? <Text style={Estilos.Campo}>Descripcion: {evento.Descripcion}</Text> : null}
      {evento.Ubicacion ? <Text style={Estilos.Campo}>Ubicacion: {evento.Ubicacion}</Text> : null}
      <View style={{ height: 12 }} />
      <Button title="Editar" onPress={() => navigation.navigate('CrearEditarEvento', { evento })} />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 20, fontWeight: '700', marginBottom: 12 },
  Campo: { fontSize: 16, marginBottom: 6 }
});
