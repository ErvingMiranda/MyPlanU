import React from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginRegistroScreen from './src/screens/LoginRegistroScreen';
import PrincipalScreen from './src/screens/PrincipalScreen';
import DetalleMetaScreen from './src/screens/DetalleMetaScreen';
import CrearEditarMetaScreen from './src/screens/CrearEditarMetaScreen';
import NotificacionesScreen from './src/screens/NotificacionesScreen';
import ConfiguracionScreen from './src/screens/ConfiguracionScreen';
import ListaEventosScreen from './src/screens/ListaEventosScreen';
import DetalleEventoScreen from './src/screens/DetalleEventoScreen';
import CrearEditarEventoScreen from './src/screens/CrearEditarEventoScreen';

const Cliente = new QueryClient();

const Stack = createNativeStackNavigator();
const Tabs = createBottomTabNavigator();

function TabsPrincipales(): JSX.Element {
  return (
    <Tabs.Navigator>
      <Tabs.Screen name="Principal" component={PrincipalScreen} />
      <Tabs.Screen name="Notificaciones" component={NotificacionesScreen} />
      <Tabs.Screen name="Configuracion" component={ConfiguracionScreen} />
    </Tabs.Navigator>
  );
}

export default function AplicacionMovil(): JSX.Element {
  return (
    <QueryClientProvider client={Cliente}>
      <NavigationContainer>
        <Stack.Navigator>
          <Stack.Screen name="LoginRegistro" component={LoginRegistroScreen} options={{ title: 'Login/Registro' }} />
          <Stack.Screen name="Principal" component={TabsPrincipales} options={{ headerShown: false }} />
          <Stack.Screen name="DetalleMeta" component={DetalleMetaScreen} options={{ title: 'Detalle de Meta' }} />
          <Stack.Screen name="CrearEditarMeta" component={CrearEditarMetaScreen} options={{ title: 'Crear/Editar Meta' }} />
          <Stack.Screen name="ListaEventos" component={ListaEventosScreen} options={{ title: 'Eventos' }} />
          <Stack.Screen name="DetalleEvento" component={DetalleEventoScreen} options={{ title: 'Detalle de Evento' }} />
          <Stack.Screen name="CrearEditarEvento" component={CrearEditarEventoScreen} options={{ title: 'Crear/Editar Evento' }} />
        </Stack.Navigator>
      </NavigationContainer>
    </QueryClientProvider>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  Titulo: { fontSize: 24, fontWeight: '600' }
});
