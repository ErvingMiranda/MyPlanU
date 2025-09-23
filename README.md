# MyPlanU
MyPlanU v0.1
=================

Descripcion
-----------
MyPlanU es una agenda inteligente y colaborativa para estudiantes y equipos. Esta version inicial (v0.1) instala el monorepo con arquitectura Models–Services–Views, un backend en Python (FastAPI + SQLModel + SQLite) y un frontend movil con Expo React Native + TypeScript. Aun sin autenticacion real ni Docker.

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
2. Levantar el servidor de Expo.

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
npm run start
```

Cambios de esta version
-----------------------
- Monorepo creado con back y movil basicos.
- Estructura Models–Services–Views en el backend (HealthView basico).
- Convenciones de nombres y estilo establecidas.
- Archivos base: .editorconfig, .gitignore, README.md.
