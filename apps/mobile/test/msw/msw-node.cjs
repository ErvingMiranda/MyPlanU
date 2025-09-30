// Wrapper para evitar la resolución por condición "react-native" del preset jest-expo
// que hace que "msw/node" sea null. Usamos la ruta CJS compilada directamente.
try {
	module.exports = require('msw/native');
} catch (e) {
	module.exports = require('msw/lib/node/index.js');
}
