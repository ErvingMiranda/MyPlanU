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

import { AuthProvider } from './src/auth/AuthContext';
import { getSessionUserId } from './src/auth/session';
import { ObtenerNotificacionesSistema, MarcarNotificacionLeida } from './src/api/ClienteApi';

function AppWithNavigation(): React.ReactElement {
  const { isLoggedIn, isLoading } = useAuth();

  React.useEffect(() => {
    let cancelado = false;
    let intervalo: ReturnType<typeof setInterval> | undefined;
    const revisar = async () => {
      if (!isLoggedIn || cancelado) return;
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
    if (isLoggedIn) {
      revisar();
      intervalo = setInterval(revisar, 15000);
    }
    return () => {
      cancelado = true;
      if (intervalo) clearInterval(intervalo);
    };
  }, [isLoggedIn]);

  if (isLoading) {
    return null; // or a loading spinner
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isLoggedIn ? (
          <Stack.Screen name="LoginRegistro" component={LoginRegistroScreen} />
        ) : (
          <>
            <Stack.Screen name="HomeTabs" component={TabsPrincipales} />
            <Stack.Screen name="DetalleMeta" component={DetalleMetaScreen} options={{ title: 'Detalle de Meta' }} />
            <Stack.Screen name="CrearEditarMeta" component={CrearEditarMetaScreen} options={{ title: 'Crear/Editar Meta' }} />
            <Stack.Screen name="ListaEventos" component={ListaEventosScreen} options={{ title: 'Eventos' }} />
            <Stack.Screen name="DetalleEvento" component={DetalleEventoScreen} options={{ title: 'Detalle de Evento' }} />
            <Stack.Screen name="CrearEditarEvento" component={CrearEditarEventoScreen} options={{ title: 'Crear/Editar Evento' }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function AplicacionMovil(): React.ReactElement {
  React.useEffect(() => {
    installAxiosInterceptors(http);
    processPending(http).catch(() => {});
  }, []);

  return (
    <QueryClientProvider client={Cliente}>
      <AuthProvider>
        <AppWithNavigation />
      </AuthProvider>
      <Toast />
    </QueryClientProvider>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  Titulo: { fontSize: 24, fontWeight: '600' }
});
