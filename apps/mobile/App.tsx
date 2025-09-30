import React from 'react';
import { Text, View, StyleSheet, Alert } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toast } from './src/ui/toast';
import { http } from './src/api/http';
import { installAxiosInterceptors } from './src/api/errors';
import { processPending } from './src/offline';
import LoginRegistroScreen from './src/screens/LoginRegistroScreen';
import PrincipalScreen from './src/screens/PrincipalScreen';
import DetalleMetaScreen from './src/screens/DetalleMetaScreen';
import CrearEditarMetaScreen from './src/screens/CrearEditarMetaScreen';
import NotificacionesScreen from './src/screens/NotificacionesScreen';
import ConfiguracionScreen from './src/screens/ConfiguracionScreen';
import ListaEventosScreen from './src/screens/ListaEventosScreen';
import DetalleEventoScreen from './src/screens/DetalleEventoScreen';
import CrearEditarEventoScreen from './src/screens/CrearEditarEventoScreen';
import PapeleraScreen from './src/screens/PapeleraScreen';

const Cliente = new QueryClient();

const Stack = createNativeStackNavigator();
const Tabs = createBottomTabNavigator();

function TabsPrincipales(): React.ReactElement {
  return (
    <Tabs.Navigator>
      <Tabs.Screen name="Principal" component={PrincipalScreen} />
      <Tabs.Screen name="Notificaciones" component={NotificacionesScreen} />
      <Tabs.Screen name="Configuracion" component={ConfiguracionScreen} />
      <Tabs.Screen name="Papelera" component={PapeleraScreen} />
    </Tabs.Navigator>
  );
}

import { hasAuthToken, getSessionUserId } from './src/auth/session';
import { ObtenerNotificacionesSistema, MarcarNotificacionLeida } from './src/api/ClienteApi';

export default function AplicacionMovil(): React.ReactElement {
  const [checking, setChecking] = React.useState(true);
  const [authed, setAuthed] = React.useState(false);
  // install interceptors once
  React.useEffect(() => {
    installAxiosInterceptors(http);
    // try to process pending offline queue on startup
    processPending(http).catch(() => {});
    (async () => {
      const tokenExists = await hasAuthToken();
      setAuthed(tokenExists);
      setChecking(false);
    })();
  }, []);

  React.useEffect(() => {
    let cancelado = false;
    let intervalo: ReturnType<typeof setInterval> | undefined;
    const revisar = async () => {
      if (!authed || cancelado) return;
      try {
        const userId = await getSessionUserId();
        if (!userId) return;
        const notificaciones = await ObtenerNotificacionesSistema();
        for (const notif of notificaciones) {
          if (cancelado) break;
          Alert.alert('Notificacion', notif.Mensaje);
          await MarcarNotificacionLeida(notif.Id);
        }
      } catch (e: any) {
        if (__DEV__) {
          // eslint-disable-next-line no-console
          console.warn('No se pudieron obtener notificaciones', e?.message ?? e);
        }
      }
    };
    if (authed) {
      revisar();
      intervalo = setInterval(revisar, 15000);
    }
    return () => {
      cancelado = true;
      if (intervalo) clearInterval(intervalo);
    };
  }, [authed]);
  return (
    <QueryClientProvider client={Cliente}>
      <NavigationContainer
        onStateChange={async () => {
          const tokenExists = await hasAuthToken();
          setAuthed(tokenExists);
        }}
      >
        {checking ? null : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {!authed && (
            <Stack.Screen name="LoginRegistro" component={LoginRegistroScreen} />
          )}
          {authed && (
            <Stack.Screen name="HomeTabs" component={TabsPrincipales} />
          )}
          <Stack.Screen name="DetalleMeta" component={DetalleMetaScreen} options={{ title: 'Detalle de Meta' }} />
          <Stack.Screen name="CrearEditarMeta" component={CrearEditarMetaScreen} options={{ title: 'Crear/Editar Meta' }} />
          <Stack.Screen name="ListaEventos" component={ListaEventosScreen} options={{ title: 'Eventos' }} />
          <Stack.Screen name="DetalleEvento" component={DetalleEventoScreen} options={{ title: 'Detalle de Evento' }} />
          <Stack.Screen name="CrearEditarEvento" component={CrearEditarEventoScreen} options={{ title: 'Crear/Editar Evento' }} />
        </Stack.Navigator>
        )}
      </NavigationContainer>
      <Toast />
    </QueryClientProvider>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  Titulo: { fontSize: 24, fontWeight: '600' }
});
