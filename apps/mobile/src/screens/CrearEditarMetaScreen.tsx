import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, Button, Alert } from 'react-native';

export default function CrearEditarMetaScreen(): JSX.Element {
  const [Titulo, EstablecerTitulo] = useState('');
  const [TipoMeta, EstablecerTipoMeta] = useState('SALUD');
  const [Descripcion, EstablecerDescripcion] = useState('');

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.TituloPantalla}>Crear / Editar Meta</Text>
      <Text>Titulo</Text>
      <TextInput style={Estilos.Input} value={Titulo} onChangeText={EstablecerTitulo} placeholder="Ej. Correr 5km" />
      <Text>TipoMeta</Text>
      <TextInput style={Estilos.Input} value={TipoMeta} onChangeText={EstablecerTipoMeta} placeholder="SALUD|FINANZAS|CARRERA|OTRA" />
      <Text>Descripcion</Text>
      <TextInput style={[Estilos.Input, { height: 80 }]} value={Descripcion} onChangeText={EstablecerDescripcion} multiline />
      <View style={Estilos.Acciones}>
        <Button title="Guardar" onPress={() => Alert.alert('Pendiente', 'Persistencia no implementada en v0.4')} />
        <Button title="Cancelar" onPress={() => Alert.alert('Cancelado')} />
      </View>
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  TituloPantalla: { fontSize: 20, fontWeight: '600', marginBottom: 12 },
  Input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 12 },
  Acciones: { flexDirection: 'row', justifyContent: 'space-between' }
});
