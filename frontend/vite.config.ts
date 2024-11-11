/*
* File configures the Vite tool for the project. It imports the React plugin and the defineConfig function from Vita. 
* The configuration includes:
*   - Plugins: Uses a plugin for React.
*   - Build: Sets the output directory to ../static, empties the output directory before the build, and generates sourcemaps.
*   - Server: Sets proxy for /ask and /chat paths to http://localhost:5000.
* 
* This file is useful for customizing Vite's behavior for developing and building a project, 
* including integrating with React and setting up a proxy server for API requests.
* 
*/

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static',
    emptyOutDir: true,
    sourcemap: true
  },
  server: {
    proxy: {
      '/ask': 'http://localhost:5000',
      '/chat': 'http://localhost:5000'
    }
  }
})
