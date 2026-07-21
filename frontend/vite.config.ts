import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true,
    },
    host: true, // Needed for docker
    strictPort: true,
    port: 15173,
    allowedHosts: true, // Permite conexiones desde cualquier DNS/IP (como EC2)
  }
})
