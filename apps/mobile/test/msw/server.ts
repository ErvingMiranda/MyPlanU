// msw v2 ships ESM by default; jest-expo supports transforming ESM but resolution can vary.
// Use dynamic import to avoid resolution issues under Jest.
import { handlers } from './handlers';

let setupServerFn: any;
// Cargar wrapper CJS para evitar problemas de export conditions con react-native
// eslint-disable-next-line @typescript-eslint/no-var-requires
setupServerFn = require('./msw-node.cjs').setupServer;

export const server = setupServerFn(...handlers);
