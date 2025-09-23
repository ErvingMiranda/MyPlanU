/** @type {import('jest').Config} */
module.exports = {
  preset: 'jest-expo',
  testMatch: ['**/__tests__/**/*.(test|spec).[tj]s?(x)'],
  setupFiles: ['whatwg-fetch'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|react-native-gesture-handler|react-native-reanimated|react-native-safe-area-context|react-native-screens|@react-navigation|expo(nent)?|@expo(nent)?/.*|expo-modules-core)/)'
  ],
};
