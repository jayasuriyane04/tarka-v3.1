import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  resolve: { preserveSymlinks: true },
  server: { port: 5175, proxy: { '/api': 'http://127.0.0.1:8003' } },
  build: { sourcemap: false },
});
