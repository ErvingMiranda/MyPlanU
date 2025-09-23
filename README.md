# MyPlanU
MyPlanU v0.5
=================

Descripcion
-----------
MyPlanU es una agenda inteligente y colaborativa para estudiantes y equipos. Esta version (v0.5) conecta los flujos de navegacion en la app movil segun el diagrama propuesto.

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
App movil (flujos v0.5):
	- LoginRegistroScreen → (replace) → PrincipalScreen.
	- PrincipalScreen → DetalleMetaScreen (al tocar una meta).
	- PrincipalScreen → CrearEditarMetaScreen (boton "+").
	- PrincipalScreen → NotificacionesScreen y → ConfiguracionScreen (botones).
	- NotificacionesScreen → DetalleMetaScreen (mock) o volver a PrincipalScreen.
	- DetalleMetaScreen → CrearEditarMetaScreen (boton "Editar").
	- ConfiguracionScreen → volver a PrincipalScreen con "Guardar" o "Cancelar".
	- PrincipalScreen → LoginRegistroScreen (boton "CerrarSesion").

Base tecnica:
	- Navegacion: Stack + Tabs.
	- React Query en el root.
	- Cliente API `src/api/ClienteApi.ts` y configuracion `src/config.ts`.

TODOs siguientes (planeados):
- Permisos por rol: Dueno, Colaborador, Lector (validacion en Services).
- Cascada logica: al eliminar Meta, propagar a Eventos y Recordatorios.
 - Persistencia real en Crear/Editar Meta desde movil.
 - Manejo de autenticacion real en Login/Registro.
