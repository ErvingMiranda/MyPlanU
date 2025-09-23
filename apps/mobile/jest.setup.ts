import { server } from './test/msw/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Reduce noise in test output
jest.spyOn(console, 'debug').mockImplementation(() => {});
