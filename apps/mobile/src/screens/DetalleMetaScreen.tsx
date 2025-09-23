import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';
import { showSuccess, showError, showRetry } from '../ui/toast';
import { logEvent } from '../telemetry';
import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Meta, RecuperarMeta } from '../api/ClienteApi';

type Parametros = { DetalleMeta: { meta: Meta } };

export default function DetalleMetaScreen(): React.ReactElement {
  const ruta = useRoute<RouteProp<Parametros, 'DetalleMeta'>>();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const meta = ruta.params?.meta;

  if (!meta) {
    return (
      <View style={Estilos.Contenedor}> 
        <Text>No se encontró la meta.</Text>
      </View>
    );
  }

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>{meta.Titulo}</Text>
      {meta.Descripcion ? <Text style={Estilos.Campo}>Descripcion: {meta.Descripcion}</Text> : null}
      <Text style={Estilos.Campo}>Tipo: {meta.TipoMeta}</Text>
      <Text style={Estilos.Campo}>PropietarioId: {meta.PropietarioId}</Text>
      {meta.CreadoEn ? <Text style={Estilos.Campo}>CreadoEn: {meta.CreadoEn}</Text> : null}
      {meta.ActualizadoEn ? <Text style={Estilos.Campo}>ActualizadoEn: {meta.ActualizadoEn}</Text> : null}
      {meta.EliminadoEn ? <Text style={[Estilos.Campo, { color: 'red' }]}>EliminadoEn: {meta.EliminadoEn}</Text> : null}
      <View style={{ height: 12 }} />
      {meta.EliminadoEn ? (
  <Button title="Recuperar" onPress={async () => { try { await RecuperarMeta(meta.Id); showSuccess('Meta recuperada'); logEvent('recover_success', { tipo: 'Meta', Id: meta.Id }); navigation.goBack(); } catch (e: any) { logEvent('recover_error', { tipo: 'Meta', Id: meta.Id, message: e?.message }); showRetry(e?.message ?? 'No se pudo recuperar', async () => { try { await RecuperarMeta(meta.Id); showSuccess('Meta recuperada'); logEvent('recover_success', { tipo: 'Meta', Id: meta.Id, retry: true }); navigation.goBack(); } catch (ee: any) { logEvent('recover_error', { tipo: 'Meta', Id: meta.Id, message: ee?.message, retry: true }); showError(ee?.message ?? 'No se pudo recuperar'); } }); } }} />
      ) : (
        <Button title="Editar" onPress={() => navigation.navigate('CrearEditarMeta', { meta })} />
      )}
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  Titulo: { fontSize: 22, fontWeight: '700', marginBottom: 12 },
  Campo: { fontSize: 16, marginBottom: 6 }
});
