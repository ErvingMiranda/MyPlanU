import React from 'react';
import { View, Text, Button, StyleSheet, TextInput } from 'react-native';
import { http } from '../api/http';
import { setAuthToken } from '../api/http';
import { showError, showSuccess } from '../ui/toast';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<any, any>;

export default function LoginRegistroScreen({ navigation }: Props): React.ReactElement {
  const [Correo, SetCorreo] = React.useState('demo@example.com');
  const [Nombre, SetNombre] = React.useState('Demo');
  const [Contrasena, SetContrasena] = React.useState('demo123');
  const [Modo, SetModo] = React.useState<'login'|'registro'>('registro');
  const [Loading, SetLoading] = React.useState(false);

  async function hacerAuth() {
    try {
      SetLoading(true);
      if (Modo === 'registro') {
        const r = await http.post('/auth/registro', { Correo, Nombre, Contrasena });
        const token = r.data.access_token;
        await setAuthToken(token);
        showSuccess('Registrado');
      } else {
        const r = await http.post('/auth/login', { Correo, Contrasena });
        const token = r.data.access_token;
        await setAuthToken(token);
        showSuccess('Sesión iniciada');
      }
      navigation.replace('HomeTabs');
    } catch (e: any) {
      showError(e?.response?.data?.detail || 'Error auth');
    } finally {
      SetLoading(false);
    }
  }

  return (
    <View style={Estilos.Contenedor}>
      <Text style={Estilos.Titulo}>MyPlanU</Text>
      <TextInput style={Estilos.Input} autoCapitalize='none' placeholder='Correo' value={Correo} onChangeText={SetCorreo} />
      {Modo === 'registro' && (
        <TextInput style={Estilos.Input} placeholder='Nombre' value={Nombre} onChangeText={SetNombre} />
      )}
      <TextInput style={Estilos.Input} secureTextEntry placeholder='Contraseña' value={Contrasena} onChangeText={SetContrasena} />
      <Button title={Loading ? 'Enviando...' : (Modo === 'registro' ? 'Registrarse' : 'Iniciar Sesión')} onPress={hacerAuth} disabled={Loading} />
      <View style={{ height: 12 }} />
      <Button title={Modo === 'registro' ? 'Ya tengo cuenta' : 'Crear nueva cuenta'} onPress={() => SetModo(M => M === 'registro' ? 'login' : 'registro')} />
    </View>
  );
}

const Estilos = StyleSheet.create({
  Contenedor: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 },
  Titulo: { fontSize: 22, fontWeight: '600', marginBottom: 16 },
  Input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 8, width: '100%', marginBottom: 12 }
});
