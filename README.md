# MyPlanU v0.19.0 (en desarrollo)

MyPlanU es una agenda inteligente y colaborativa para estudiantes y equipos. Este repositorio es un monorepo que contiene:

-   **Backend**: API RESTful construida con FastAPI y SQLModel.
-   **App Móvil**: Aplicación para iOS y Android desarrollada con Expo (React Native) y TypeScript.

El proyecto sigue convenciones de código en español y una arquitectura MSV (Models-Services-Views).

## Estructura del Repositorio

```
/
├── apps/
│   ├── api/      # Backend en FastAPI
│   └── mobile/   # App móvil en Expo
├── packages/
│   └── shared-types/ # Tipos compartidos (placeholder)
└── docs/
    └── ...         # Documentación adicional
```

## Requisitos Previos

-   Python 3.11+
-   Node.js 18+
-   [Expo CLI](https://docs.expo.dev/get-started/installation/)

## Instrucciones de Inicio

Sigue estos pasos para levantar el entorno de desarrollo local.

### 1. Backend (API)

Ejecuta los siguientes comandos desde la raíz del proyecto:

```bash
# 1. Navega al directorio de la API
cd apps/api

# 2. Crea y activa un entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Inicia el servidor
uvicorn app.main:Aplicacion --reload --host 0.0.0.0 --port 8000
```

Para verificar que el backend funciona, abre tu navegador o usa `curl` en la siguiente URL:
`http://127.0.0.1:8000/health`

### 2. App Móvil (Expo)

En una nueva terminal, ejecuta los siguientes comandos desde la raíz del proyecto:

```bash
# 1. Navega al directorio de la app móvil
cd apps/mobile

# 2. Instala las dependencias
npm install

# 3. Inicia el servidor de desarrollo de Expo
npm start
```

Esto abrirá el panel de Metro Bundler, donde podrás escanear el código QR con la app de Expo Go en tu dispositivo móvil o ejecutar la app en un simulador.

> **Nota importante:** Para que la app móvil pueda comunicarse con tu backend local, asegúrate de que la variable de entorno `EXPO_PUBLIC_API_URL` esté configurada correctamente o ajústala en la pantalla de "Configuración" de la app. Por ejemplo: `export EXPO_PUBLIC_API_URL="http://<TU_IP_LOCAL>:8000"`.

<details>
<summary>📚 Historial de Versiones (Changelog)</summary>

### v0.19.0 (Experiencia móvil y sincronización)
- Endpoints complementarios para la cola offline en backend.
- Integración de Expo Notifications y sincronización offline ↔ online.
- Garantizar conectividad desde dispositivos físicos y mejoras de formato/código.
- Documentación de flujos offline y limpieza general.

### v0.18.0 (Auditoría y notificaciones)
- **Backend**:
  - Se añade la tabla `BitacoraRecuperacion` y se registran automáticamente todas las recuperaciones.
  - El borrado de eventos crea notificaciones para dueño y participantes.
  - Nuevos endpoints `/bitacora/recuperaciones` y `/notificaciones/sistema`.
- **Móvil**:
  - `DetalleEventoScreen` consume participantes reales desde la API.
  - La app consulta periódicamente las notificaciones del backend.
- **Documentación**:
  - Se publica la guía `docs/monitoring_auditoria.md`.

### v0.17.0 (Permisos y cascadas básicas)
- **Backend**:
  - Servicios validan permisos según el rol del solicitante (403/409).
  - Borrado de Metas aplica cascada lógica a Eventos y Recordatorios.
  - Metas "Colectiva" solo se pueden cerrar si tienen al menos un colaborador.
- **Móvil**:
  - Cliente guarda `userId` desde el JWT para enviar `PropietarioId` correcto.
  - Pantallas muestran errores de permisos con toasts.

### v0.16.1 (Ajustes post-autenticación)
- **Backend**:
  - Helper `ObtenerEngine()` para reutilizar el engine de SQLModel en pruebas.
  - Pruebas de API usan helper de autenticación para crear usuario y token.
- **Móvil**:
  - `fetchJson()` incluye automáticamente el header `Authorization`.
  - Selector de tipo de meta ("Individual" / "Colectiva") en lugar de campo libre.

### v0.16.0 (Autenticación JWT básica)
- **Backend**:
  - Nuevos endpoints `/auth/registro` y `/auth/login`.
  - Contraseñas hasheadas con `bcrypt`.
  - Endpoints principales protegidos con `get_current_user`.
- **Móvil**:
  - Pantalla `LoginRegistroScreen` con modos para registro y login.
  - Token JWT persistido en AsyncStorage y añadido a las peticiones con un interceptor de Axios.
  - Navegación condicionada al estado de autenticación.

### v0.15.1 (Hardening repetición y pruebas)
- **Backend**:
  - `DiasSemana` ahora se expone como lista en todas las respuestas.
  - Validación de `IntervaloRepeticion` movida a Services para emitir errores 400.
- **Móvil**:
  - Pruebas Jest para la cola offline.
  - Cliente actualizado para consumir `DiasSemana` como lista.

### v0.15.0 (JSON bodies y contratos unificados)
- **Backend**:
  - Endpoints POST/PATCH de metas, eventos y recordatorios migrados a cuerpos JSON.
  - Estandarización de mensajes de error (`MetaInvalida: ...`).
- **Móvil**:
  - Cliente API y servicios `goals` actualizados para enviar datos como JSON.
- **Breaking Changes**:
  - La creación y actualización de recursos ahora requiere un cuerpo JSON en lugar de parámetros de consulta.

### v0.14.1 (Fixes y coherencia)
- **Backend**:
  - Versión de la API alineada al changelog (`0.14.1`).
  - CORS parametrizable mediante `MYPLANU_CORS_ORIGINS`.
  - Corregido endpoint `/papelera/recordatorios`.
- **Móvil**:
  - `PrincipalScreen` ahora usa `services/goals.listGoals()` para coherencia con la funcionalidad offline.

### v0.14.0 (Offline mínimo para metas)
- **Móvil**:
  - Cache local de la lista de metas y cola de operaciones (crear/actualizar) usando AsyncStorage.
  - Botón en "Configuración" para reintentar la sincronización manual.

### v0.13.9 (Telemetría dev)
- **Móvil**:
  - Nuevo módulo `src/telemetry.ts` con buffer en memoria, activado solo en modo desarrollo.
  - Eventos instrumentados: `network_ping`, `prefs_save_*`, `goal_save_*`, etc.

### v0.13.2 (Cliente HTTP y conectividad)
- **Móvil**:
  - Nuevo cliente HTTP en `apps/mobile/src/api/http.ts` (Axios).
  - Pantalla "Configuración" con botón para probar la conexión a la API.
  - Reemplazo de `Alert` por `react-native-toast-message` para notificaciones.

### v0.13.1 (Papelera de eliminados)
- **Backend**:
  - Nuevas rutas de solo lectura para listar elementos con soft delete (`/papelera/metas`, `/papelera/eventos`, etc.).
- **Móvil**:
  - Nueva pantalla "Papelera" con pestañas para ver y recuperar ítems eliminados.

### v0.13 (Soft delete con recuperación)
- **Backend**:
  - Nuevos endpoints para recuperar metas, eventos y recordatorios (`POST /metas/{Id}/recuperar`).
  - Regla: no se puede recuperar un hijo si su padre está eliminado.
- **Móvil**:
  - Botón "Recuperar" en las pantallas de detalle para ítems eliminados.

### v0.12 (Zonas horarias)
- **Backend**:
  - Campo `ZonaHoraria` añadido al modelo `Usuario`.
  - Endpoints aceptan `ZonaHorariaEntrada` para interpretar fechas y las devuelven convertidas a la zona del usuario.
- **Móvil**:
  - Preferencia de zona horaria local, configurable en la app.

### v0.11 (Repetición de eventos)
- **Backend**:
  - Campos de repetición en `Evento` y `Recordatorio` (`FrecuenciaRepeticion`, `IntervaloRepeticion`, `DiasSemana`).
  - Endpoint para proyectar ocurrencias futuras (`GET /eventos/proximos`).

### v0.10 (Participantes en eventos)
- **Backend**:
  - Nuevo modelo `ParticipanteEvento` con roles (`Dueno`, `Colaborador`, `Lector`).
  - Nuevos endpoints para gestionar participantes de un evento.
- **Móvil**:
  - Sección de participantes (mock) en la pantalla de detalle del evento.

### v0.9 (Recordatorios próximos)
- **Backend**:
  - Campo opcional `Mensaje` en `Recordatorio`.
  - Nuevo endpoint `GET /recordatorios/proximos`.
- **Móvil**:
  - Pantalla de notificaciones lista los recordatorios próximos desde la API.

### v0.8 (CRUD de eventos en móvil)
- **Móvil**:
  - Nuevas pantallas: `ListaEventosScreen`, `DetalleEventoScreen`, `CrearEditarEventoScreen`.
  - Navegación y consumo de API para eventos.

### v0.7 (Servicios y permisos base)
- **Backend**:
  - Enum `RolParticipante` (`Dueno`, `Colaborador`, `Lector`).
  - Lógica de permisos base en los servicios.

### v0.6 (Modelos de Evento y Recordatorio)
- **Backend**:
  - Modelos y CRUD para `Evento` y `Recordatorio` con soft delete.
  - Reglas de negocio: `Inicio < Fin`, no crear recordatorios en el pasado.

### v0.5 (Flujos de navegación)
- **Móvil**:
  - Conexión de la navegación entre todas las pantallas principales.

### v0.4 (Base de la app móvil)
- **Móvil**:
  - Estructura inicial con React Navigation y React Query.
  - Pantallas base: `LoginRegistro`, `Principal`, `DetalleMeta`, etc.
  - Cliente de API inicial y configuración de `EXPO_PUBLIC_API_URL`.

### v0.3 (Refactor a capa de Servicios)
- **Backend**:
  - Creación de la capa de `Services` (`UsuariosService`, `MetasService`) para separar la lógica de negocio de las vistas.

### v0.2 (Backend base)
- **Backend**:
  - Modelos `Usuario` y `Meta` con soft delete y timestamps.
  - Rutas en español: `/usuarios`, `/metas`.

### v0.1 (Monorepo inicial)
- Creación del monorepo con `apps/api` (FastAPI) y `apps/mobile` (Expo).
- Endpoint de salud inicial y primera versión del `README.md`.

</details>

