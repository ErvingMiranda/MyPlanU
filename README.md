# MyPlanU
MyPlanU v0.8
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

TODOs siguientes (planeados)
----------------------------
- Permisos por rol: Dueno, Colaborador, Lector (validacion en Services).
- Cascada logica: al eliminar Meta, propagar a Eventos y Recordatorios.
- Persistencia real en Crear/Editar Meta desde movil.
- Manejo de autenticacion real en Login/Registro.
