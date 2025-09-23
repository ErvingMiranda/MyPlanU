import React, { useState } from 'react';
import { View, Text, StyleSheet, Switch, Button, Alert } from 'react-native';

export default function ConfiguracionScreen(): JSX.Element {
  const [TemaOscuro, EstablecerTemaOscuro] = useState(false);
  const [Notificar, EstablecerNotificar] = useState(false);

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
      <View style={Estilos.Acciones}>
        <Button title="Guardar" onPress={() => Alert.alert('Guardado', 'Se guardaran en futuro release.')} />
        <Button title="Cancelar" onPress={() => Alert.alert('Cancelado')} />
      </View>
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 18, fontWeight: '600', marginBottom: 8 },
  Fila: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  Acciones: { flexDirection: 'row', justifyContent: 'space-between' }
});
