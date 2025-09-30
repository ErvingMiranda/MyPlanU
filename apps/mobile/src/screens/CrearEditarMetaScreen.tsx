import React, { useMemo, useState } from 'react';
import { View, Text, TextInput, StyleSheet, Button, Alert, Pressable } from 'react-native';
import { showError, showSuccess } from '../ui/toast';
import { logEvent } from '../telemetry';
import { createGoal, updateGoal, GOAL_TYPES, normalizeGoalType, type GoalType } from '../services/goals';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { useQueryClient } from '@tanstack/react-query';
import { getSessionUserId } from '../auth/session';

type Parametros = { CrearEditarMeta: { meta?: { Id: number; Titulo: string; TipoMeta: string; Descripcion?: string | null } } };

export default function CrearEditarMetaScreen(): React.ReactElement {
  const navigation = useNavigation<any>();
  const ruta = useRoute<RouteProp<Parametros, 'CrearEditarMeta'>>();
  const meta = ruta.params?.meta;
  const cliente = useQueryClient();
  const [Titulo, EstablecerTitulo] = useState('');
  const [TipoMeta, EstablecerTipoMeta] = useState<GoalType>(normalizeGoalType());
  const [Descripcion, EstablecerDescripcion] = useState('');
  const [Guardando, SetGuardando] = useState(false);
  const [UsuarioId, SetUsuarioId] = useState<number | null>(null);

  React.useEffect(() => {
    if (meta) {
      EstablecerTitulo(meta.Titulo ?? '');
      EstablecerTipoMeta(normalizeGoalType(meta.TipoMeta));
      EstablecerDescripcion(meta.Descripcion ?? '');
    }
  }, [meta]);

  React.useEffect(() => {
    (async () => {
      const uid = await getSessionUserId();
      SetUsuarioId(uid);
    })();
  }, []);

  const puedeEditar = !meta || (UsuarioId != null && meta.PropietarioId === UsuarioId);

  const tiposMeta = useMemo(() => GOAL_TYPES, []);

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.TituloPantalla}>Crear / Editar Meta</Text>
      <Text>Titulo</Text>
      <TextInput style={Estilos.Input} value={Titulo} onChangeText={EstablecerTitulo} placeholder="Ej. Correr 5km" />
      <Text>Tipo de meta</Text>
      <View style={Estilos.SeleccionTipo}>
        {tiposMeta.map((tipo, indice) => (
          <Pressable
            key={tipo}
            accessibilityRole="button"
            accessibilityState={{ selected: TipoMeta === tipo }}
            onPress={() => EstablecerTipoMeta(tipo)}
            style={[
              Estilos.OpcionTipo,
              indice < tiposMeta.length - 1 && Estilos.OpcionTipoSeparador,
              TipoMeta === tipo && Estilos.OpcionTipoActiva
            ]}
          >
            <Text style={[Estilos.TextoOpcion, TipoMeta === tipo && Estilos.TextoOpcionActiva]}>{tipo}</Text>
          </Pressable>
        ))}
      </View>
      <Text style={Estilos.AyudaTipo}>Selecciona si la meta es Individual o Colectiva.</Text>
      <Text>Descripcion</Text>
      <TextInput style={[Estilos.Input, { height: 80 }]} value={Descripcion} onChangeText={EstablecerDescripcion} multiline />
      <View style={Estilos.Acciones}>
        <Button title={Guardando ? 'Guardando…' : meta ? 'Actualizar' : 'Guardar'} disabled={Guardando || (!puedeEditar && !!meta)} onPress={async () => {
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
                EstablecerTipoMeta(normalizeGoalType(prev.TipoMeta));
                EstablecerDescripcion(prev.Descripcion ?? '');
                logEvent('goal_save_error', { mode: 'update', Id: meta.Id, message: e?.message });
                throw e;
              }
            } else {
              const ownerId = UsuarioId ?? (await getSessionUserId());
              if (!ownerId) {
                throw new Error('No se detectó la sesión activa.');
              }
              await createGoal({ Titulo, TipoMeta, Descripcion, PropietarioId: ownerId });
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
      {meta && !puedeEditar ? (
        <Text style={{ color: '#b00', marginTop: 12 }}>No puedes editar esta meta porque pertenece a otro usuario.</Text>
      ) : null}
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, padding: 16 },
  TituloPantalla: { fontSize: 20, fontWeight: '600', marginBottom: 12 },
  Input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, marginBottom: 12 },
  SeleccionTipo: { flexDirection: 'row', marginVertical: 8 },
  OpcionTipo: { flex: 1, borderWidth: 1, borderColor: '#ccc', borderRadius: 8, paddingVertical: 12, alignItems: 'center', marginBottom: 4 },
  OpcionTipoSeparador: { marginRight: 12 },
  OpcionTipoActiva: { borderColor: '#007AFF', backgroundColor: '#E5F1FF' },
  TextoOpcion: { fontSize: 16, color: '#333' },
  TextoOpcionActiva: { color: '#0057B7', fontWeight: '600' },
  AyudaTipo: { fontSize: 12, color: '#666', marginBottom: 12 },
  Acciones: { flexDirection: 'row', justifyContent: 'space-between' }
});
