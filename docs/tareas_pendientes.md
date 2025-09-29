# Plan de trabajo por versión

Este documento transforma los TODO repartidos en el repositorio en un plan de ejecución por versiones menores. Cada versión agrupa
las tareas necesarias para avanzar hacia una app estable y alineada con la arquitectura MSV.

## Cómo priorizamos

- **Enfoque incremental:** cada versión entrega valor tangible y desbloquea la siguiente.
- **Paridad backend/móvil:** cuando se introducen reglas nuevas en la API se programan de inmediato los cambios de app.
- **Calidad continua:** toda versión incluye tareas de pruebas, documentación y limpieza necesarias para mantener la deuda bajo
  control.

## v0.17.0 — Permisos y cascadas básicas

### Backend
- [ ] Implementar validaciones de permisos por rol (Dueño, Colaborador, Lector) en servicios de Metas, Eventos, Recordatorios y
      Usuarios respetando MSV.
- [ ] Definir el comportamiento de cascada al eliminar una Meta, asegurando el manejo coherente de Eventos y Recordatorios
      relacionados (eliminar, recuperar, dependencias).
- [ ] Determinar la cascada al eliminar un Usuario para proteger la integridad de Metas, Eventos y Recordatorios asociados.
- [ ] Validar que una Meta "Colectiva" tenga al menos un Colaborador antes de permitir cierre o cambio a estado final.

### Móvil
- [ ] Ajustar la UI de DetalleMeta y CrearEditarMeta para reflejar errores de permisos (mensajes en toasts y bloqueos de acción).
- [ ] Actualizar el cliente API para propagar los errores de autorización y estado de cascada.

### Plataforma y calidad
- [ ] Documentar las reglas de permiso y cascada en la guía MSV y en el README.
- [ ] Alinear fixtures/datos de pruebas con los nuevos roles.

## v0.18.0 — Auditoría y notificaciones

### Backend
- [ ] Registrar en bitácora quién y cuándo recupera Metas, Eventos y Recordatorios (acciones undo).
- [ ] Integrar un mecanismo de notificación para avisar a participantes cuando un Evento sea eliminado (soft delete).
- [ ] Revisar y corregir la consistencia de conversiones de zona horaria en la API para Eventos y Recordatorios.

### Móvil
- [ ] Consumir el endpoint real de participantes en `DetalleEventoScreen`.
- [ ] Mostrar alertas locales cuando se elimine un Evento al que pertenece el usuario.

### Plataforma y calidad
- [ ] Publicar nueva guía rápida de monitoreo y auditoría en `docs/`.
- [ ] Añadir pruebas automáticas que cubran la bitácora y notificaciones.

## v0.19.0 — Experiencia móvil y sincronización

### Backend
- [ ] Exponer endpoints complementarios necesarios para la cola offline (batch de Metas/Eventos).

### Móvil
- [ ] Integrar Expo Notifications para recordatorios locales y sincronización con recordatorios backend.
- [ ] Asegurar persistencia real al crear/editar Metas con sincronización offline → online.
- [ ] Garantizar conectividad desde dispositivos físicos (Expo LAN) respetando IP configurada y rutas protegidas.

### Plataforma y calidad
- [ ] Revisar y mejorar la organización del código (formato, espaciado, separación visual) en backend y móvil.
- [ ] Documentar los flujos offline en README y `docs/`.

## Backlog posterior a v0.19.0

- [ ] Revisar la necesidad de reforzar autenticación (refresh tokens, revocación) según feedback de QA.
- [ ] Explorar soporte multizona horaria en cliente (preferencias por usuario).
