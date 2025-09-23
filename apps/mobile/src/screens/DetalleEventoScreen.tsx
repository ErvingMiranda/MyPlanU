import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';
import { showSuccess, showError, showRetry } from '../ui/toast';
import { useRoute, RouteProp, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Evento, RecuperarEvento } from '../api/ClienteApi';

type Parametros = { DetalleEvento: { evento: Evento } };

export default function DetalleEventoScreen(): React.ReactElement {
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
      {evento.EliminadoEn ? <Text style={[Estilos.Campo, { color: 'red' }]}>EliminadoEn: {evento.EliminadoEn}</Text> : null}
      <View style={{ height: 8 }} />
      {evento.EliminadoEn ? (
  <Button title="Recuperar" onPress={async () => { try { await RecuperarEvento(evento.Id, evento.PropietarioId); showSuccess('Evento recuperado'); navigation.goBack(); } catch (e: any) { showRetry(e?.message ?? 'No se pudo recuperar', async () => { try { await RecuperarEvento(evento.Id, evento.PropietarioId); showSuccess('Evento recuperado'); navigation.goBack(); } catch (ee: any) { showError(ee?.message ?? 'No se pudo recuperar'); } }); } }} />
      ) : (
        <>
          <Text style={Estilos.Subtitulo}>Participantes</Text>
      {/* TODO: Reemplazar mock por datos reales desde API /eventos/{id}/participantes */}
      <View style={Estilos.ParticipanteItem}><Text>Dueno: usuario@ejemplo.com</Text></View>
      <View style={Estilos.ParticipanteItem}><Text>Colaborador: colab@equipo.com</Text></View>
      <View style={{ height: 8 }} />
      <Button title="AgregarParticipante" onPress={() => {/* placeholder */}} />
      <View style={{ height: 12 }} />
      <Button title="Editar" onPress={() => navigation.navigate('CrearEditarEvento', { evento })} />
        </>
      )}
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 20, fontWeight: '700', marginBottom: 12 },
  Campo: { fontSize: 16, marginBottom: 6 },
  Subtitulo: { fontSize: 16, fontWeight: '600', marginBottom: 6 },
  ParticipanteItem: { padding: 8, borderRadius: 8, backgroundColor: '#f2f2f2', marginBottom: 6 }
});
