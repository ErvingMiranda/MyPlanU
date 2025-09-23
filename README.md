# MyPlanU
MyPlanU v0.3
=================

Descripcion
-----------
MyPlanU es una agenda inteligente y colaborativa para estudiantes y equipos. Esta version (v0.3) refactoriza la capa Services en el backend, mantiene CRUD en español con soft delete y deja TODOs claros para la siguiente iteracion.

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
- Refactor Services (espaniol + PascalCase):
	- UsuariosService.py: Crear, Listar, Obtener, Actualizar, Eliminar, BuscarPorCorreo, Existe
	- MetasService.py: CrearMeta, ListarMetas, Obtener, ActualizarMeta, EliminarMeta
- Reglas: Validar PropietarioId y bloquear operaciones si EliminadoEn no es nulo; listados excluyen EliminadoEn != None; PATCH actualiza ActualizadoEn.
- Rutas: GET /salud → {"estado":"ok"}; CRUD /usuarios; CRUD /metas.
- Frontend movil base (Expo + TS) sin cambios funcionales.

TODOs siguientes (planeados):
- Permisos por rol: Dueno, Colaborador, Lector (validacion en Services).
- Cascada logica: al eliminar Meta, propagar a Eventos y Recordatorios.
