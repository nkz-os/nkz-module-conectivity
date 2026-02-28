import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
    react({ jsxRuntime: 'classic' }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5003,
    cors: true,
    proxy: {
      '/api': {
        // Set VITE_DEV_API_TARGET in .env.local to proxy to a running API server
        target: process.env.VITE_DEV_API_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/moduleEntry.ts'),
      name: 'NkzConnectivityModule',
      formats: ['iife'],
      fileName: () => 'nkz-module.js',
    },
    rollupOptions: {
      external: [
        'react',
        'react-dom',
        'react-dom/client',
        'react-router-dom',
        '@nekazari/sdk',
        '@nekazari/ui-kit',
      ],
      output: {
        globals: {
          'react':             'React',
          'react-dom':         'ReactDOM',
          'react-dom/client':  'ReactDOM',
          'react-router-dom':  'ReactRouterDOM',
          '@nekazari/sdk':     '__NKZ_SDK__',
          '@nekazari/ui-kit':  '__NKZ_UI__',
        },
        inlineDynamicImports: true,
      },
    },
    minify: true,
    cssCodeSplit: false,
  },
});
