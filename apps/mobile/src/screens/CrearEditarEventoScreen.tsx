import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, StyleSheet, Button, Alert } from 'react-native';
import { showError, showSuccess } from '../ui/toast';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Evento, CrearEvento, ActualizarEvento } from '../api/ClienteApi';
import { ObtenerZonaHoraria } from '../userPrefs';
import { getSessionUserId } from '../auth/session';

type Parametros = { CrearEditarEvento: { evento?: Evento } };

export default function CrearEditarEventoScreen(): React.ReactElement {
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const ruta = useRoute<RouteProp<Parametros, 'CrearEditarEvento'>>();
  const EventoInicial = ruta.params?.evento;

  const [Titulo, EstablecerTitulo] = useState(EventoInicial?.Titulo ?? '');
  const [MetaId, EstablecerMetaId] = useState(String(EventoInicial?.MetaId ?? ''));
  const [PropietarioId, EstablecerPropietarioId] = useState(String(EventoInicial?.PropietarioId ?? ''));
  const [UsuarioActualId, SetUsuarioActualId] = useState<number | null>(null);
  const [Inicio, EstablecerInicio] = useState(EventoInicial?.Inicio ?? '');
  const [Fin, EstablecerFin] = useState(EventoInicial?.Fin ?? '');
  const [Descripcion, EstablecerDescripcion] = useState(EventoInicial?.Descripcion ?? '');
  const [Ubicacion, EstablecerUbicacion] = useState(EventoInicial?.Ubicacion ?? '');

  const ValidarFechas = (): boolean => {
    if (!Inicio || !Fin) return true; // no bloquear si faltan para edits parciales
    const ini = new Date(Inicio).getTime();
    const fin = new Date(Fin).getTime();
    return ini < fin;
  };

  useEffect(() => {
    (async () => {
      const uid = await getSessionUserId();
      SetUsuarioActualId(uid);
      if (!EventoInicial && uid != null) {
        EstablecerPropietarioId(String(uid));
      }
    })();
  }, [EventoInicial]);

  const Guardar = async () => {
    if (!ValidarFechas()) {
      Alert.alert('Error', 'Inicio debe ser menor que Fin');
      return;
    }
    try {
      if (EventoInicial) {
        const actualizado = await ActualizarEvento(EventoInicial.Id, {
          Titulo: Titulo || undefined,
          Descripcion: Descripcion,
          Inicio: Inicio || undefined,
          Fin: Fin || undefined,
          Ubicacion: Ubicacion,
          ZonaHorariaEntrada: ObtenerZonaHoraria(),
          UsuarioId: UsuarioActualId ?? EventoInicial.PropietarioId,
        });
  showSuccess(`Evento ${actualizado.Id} actualizado`);
        navigation.goBack();
      } else {
        // Para crear se requieren MetaId y PropietarioId
        const metaId = parseInt(MetaId, 10);
        const propietarioId = parseInt(PropietarioId, 10);
        const sessionId = UsuarioActualId ?? propietarioId;
        if (!metaId || !propietarioId || !Titulo || !Inicio || !Fin) {
          Alert.alert('Faltan datos', 'MetaId, PropietarioId, Titulo, Inicio y Fin son obligatorios');
          return;
        }
        const creado = await CrearEvento({
          MetaId: metaId,
          PropietarioId: sessionId,
          Titulo,
          Descripcion: Descripcion || undefined,
          Inicio,
          Fin,
          Ubicacion: Ubicacion || undefined,
          ZonaHorariaEntrada: ObtenerZonaHoraria(),
          UsuarioId: sessionId,
        } as any);
  showSuccess(`Evento ${creado.Id} creado`);
        navigation.goBack();
      }
    } catch (e: any) { showError(e?.message ?? 'Fallo en API'); }
  };

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.TituloPantalla}>{EventoInicial ? 'Editar Evento' : 'Crear Evento'}</Text>
      {!EventoInicial && (
        <>
          <Text>MetaId</Text>
          <TextInput style={Estilos.Input} keyboardType="numeric" value={MetaId} onChangeText={EstablecerMetaId} placeholder="Ej. 1" />
          <Text>PropietarioId</Text>
          <TextInput style={Estilos.Input} keyboardType="numeric" value={PropietarioId} onChangeText={EstablecerPropietarioId} placeholder="Ej. 1" />
        </>
      )}
      <Text>Titulo</Text>
      <TextInput style={Estilos.Input} value={Titulo} onChangeText={EstablecerTitulo} placeholder="Titulo del evento" />
      <Text>Inicio (ISO)</Text>
      <TextInput style={Estilos.Input} value={Inicio} onChangeText={EstablecerInicio} placeholder="YYYY-MM-DDTHH:mm:ss" />
      <Text>Fin (ISO)</Text>
      <TextInput style={Estilos.Input} value={Fin} onChangeText={EstablecerFin} placeholder="YYYY-MM-DDTHH:mm:ss" />
      <Text>Descripcion</Text>
      <TextInput style={[Estilos.Input, { height: 80 }]} value={Descripcion} onChangeText={EstablecerDescripcion} multiline />
      <Text>Ubicacion</Text>
      <TextInput style={Estilos.Input} value={Ubicacion} onChangeText={EstablecerUbicacion} />
      <View style={Estilos.Acciones}>
        <Button title="Guardar" onPress={Guardar} />
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
