// msw v2 ships ESM by default; jest-expo supports transforming ESM but resolution can vary.
// Use dynamic import to avoid resolution issues under Jest.
import { handlers } from './handlers';

let setupServerFn: any;
// eslint-disable-next-line @typescript-eslint/no-var-requires
setupServerFn = require('msw/node').setupServer;

export const server = setupServerFn(...handlers);
