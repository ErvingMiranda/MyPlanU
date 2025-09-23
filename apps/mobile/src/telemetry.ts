type TelemetryEvent = {
  name: string;
  ts: number;
  data?: Record<string, any>;
};

const RING_MAX = 200;
const buffer: TelemetryEvent[] = [];

function push(ev: TelemetryEvent) {
  buffer.push(ev);
  if (buffer.length > RING_MAX) buffer.shift();
  if (__DEV__) {
    // eslint-disable-next-line no-console
    console.log(`[telemetry] ${ev.name}`, ev.data ?? {});
  }
}

export function logEvent(name: string, data?: Record<string, any>) {
  const enabled = __DEV__ || process.env.EXPO_PUBLIC_TELEMETRY === 'dev';
  if (!enabled) return;
  push({ name, ts: Date.now(), data });
}

export function getRecentEvents(): TelemetryEvent[] { return [...buffer]; }
