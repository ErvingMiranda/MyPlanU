import { server } from './test/msw/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Reduce noise in test output
jest.spyOn(console, 'debug').mockImplementation(() => {});

// Mock AsyncStorage for Jest (react-native environment)
jest.mock('@react-native-async-storage/async-storage', () => require('@react-native-async-storage/async-storage/jest/async-storage-mock'));

// Mock expo-constants to evitar importaciones ESM en Jest
jest.mock('expo-constants', () => ({
  expoConfig: { hostUri: '127.0.0.1:19000' },
}));
