import React, { useState } from 'react';
import { View, Text, StyleSheet, Switch, Button, TextInput, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ActualizarUsuario } from '../api/ClienteApi';
import { EstablecerZonaHoraria, ObtenerZonaHoraria } from '../userPrefs';

export default function ConfiguracionScreen(): JSX.Element {
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const [TemaOscuro, EstablecerTemaOscuro] = useState(false);
  const [Notificar, EstablecerNotificar] = useState(false);
  const [UsuarioId, EstablecerUsuarioId] = useState<string>('1');
  const [ZonaHoraria, EstablecerZona] = useState<string>(ObtenerZonaHoraria() ?? 'UTC');

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>Configuracion</Text>
      <View style={Estilos.Fila}>
        <Text>Tema Oscuro</Text>
        <Switch value={TemaOscuro} onValueChange={EstablecerTemaOscuro} />
      </View>
      <View style={Estilos.Fila}>
        <Text>Notificaciones</Text>
        <Switch value={Notificar} onValueChange={EstablecerNotificar} />
      </View>
      <Text>UsuarioId</Text>
      <TextInput style={Estilos.Input} keyboardType="numeric" value={UsuarioId} onChangeText={EstablecerUsuarioId} placeholder="Id de usuario" />
      <Text>Zona Horaria (IANA, ej: America/Mexico_City)</Text>
      <TextInput style={Estilos.Input} value={ZonaHoraria} onChangeText={EstablecerZona} placeholder="Ej: UTC o America/Bogota" />
      <View style={Estilos.Acciones}>
        <Button title="Guardar" onPress={async () => {
          try {
            EstablecerZonaHoraria(ZonaHoraria);
            const id = parseInt(UsuarioId, 10);
            if (id) await ActualizarUsuario(id, { ZonaHoraria });
            Alert.alert('Listo', 'Preferencias guardadas');
            navigation.navigate('HomeTabs');
          } catch (e: any) {
            Alert.alert('Error', e?.message ?? 'No se pudo guardar');
          }
        }} />
  <Button title="Cancelar" onPress={() => navigation.navigate('HomeTabs')} />
      </View>
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 18, fontWeight: '600', marginBottom: 8 },
  Fila: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  Acciones: { flexDirection: 'row', justifyContent: 'space-between' },
  Input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 12 }
});
