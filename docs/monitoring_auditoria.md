# Guía rápida de auditoría y monitoreo

Esta guía resume cómo verificar las nuevas capacidades de auditoría y notificaciones introducidas en MyPlanU v0.18.0.

## Bitácora de recuperaciones

- Endpoint: `GET /bitacora/recuperaciones`
- Filtros:
  - `TipoEntidad` opcional (`Meta`, `Evento`, `Recordatorio`).
  - `SoloPropias` (por defecto `true`) limita la respuesta al usuario autenticado.
- Cada registro incluye `TipoEntidad`, `EntidadId`, `UsuarioId`, `Detalle` y `RegistradoEn` (UTC).
- Las acciones de recuperación desde la app o la API generan automáticamente un registro.

### Ejemplo rápido

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/bitacora/recuperaciones
```

## Notificaciones de eventos eliminados

- Al eliminar un evento se crea una notificación para el dueño y cada participante activo.
- Endpoint de lectura: `GET /notificaciones/sistema` (por defecto solo devuelve no leídas).
- Marcar como leída: `POST /notificaciones/{Id}/leer`.
- La app móvil consulta este endpoint periódicamente y muestra una alerta local por cada notificación pendiente.

### Flujo sugerido de monitoreo

1. Eliminar un evento compartido vía API o app.
2. Consultar `GET /notificaciones/sistema` con el colaborador para verificar la alerta pendiente.
3. Confirmar que `POST /notificaciones/{Id}/leer` marca la notificación como atendida.
4. Revisar la bitácora para comprobar la auditoría de recuperaciones si se revierte la eliminación.

## Buenas prácticas

- Mantener sincronizada la zona horaria del usuario antes de realizar recuperaciones para asegurar que los sellos de tiempo se interpretan correctamente.
- Automatizar una prueba de smoke que elimine y recupere un evento verificando notificaciones y bitácora.
