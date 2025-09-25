import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Switch, Button, TextInput } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ActualizarUsuario } from '../api/ClienteApi';
import { EstablecerZonaHoraria, ObtenerZonaHoraria } from '../userPrefs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { http, ping, clearAuthToken } from '../api/http';
import { showError, showSuccess, showInfo, showRetry } from '../ui/toast';
import { logEvent } from '../telemetry';
import { processPending } from '../offline';

export default function ConfiguracionScreen(): React.ReactElement {
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const [TemaOscuro, EstablecerTemaOscuro] = useState(false);
  const [Notificar, EstablecerNotificar] = useState(false);
  const [UsuarioId, EstablecerUsuarioId] = useState<string>('1');
  const [ZonaHoraria, EstablecerZona] = useState<string>(ObtenerZonaHoraria() ?? 'UTC');
  const [ApiBaseUrl, SetApiBaseUrl] = useState<string>(http.defaults.baseURL || '');
  const [PingEstado, SetPingEstado] = useState<'idle'|'ok'|'fail'|'loading'>('idle');
  const [Syncing, SetSyncing] = useState(false);

  useEffect(() => {
    (async () => {
      const guardada = await AsyncStorage.getItem('APP_API_BASE_URL');
      if (guardada) {
        SetApiBaseUrl(guardada);
        http.defaults.baseURL = guardada;
      }
    })();
  }, []);

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>Configuracion</Text>
      <View style={Estilos.Fila}>
        <Text>Tema Oscuro</Text>
        <Switch value={TemaOscuro} onValueChange={EstablecerTemaOscuro} />
      </View>
      <View style={{ marginBottom: 12 }}>
        <Button title={Syncing ? 'Sincronizando…' : 'Reintentar sync offline'} disabled={Syncing} onPress={async () => {
          try {
            SetSyncing(true);
            const { ok, fail } = await processPending(http);
            logEvent('offline_sync_attempt', { ok, fail });
            if (ok === 0 && fail === 0) {
              showInfo('Sin operaciones pendientes');
            } else if (fail === 0) {
              showSuccess(`Sincronizado ${ok}/${ok}`);
            } else {
              showRetry(`Sync parcial: ok ${ok}, fallas ${fail}`, () => {
                // retry same action
                (async () => {
                  SetSyncing(true);
                  try {
                    const r = await processPending(http);
                    logEvent('offline_sync_retry', { ok: r.ok, fail: r.fail });
                    if (r.fail === 0) {
                      showSuccess(`Sincronizado ${r.ok}/${r.ok}`);
                    } else {
                      showError(`Aún pendientes: ${r.fail}`);
                    }
                  } finally {
                    SetSyncing(false);
                  }
                })();
              });
            }
          } catch (e: any) {
            logEvent('offline_sync_error', { message: e?.message });
            showRetry('Error al sincronizar', () => {
              // trigger again
              (async () => {
                SetSyncing(true);
                try {
                  const r = await processPending(http);
                  logEvent('offline_sync_retry', { ok: r.ok, fail: r.fail });
                  if (r.fail === 0) {
                    showSuccess(`Sincronizado ${r.ok}/${r.ok}`);
                  } else {
                    showError(`Aún pendientes: ${r.fail}`);
                  }
                } finally {
                  SetSyncing(false);
                }
              })();
            });
          } finally {
            SetSyncing(false);
          }
        }} />
      </View>
      <View style={Estilos.Fila}>
        <Text>Notificaciones</Text>
        <Switch value={Notificar} onValueChange={EstablecerNotificar} />
      </View>
      <Text>UsuarioId</Text>
      <TextInput style={Estilos.Input} keyboardType="numeric" value={UsuarioId} onChangeText={EstablecerUsuarioId} placeholder="Id de usuario" />
      <Text>Zona Horaria (IANA, ej: America/Mexico_City)</Text>
      <TextInput style={Estilos.Input} value={ZonaHoraria} onChangeText={EstablecerZona} placeholder="Ej: UTC o America/Bogota" />
      <Text style={{ marginTop: 8 }}>API_BASE_URL (solo dev)</Text>
      <TextInput style={Estilos.Input} value={ApiBaseUrl} onChangeText={SetApiBaseUrl} placeholder="http://127.0.0.1:8000" autoCapitalize="none" autoCorrect={false} />
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
        <Button title={PingEstado === 'loading' ? 'Probando…' : 'Probar conexión'} onPress={async () => {
          try {
            SetPingEstado('loading');
            const res = await ping();
            SetPingEstado(res.ok ? 'ok' : 'fail');
            logEvent('network_ping', { ok: res.ok, url: res.url });
            if (res.ok) showInfo(`Conectado: ${res.url}`); else showError(`Sin conexión: ${res.url}`);
          } catch {
            SetPingEstado('fail');
            logEvent('network_ping', { ok: false, url: http.defaults.baseURL });
            showRetry('Sin conexión. Revisa la URL o tu red.', async () => {
              try {
                SetPingEstado('loading');
                const res2 = await ping();
                SetPingEstado(res2.ok ? 'ok' : 'fail');
                logEvent('network_ping', { ok: res2.ok, url: res2.url, retry: true });
                if (res2.ok) showInfo(`Conectado: ${res2.url}`); else showError(`Sin conexión: ${res2.url}`);
              } catch {
                SetPingEstado('fail');
                logEvent('network_ping', { ok: false, url: http.defaults.baseURL, retry: true });
                showError('Sigue sin conexión.');
              }
            });
          }
        }} />
        <Text style={{ marginLeft: 12 }}>{PingEstado === 'ok' ? '✅ OK' : PingEstado === 'fail' ? '❌ ERROR' : ''}</Text>
      </View>
      <View style={Estilos.Acciones}>
        <Button title="Guardar" onPress={async () => {
          try {
            EstablecerZonaHoraria(ZonaHoraria);
            const id = parseInt(UsuarioId, 10);
            if (id) await ActualizarUsuario(id, { ZonaHoraria });
            if (ApiBaseUrl) {
              await AsyncStorage.setItem('APP_API_BASE_URL', ApiBaseUrl);
              http.defaults.baseURL = ApiBaseUrl;
            }
            showSuccess('Preferencias guardadas');
            logEvent('prefs_save_success', { ZonaHoraria, ApiBaseUrl });
            navigation.navigate('HomeTabs');
          } catch (e: any) {
            showError(e?.message ?? 'No se pudo guardar');
            logEvent('prefs_save_error', { message: e?.message });
          }
        }} />
  <Button title="Cancelar" onPress={() => navigation.navigate('HomeTabs')} />
      </View>
      <View style={{ marginTop: 24 }}>
        <Button title="Cerrar Sesión" color="#b00" onPress={async () => {
          await clearAuthToken();
          navigation.reset({ index: 0, routes: [{ name: 'LoginRegistro' }] });
        }} />
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
