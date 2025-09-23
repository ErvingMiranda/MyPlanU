import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, Button, Alert } from 'react-native';
import { createGoal } from '../services/goals';
import { useNavigation } from '@react-navigation/native';

export default function CrearEditarMetaScreen(): JSX.Element {
  const navigation = useNavigation<any>();
  const [Titulo, EstablecerTitulo] = useState('');
  const [TipoMeta, EstablecerTipoMeta] = useState('SALUD');
  const [Descripcion, EstablecerDescripcion] = useState('');
  const [Guardando, SetGuardando] = useState(false);

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
        <Button title={Guardando ? 'Guardando…' : 'Guardar'} disabled={Guardando} onPress={async () => {
          try {
            if (!Titulo.trim()) { Alert.alert('Validación', 'El título es requerido'); return; }
            SetGuardando(true);
            await createGoal({ Titulo, TipoMeta, Descripcion, PropietarioId: 1 });
            Alert.alert('Éxito', 'Meta guardada');
            navigation.goBack();
          } catch (e: any) {
            Alert.alert('Error', e?.message ?? 'No se pudo guardar la meta');
          } finally {
            SetGuardando(false);
          }
        }} />
        <Button title="Cancelar" onPress={() => navigation.goBack()} />
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
