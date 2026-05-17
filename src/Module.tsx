import { defineModule } from '@nekazari/module-kit';
import { lazy } from 'react';
import './i18n';
import { moduleSlots } from './slots';
import pkg from '../package.json';

const MainPage = lazy(() => import('./App'));

export default defineModule({
  id: 'connectivity',
  displayName: 'Connectivity',
  version: pkg.version,
  hostApiVersion: '^2.0.0',
  description: 'Connectivity — Nekazari Platform Module',
  accent: { base: '#3B82F6', soft: '#DBEAFE', strong: '#1D4ED8' },
  icon: 'wifi',
  main: MainPage,
  api: { basePath: '/api/connectivity' },
  slots: moduleSlots as never,
});
