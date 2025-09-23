# MyPlanU
MyPlanU v0.4
=================

Descripcion
-----------
MyPlanU es una agenda inteligente y colaborativa para estudiantes y equipos. Esta version (v0.4) agrega la base de la app movil con navegacion y consumo de la API de metas, manteniendo las convenciones en español y PascalCase.

Estructura del Monorepo
-----------------------
- apps/
	- api/ (FastAPI + SQLModel + SQLite)
	- mobile/ (Expo React Native + TypeScript)
- packages/
	- shared-types/ (placeholder para tipos compartidos)
- .editorconfig, .gitignore, README.md

Convenciones
------------
- Nombres de codigo en espanol, sin tildes ni letra eñe. Ejemplos: Correo, PropietarioId, TipoMeta.
- PascalCase para clases, variables, funciones y atributos tanto en backend como en movil.
- Arquitectura Models–Services–Views (MSV).

Requisitos Previos
------------------
- Python 3.11+
- Node.js 18+ y npm o yarn
- Expo CLI (se instala al correr el proyecto movil por primera vez)

Como Ejecutar
-------------
Backend (API):
1. Crear y activar un entorno virtual de Python.
2. Instalar dependencias.
3. Ejecutar el servidor de desarrollo.

Movil (Expo):
1. Instalar dependencias de Node.
2. Definir la URL de la API (opcional). Puedes usar EXPO_PUBLIC_API_URL para apuntar al backend.
3. Levantar el servidor de Expo.

Comandos Rapidos (opcionales)
-----------------------------
Backend:
```
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn app.main:Aplicacion --reload --host 0.0.0.0 --port 8000
```

Movil:
```
cd apps/mobile
npm install
# Opcional: configurar la URL del backend para el cliente movil
# export EXPO_PUBLIC_API_URL="http://127.0.0.1:8000"
npm run start
```

Cambios de esta version
-----------------------
- App movil base (Expo + TypeScript):
	- Navegacion: Stack (LoginRegistro → Principal) y Tabs (Principal, Notificaciones, Configuracion).
	- Pantallas: LoginRegistroScreen, PrincipalScreen (lista metas desde API), DetalleMetaScreen, CrearEditarMetaScreen (formulario basico sin persistencia), NotificacionesScreen, ConfiguracionScreen.
	- Cliente API en `apps/mobile/src/api/ClienteApi.ts` y configuracion de URL en `apps/mobile/src/config.ts` (usa `process.env.EXPO_PUBLIC_API_URL` o `http://127.0.0.1:8000`).
	- React Query configurado en el root para consultas (lista de metas).

Backend (continuidad de v0.3):
	- Services en español y PascalCase.
	- Rutas: GET /salud; CRUD /usuarios; CRUD /metas.

TODOs siguientes (planeados):
- Permisos por rol: Dueno, Colaborador, Lector (validacion en Services).
- Cascada logica: al eliminar Meta, propagar a Eventos y Recordatorios.
 - Persistencia real en Crear/Editar Meta desde movil.
 - Manejo de autenticacion real en Login/Registro.
