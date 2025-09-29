# MyPlanU
MyPlanU v0.16.1 (en desarrollo)
=================

Descripcion
-----------
MyPlanU es una agenda inteligente y colaborativa para estudiantes y equipos. Este repositorio es un monorepo con backend (FastAPI + SQLModel) y app movil (Expo + TypeScript), con convenciones en español y arquitectura MSV.

Estructura del Monorepo
-----------------------
- apps/
  - api/ (FastAPI + SQLModel + SQLite)
  - mobile/ (Expo React Native + TypeScript)
- packages/
  - shared-types/ (placeholder para tipos compartidos)
- .editorconfig, .gitignore, README.md

Convenciones y Arquitectura (MSV)
---------------------------------
- Nombres de codigo en espanol, sin tildes ni letra eñe (ej.: Correo, PropietarioId, TipoMeta).
- PascalCase para clases, variables, funciones y atributos en backend y movil.
- Arquitectura Models–Services–Views (MSV):
  - Models: definiciones de datos y mapeos (SQLModel en backend, tipos en movil).
  - Services: reglas de negocio y validaciones.
  - Views: endpoints (FastAPI) y pantallas (React Native).

Requisitos
----------
- Python 3.11+
- Node.js 18+
- Expo CLI

Como Ejecutar
-------------
Backend (API)
1) Crear y activar venv, instalar requirements, correr uvicorn y probar `/salud`:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn app.main:Aplicacion --reload --host 0.0.0.0 --port 8000
# Probar salud
curl http://127.0.0.1:8000/salud
```

Movil (Expo)
1) Instalar dependencias y arrancar Expo:

```bash
cd apps/mobile
npm install
npx expo start
```

Nota sobre API_URL
------------------
Si el emulador/dispositivo no accede a localhost, configura la URL del backend en el cliente movil usando la variable de entorno de Expo:

```bash
export EXPO_PUBLIC_API_URL="http://<IP_LOCAL>:8000"
```

Changelog por version
---------------------

v0.1
- Monorepo inicial con apps/api (FastAPI + SQLModel) y apps/mobile (Expo + TS), .editorconfig y .gitignore.
- Endpoint salud y README v0.1.

v0.2
- Backend base en español y PascalCase.
- Modelos Usuario y Meta, soft delete, timestamps y validaciones.
- Rutas en español: /salud, /usuarios, /metas.

v0.3
- Refactor: capa Services separada (UsuariosService, MetasService).
- Manejo de correo duplicado con 409 y mejoras de validacion.
- README v0.3 con TODOs (roles y cascadas).

v0.4
- App movil base: navegacion inicial (Stack + Tabs) y React Query.
- Pantallas: LoginRegistro, Principal (lista metas), DetalleMeta, CrearEditarMeta, Notificaciones, Configuracion.
- Cliente API y configuracion EXPO_PUBLIC_API_URL.

v0.5
- Flujos de navegacion conectados:
  - LoginRegistro → (replace) → Principal.
  - Principal → DetalleMeta (tocar meta).
  - Principal → CrearEditarMeta (boton "+").
  - Principal → Notificaciones y → Configuracion (botones).
  - Notificaciones → DetalleMeta (mock) o volver a Principal.
  - DetalleMeta → CrearEditarMeta (boton "Editar").
  - Configuracion → volver a Principal con "Guardar" o "Cancelar".
  - Principal → LoginRegistro (boton "CerrarSesion").

v0.6
- Backend: modelos y CRUD de Evento y Recordatorio con soft delete.
- Modelos:
  - Evento(Id, MetaId -> Meta, PropietarioId -> Usuario, Titulo, Descripcion=None, Inicio, Fin, Ubicacion=None, CreadoEn, ActualizadoEn=None, EliminadoEn=None)
  - Recordatorio(Id, EventoId -> Evento, FechaHora, Canal in ['Local','Push'], Enviado=False, CreadoEn, EliminadoEn=None)
- Reglas:
  - Inicio < Fin.
  - Meta y Propietario deben existir y no estar eliminados.
  - No crear Recordatorio en el pasado.
  - Al borrar Evento (soft), marcar Recordatorios relacionados como EliminadoEn.
- Rutas REST en español: /eventos, /recordatorios (GET/POST/PATCH/DELETE), y /salud se mantiene igual.

v0.7
- Servicios y permisos base:
  - Enum RolParticipante: ['Dueno','Colaborador','Lector'].
  - Permisos: Dueno = CRUD total; Colaborador = crear/leer/actualizar; Lector = solo lectura.
  - Bloquear eliminar si rol != Dueno.
  - Reglas vigentes: Inicio < Fin; Recordatorio no en pasado; existencia de Meta/Propietario/Evento.

v0.8
- App movil: lista y detalle de eventos; crear/editar.
- Pantallas nuevas: ListaEventosScreen, DetalleEventoScreen, CrearEditarEventoScreen.
- Navegacion: desde PrincipalScreen → "VerEventos" abre ListaEventosScreen.
- Interaccion:
  - Lista toca item → DetalleEventoScreen (muestra Titulo, Inicio, Fin, etc.).
  - Boton "Editar" → CrearEditarEventoScreen con datos pre-cargados.
  - Validacion UI simple: Inicio < Fin.
- API consumida: GET /eventos; POST/PATCH /eventos para crear/editar (sin permisos reales aun).

v0.9
- Backend:
  - Recordatorio ahora tiene campo opcional Mensaje.
  - Nuevo endpoint: GET /recordatorios/proximos?dias=7 para listar recordatorios futuros (por defecto 7 dias).
- Movil:
  - NotificacionesScreen ahora lista recordatorios proximos desde la API y muestra un contador de "tiempo restante" (min/horas).
  - Formulario rapido para crear un Recordatorio (EventoId, FechaHora en ISO, Mensaje opcional) y refrescar la lista.
- Nota TODO: Integrar Expo Notifications (notificaciones locales) en la siguiente version.

v0.10
- Backend:
  - Nuevo modelo ParticipanteEvento(Id, EventoId -> Evento, UsuarioId -> Usuario, Rol in ['Dueno','Colaborador','Lector'], CreadoEn).
  - Reglas: un Evento debe tener exactamente un Dueno; Colaborador/Lector opcionales. Si Meta es 'Colectiva', TODO validar al cerrar que exista al menos un Colaborador.
  - Servicio ParticipantesService: AgregarParticipante, CambiarRol, QuitarParticipante (no permite quitar Dueno si no hay transferencia).
  - Rutas:
    - GET /eventos/{Id}/participantes
    - POST /eventos/{Id}/participantes (agrega participante con rol)
    - PATCH /participantes/{Id} (cambiar rol)
    - DELETE /participantes/{Id}
  - EventosService: al eliminar evento, se dejo TODO para notificar a participantes.
- Movil:
  - DetalleEventoScreen muestra seccion de Participantes (mock temporal) y boton "AgregarParticipante" (placeholder sin logica).

v0.11
- Backend:
  - Repeticion en Evento y Recordatorio: campos FrecuenciaRepeticion ('Diaria','Semanal','Mensual'), IntervaloRepeticion (int), DiasSemana (CSV, ej. "Lun,Mie").
  - Proyeccion de ocurrencias sin persistir: GET /eventos/proximos?Desde=...&Hasta=... devuelve ocurrencias (Titulo, Inicio, Fin, EventoId).
  - Recordatorio acepta tambien repeticion y puede calcular proximas fechas (no se crean en pasado; solo proximas).
- Criterios rapidos:
  - Crear Evento semanal con DiasSemana=['Lun','Mie'] y consultar /eventos/proximos devuelve ocurrencias en esos dias dentro del rango.
  - Recordatorio con repeticion calcula proximas fechas dentro del rango futuro.

v0.12
- Backend (zonas horarias por usuario):
  - Usuario ahora tiene campo ZonaHoraria (IANA, ej. "America/Mexico_City"), por defecto 'UTC'.
  - Los endpoints de eventos y recordatorios aceptan parametros opcionales para manejar zonas horarias:
    - ZonaHorariaEntrada: al crear/editar (o al consultar rangos) si las fechas son "naive", se interpretan en esta zona y se almacenan en UTC.
    - UsuarioId y/o ZonaHoraria: para respuestas, las fechas se devuelven en ISO8601 con offset convertido a la zona del usuario (si no se provee, se usa UTC).
  - Endpoints actualizados: GET/POST/PATCH /eventos, GET /eventos/{Id}, GET /eventos/proximos, GET/POST/PATCH /recordatorios, GET /recordatorios/{Id}, GET /recordatorios/proximos.
- Movil:
  - Nueva preferencia local de zona horaria (detecta la del dispositivo por defecto) y pantalla Configuracion permite establecerla y persistirla en el backend (PATCH /usuarios/{Id}).
  - Cliente API envia automaticamente ZonaHoraria/ZonaHorariaEntrada y UsuarioId al consultar/crear/editar, y muestra fechas ya ajustadas por el backend.
- Criterios rapidos:
  - Al cambiar la zona horaria en Configuracion y refrescar Lista/Detalle de eventos, las horas se muestran con el offset correcto de la zona.
  - Los recordatorios proximos muestran su FechaHora con el offset de la zona del usuario y el contador "tiempo restante" coincide.

v0.13
- Soft delete con recuperacion (undo):
  - Nuevos servicios y endpoints para recuperar Meta, Evento y Recordatorio:
    - POST /metas/{Id}/recuperar
    - POST /eventos/{Id}/recuperar
    - POST /recordatorios/{Id}/recuperar
  - Reglas: no se puede recuperar un hijo si su padre esta eliminado (primero recuperar la Meta, luego el Evento, luego el Recordatorio).
  - Bitacora: TODO registrar quien recupera y cuando.
- Movil:
  - En DetalleMeta y DetalleEvento, si el recurso esta eliminado se muestra boton "Recuperar" (placeholder de flujo admin/lista de eliminados).
- Criterios rapidos:
  - Eliminar una Meta y sus Eventos (soft), luego recuperar primero la Meta y despues los Eventos.
  - Intentar recuperar Evento con Meta eliminada debe fallar con mensaje claro.

v0.13.1
- Backend (papelera de eliminados):
  - Nuevas rutas de solo lectura para listar elementos con soft delete:
    - GET /papelera/metas?PropietarioId=&Desde=&Hasta=&UsuarioId=&ZonaHoraria=&ZonaHorariaEntrada=
    - GET /papelera/eventos?PropietarioId=&MetaId=&Desde=&Hasta=&UsuarioId=&ZonaHoraria=&ZonaHorariaEntrada=
    - GET /papelera/recordatorios?EventoId=&Desde=&Hasta=&UsuarioId=&ZonaHoraria=&ZonaHorariaEntrada=
  - Todas regresan fechas en ISO8601 ajustadas a la zona indicada (o la del UsuarioId) igual que el resto de endpoints.
- Movil:
  - Nueva pantalla "Papelera" con pestañas Metas/Eventos/Recordatorios. Permite ver EliminadoEn y recuperar cada item.
  - Manejo de errores al recuperar (muestra mensaje del backend cuando aplica, ej. dependencias no recuperadas).
- Ejemplos rapidos (cURL):
  - Metas eliminadas en la ultima semana, vistas en zona de Mexico City:
    curl "http://localhost:8000/papelera/metas?Desde=$(date -Iseconds -u --date='-7 days')&ZonaHoraria=America/Mexico_City"
  - Eventos eliminados de una meta especifica:
    curl "http://localhost:8000/papelera/eventos?MetaId=123"
  - Recordatorios eliminados de un evento, interpretando el filtro de fecha de entrada en zona local:
    curl "http://localhost:8000/papelera/recordatorios?EventoId=45&Desde=2025-01-01T00:00:00&ZonaHorariaEntrada=America/Bogota&ZonaHoraria=America/Bogota"

v0.13.2
- Base URL y healthcheck:
  - Backend ahora expone tambien /health (alias de /salud) para checks de infraestructura.
  - Movil: nuevo cliente HTTP en `apps/mobile/src/api/http.ts` (Axios) que lee API_BASE_URL y EXPO_PUBLIC_API_URL.
  - Agrega `apps/mobile/.env.example` con API_BASE_URL. En simulador usa 127.0.0.1; en dispositivo fisico, usa la IP LAN de tu maquina (ej. http://192.168.1.10:8000).
  - Funcion `ping()` consulta /health y cae a /salud. Reemplazar mensajes genericos de red por un toast con sugerencia de revisar URL o conectividad.

v0.13.6
- Pantalla Configuracion con conectividad:
  - Nuevo botón “Probar conexión” que llama ping() y muestra estado.
  - Campo editable de API_BASE_URL (solo dev) que se persiste en almacenamiento y actualiza baseURL de Axios en caliente.

v0.13.7
- Manejo de errores unificado y toasts:
  - Cliente Axios ahora instala interceptores (solo log en dev) y se centraliza el mapeo de errores en `src/api/errors.ts`.
  - Reemplazo de Alerts por toasts en pantallas de Configuración y Crear/Editar Meta para feedback no intrusivo.
  - Nuevos helpers `showSuccess/showError/showInfo` y provider global `<Toast />` integrados.

Pruebas (app móvil)
-------------------
- Stack: Jest + jest-expo.
- Ejecutar pruebas en `apps/mobile`:

```bash
cd apps/mobile
npm test
```

- Cobertura básica incluida:
  - Servicios de metas (Axios) con escenarios de éxito, 404 y timeout (axios-mock-adapter).
  - Cliente fetch de recordatorios/metas con mocks de fetch manuales (éxito y 409).

v0.13.9
- Telemetría dev (opcional):
  - Nuevo módulo `src/telemetry.ts` con `logEvent(name, data)` y buffer en memoria (200 eventos).
  - Activado solo en `__DEV__` o si `EXPO_PUBLIC_TELEMETRY=dev`.
  - Eventos instrumentados: `network_ping`, `prefs_save_*`, `goal_save_*`, `recover_*` (meta/evento/recordatorio).

v0.14.0
- Offline mínimo (metas):
  - Cache local de la lista de metas y cola de operaciones (crear/actualizar) usando AsyncStorage.
  - En red caída: la lista usa el cache y crear/editar operan de forma optimista y se encolan para sincronizar luego.
  - Al iniciar la app se intenta procesar la cola automáticamente.
  - Nuevo botón en Configuración: “Reintentar sync offline” para forzar la sincronización manual y ver resultado por toasts.

v0.14.1 (Fixes y coherencia)
- Backend:
  - Version de la API alineada al changelog (FastAPI `version=0.14.1`).
  - Parametrización de CORS mediante variable de entorno `MYPLANU_CORS_ORIGINS` (lista separada por comas, fallback `*`).
  - Endpoint `/papelera/recordatorios` corrigió uso errado de `EventosService` y ahora emplea `RecordatoriosService.ListarRecordatoriosEliminados`.
  - Comentario y refuerzo en `.gitignore` para excluir bases SQLite (`*.db`, `apps/api/datos.db`).
- Móvil:
  - `PrincipalScreen` ahora usa `services/goals.listGoals()` (cache + cola offline) en lugar de `ClienteApi.ObtenerMetas` asegurando coherencia con la funcionalidad offline de v0.14.0.
- Documentación:
  - Encabezado actualizado a `MyPlanU v0.14.1` y sección de fixes añadida.

v0.15.0 (JSON bodies y contratos unificados)
- Backend:
  - Introducidos modelos Pydantic (`schemas.py`) para request/response: MetaCrear/Actualizar/Respuesta, EventoCrear/Actualizar/Respuesta, RecordatorioCrear/Actualizar/Respuesta.
  - Endpoints POST/PATCH de `/metas`, `/eventos` y `/recordatorios` ahora aceptan cuerpos JSON en lugar de query params.
  - Campos de repetición (`FrecuenciaRepeticion`, `IntervaloRepeticion`, `DiasSemana`) se envían en objeto `Repeticion`. `DiasSemana` se recibe como lista (ej. `["Lun","Mie"]`) y se almacena como CSV interno.
  - Estandarización de mensajes de error: patrones `MetaInvalida: ...`, `EventoInvalido: ...`, `RecordatorioInvalido: ...`.
- Móvil:
  - Cliente `ClienteApi` migrado a POST/PATCH JSON para metas, eventos y recordatorios (incluye repetición y zonas horarias en body).
  - Servicios `services/goals` actualizados a JSON y cola offline (`offline.ts`) procesando create/update de metas con body JSON.
- Migración / Breaking Changes:
  - Antes: `POST /metas?PropietarioId=1&Titulo=...&TipoMeta=...` → Ahora: `POST /metas` con JSON.
  - Antes: `POST /eventos?...Inicio=...&Fin=...` → Ahora: `POST /eventos` con JSON (incluye `Repeticion`).
  - Antes: `POST /recordatorios?...` → Ahora: `POST /recordatorios` con JSON.
  - Cualquier cliente que dependiera de query strings para crear/actualizar debe actualizarse.
- TODO restante antes de cerrar v0.15.0:
  - Revisar roles/permisos (fuera de alcance inmediato). 
  - Revisar consistencia de conversion de zonas (documentado, funcional actual).

Ejemplos cURL (nuevos contratos JSON)
-------------------------------------
Crear Meta:
```bash
curl -X POST http://localhost:8000/metas \
  -H 'Content-Type: application/json' \
  -d '{
    "PropietarioId": 1,
    "Titulo": "Estudiar Algebra",
    "TipoMeta": "Academica",
    "Descripcion": "Repasar capitulos 1-3"
  }'
```

Actualizar Meta (solo titulo):
```bash
curl -X PATCH http://localhost:8000/metas/10 \
  -H 'Content-Type: application/json' \
  -d '{ "Titulo": "Estudiar Algebra II" }'
```

Crear Evento con repetición semanal (Lunes y Miercoles):
```bash
curl -X POST http://localhost:8000/eventos \
  -H 'Content-Type: application/json' \
  -d '{
    "MetaId": 10,
    "PropietarioId": 1,
    "Titulo": "Sesion de estudio",
    "Inicio": "2025-09-25T14:00:00",
    "Fin": "2025-09-25T15:00:00",
    "Repeticion": { "Frecuencia": "Semanal", "Intervalo": 1, "DiasSemana": ["Lun","Mie"] },
    "ZonaHorariaEntrada": "America/Mexico_City"
  }'
```

Actualizar Evento (cambiar horario):
```bash
curl -X PATCH http://localhost:8000/eventos/55 \
  -H 'Content-Type: application/json' \
  -d '{ "Inicio": "2025-09-26T14:00:00", "Fin": "2025-09-26T15:30:00" }'
```

Crear Recordatorio:
```bash
curl -X POST http://localhost:8000/recordatorios \
  -H 'Content-Type: application/json' \
  -d '{
    "EventoId": 55,
    "FechaHora": "2025-09-26T13:50:00",
    "Canal": "Local",
    "Mensaje": "Preparar cuaderno",
    "ZonaHorariaEntrada": "America/Mexico_City"
  }'
```

Actualizar Recordatorio (mensaje):
```bash
curl -X PATCH http://localhost:8000/recordatorios/77 \
  -H 'Content-Type: application/json' \
  -d '{ "Mensaje": "Recordar materiales" }'
```

Notas sobre Zonas Horarias:
- `ZonaHorariaEntrada`: interpreta campos de fecha/hora del body (naive) en esa zona y los persiste en UTC.
- `ZonaHoraria`: controla la zona en la que se devuelven las fechas (si no se pasa, se usa la del `UsuarioId` o UTC).

TODOs siguientes (planeados)
----------------------------
- Permisos por rol: Dueno, Colaborador, Lector (validacion en Services).
- Cascada logica: al eliminar Meta, propagar a Eventos y Recordatorios.
- Persistencia real en Crear/Editar Meta desde movil.
- Manejo de autenticacion real en Login/Registro.
- Organización del código: revisar espaciados, consistencia de formato y separación visual para mejorar legibilidad.
- IP / conectividad móvil: garantizar acceso desde dispositivo físico (Expo LAN) con autenticación y servicios funcionando sobre la IP configurada.

v0.15.1 (Hardening repetición y pruebas)
- Backend:
  - `DiasSemana` ahora se expone como lista en todas las respuestas (antes CSV). La conversión lista↔CSV se centralizó en Services.
  - Validación de `IntervaloRepeticion` movida a Services para emitir `EventoInvalido` / `RecordatorioInvalido` (400) en lugar de 422 de esquema.
  - Respuestas de eventos/recordatorios normalizan repetición y mantienen patrones de error estandarizados.
  - Nuevas pruebas: proyección semanal con DiasSemana, intervalos negativos → error 400, persistencia de DiasSemana en recordatorios.
- Móvil:
  - Cola offline intacta; nuevas pruebas Jest para flujo base, reintento parcial, orden create→update y persistencia tras reinicio.
  - Actualizado a consumir `DiasSemana` como lista (sin dependencia de CSV legacy).
- Documentación:
  - Sección de errores estandarizados agregada.
  - Changelog marca 0.15.0 como estable y describe cambios de 0.15.1.
- Notas:
  - Breaking: clientes que esperaban `DiasSemana` CSV deben adaptarse (móvil ya alineado).
  - Preparación para futuras mejoras de permisos y autenticación.

Errores estandarizados (patrones y ejemplos)
-------------------------------------------
El backend expone mensajes de error consistentes en `detail` para facilitar el mapeo en el cliente. Formatos clave:

1. Validaciones de dominio (400):
   - `MetaInvalida: <motivo>`
   - `EventoInvalido: <motivo>`
   - `RecordatorioInvalido: <motivo>`
   Ejemplos:
```json
{
  "detail": "EventoInvalido: IntervaloRepeticion debe ser > 0"
}
```
```json
{
  "detail": "RecordatorioInvalido: FechaHora no puede estar en el pasado"
}
```

2. Recurso no encontrado (404):
```json
{
  "detail": "Meta no encontrada"
}
```
```json
{
  "detail": "Evento no encontrado"
}
```

3. Conflictos (409) (ej. duplicados):
```json
{
  "detail": "MetaInvalida: ya existe una meta con ese Titulo para el Propietario"
}
```

4. Errores de validación de entrada (422) (Pydantic) se reservan para formato JSON o tipos erróneos, pero la mayoría de reglas de negocio se trasladaron a Services para devolver 400 con los patrones anteriores.

5. Eliminados/recuperación (400/409):
```json
{
  "detail": "EventoInvalido: no se puede recuperar porque la Meta padre sigue eliminada"
}
```

Buenas prácticas cliente:
- Mostrar `detail` directamente en toasts si inicia con `<Algo>Invalido:` recortando el prefijo opcionalmente.
- Reintentos automáticos sólo para errores de red (timeout, offline) y no para 400/409.
- Mapear 404 a un estado de "Recurso eliminado o inexistente" y ofrecer navegación atrás.

v0.16.0 (Autenticación JWT básica)
- Backend:
  - Nuevos endpoints `/auth/registro` y `/auth/login`.
  - Registro guarda contraseña hasheada (bcrypt via passlib) y devuelve token JWT.
  - Login valida credenciales y entrega `{ access_token, token_type="bearer" }`.
  - Dependencia `get_current_user` protege `/metas`, `/eventos`, `/recordatorios` y `/papelera` (401 si token inválido / ausente, 403 si acceso a recurso de otro usuario según reglas actuales de propietario).
  - Campo `ContrasenaHash` agregado a `Usuario` (no se retorna en respuestas).
- Móvil:
  - Pantalla `LoginRegistroScreen` con modos registro / login.
  - Token persistido en AsyncStorage y agregado en header `Authorization: Bearer <token>` por interceptor Axios.
  - Botón "Cerrar Sesión" en Configuración que limpia token y redirige a pantalla de login.
  - Navegación condicionada al estado de autenticación (si no hay token → login, si hay token → tabs principales).
- Seguridad / Notas:
  - SECRET_KEY y ACCESS_TOKEN_EXPIRE_MINUTES configurables por variables de entorno (fallback dev inseguros si no se definen).
  - Recomendado rotar secret y mover a almacén seguro en despliegues productivos.
  - Próximos pasos sugeridos: refresh tokens, revocación, roles/granularidad de permisos.

Ejemplos cURL autenticación
---------------------------
Registro (dev):
```bash
curl -X POST http://localhost:8000/auth/registro \
  -H 'Content-Type: application/json' \
  -d '{"Correo":"demo@example.com","Nombre":"Demo","Contrasena":"demo123"}'
```

Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"Correo":"demo@example.com","Contrasena":"demo123"}'
```

Usar token para listar metas:
```bash
TOKEN="$(curl -s -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' -d '{"Correo":"demo@example.com","Contrasena":"demo123"}' | jq -r .access_token)"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/metas
```

Errores esperados auth:
- 401 Unauthorized: token ausente, expirado o inválido (`{"detail":"Token invalido"}` o `{"detail":"Credenciales invalidas"}`).
- 403 Forbidden: acceso a recurso que no pertenece al usuario autenticado (`{"detail":"Forbidden"}`).
- 409 Conflict: correo ya registrado en `/auth/registro`.

v0.16.1 (Ajustes post-autenticación)
- Backend y pruebas:
  - Nuevo helper `ObtenerEngine()` expone el engine de SQLModel para reutilizarlo en pruebas y utilidades.
  - Las pruebas de eventos y recordatorios ahora usan un helper de autenticación que crea usuario y token antes de invocar los endpoints protegidos.
- Móvil:
  - `fetchJson()` incluye automáticamente el header `Authorization` cuando hay token almacenado, alineando las llamadas `fetch` con el cliente Axios.
  - Pantalla Crear/Editar Meta reemplaza el campo libre de tipo por un selector accesible entre "Individual" y "Colectiva".
  - `services/goals` normaliza `TipoMeta`, limita los valores permitidos y reutiliza la constante `GOAL_TYPES` en UI y capa offline.

