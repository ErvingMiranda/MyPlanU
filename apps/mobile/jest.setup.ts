import { server } from './test/msw/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Reduce noise in test output
jest.spyOn(console, 'debug').mockImplementation(() => {});

// Mock AsyncStorage for Jest (react-native environment)
jest.mock('@react-native-async-storage/async-storage', () => require('@react-native-async-storage/async-storage/jest/async-storage-mock'));
