import { defineConfig } from 'vite'

// Minimal Vite config. The viewer is a plain TypeScript + three.js app.
// Control input arrives over a WebSocket from the Python bridge (see ../server).
export default defineConfig({
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
  // .vrm / .vrma are served as static binary assets from /public/models.
  assetsInclude: ['**/*.vrm', '**/*.vrma'],
})
