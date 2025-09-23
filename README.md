# MyPlanU
MyPlanU v0.13.6
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

TODOs siguientes (planeados)
----------------------------
- Permisos por rol: Dueno, Colaborador, Lector (validacion en Services).
- Cascada logica: al eliminar Meta, propagar a Eventos y Recordatorios.
- Persistencia real en Crear/Editar Meta desde movil.
- Manejo de autenticacion real en Login/Registro.
