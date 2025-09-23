let ZonaHorariaSeleccionada: string | undefined = undefined;

export function EstablecerZonaHoraria(zona?: string) {
  ZonaHorariaSeleccionada = zona || undefined;
}

export function ObtenerZonaHoraria(): string | undefined {
  if (ZonaHorariaSeleccionada) return ZonaHorariaSeleccionada;
  try {
    // Intentar detectar zona del dispositivo
    const tz = (Intl as any)?.DateTimeFormat?.().resolvedOptions?.().timeZone;
    if (typeof tz === 'string' && tz.length > 0) return tz;
  } catch {}
  return undefined;
}
