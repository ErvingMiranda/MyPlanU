import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, Button, Alert } from 'react-native';
import { showError, showSuccess } from '../ui/toast';
import { logEvent } from '../telemetry';
import { createGoal, updateGoal } from '../services/goals';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { useQueryClient } from '@tanstack/react-query';

type Parametros = { CrearEditarMeta: { meta?: { Id: number; Titulo: string; TipoMeta: string; Descripcion?: string | null } } };

export default function CrearEditarMetaScreen(): React.ReactElement {
  const navigation = useNavigation<any>();
  const ruta = useRoute<RouteProp<Parametros, 'CrearEditarMeta'>>();
  const meta = ruta.params?.meta;
  const cliente = useQueryClient();
  const [Titulo, EstablecerTitulo] = useState('');
  const [TipoMeta, EstablecerTipoMeta] = useState('SALUD');
  const [Descripcion, EstablecerDescripcion] = useState('');
  const [Guardando, SetGuardando] = useState(false);

  React.useEffect(() => {
    if (meta) {
      EstablecerTitulo(meta.Titulo ?? '');
      EstablecerTipoMeta(meta.TipoMeta ?? '');
      EstablecerDescripcion(meta.Descripcion ?? '');
    }
  }, [meta]);

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
        <Button title={Guardando ? 'Guardando…' : meta ? 'Actualizar' : 'Guardar'} disabled={Guardando} onPress={async () => {
          try {
            if (!Titulo.trim()) { Alert.alert('Validación', 'El título es requerido'); return; }
            SetGuardando(true);
            if (meta) {
              const prev = { ...meta };
              try {
                await updateGoal(meta.Id, { Titulo, TipoMeta, Descripcion });
                showSuccess('Meta actualizada');
                logEvent('goal_save_success', { mode: 'update', Id: meta.Id });
              } catch (e: any) {
                // rollback UI state
                EstablecerTitulo(prev.Titulo ?? '');
                EstablecerTipoMeta(prev.TipoMeta ?? '');
                EstablecerDescripcion(prev.Descripcion ?? '');
                logEvent('goal_save_error', { mode: 'update', Id: meta.Id, message: e?.message });
                throw e;
              }
            } else {
              await createGoal({ Titulo, TipoMeta, Descripcion, PropietarioId: 1 });
              showSuccess('Meta creada');
              logEvent('goal_save_success', { mode: 'create' });
            }
            await cliente.invalidateQueries({ queryKey: ['metas'] });
            navigation.goBack();
          } catch (e: any) {
            showError(e?.message ?? 'No se pudo guardar la meta');
            logEvent('goal_save_error', { mode: meta ? 'update' : 'create', message: e?.message });
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
