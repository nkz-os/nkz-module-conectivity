/**
 * NKZ Module Entry Point — IIFE bundle
 *
 * This file is the single entry point compiled into nkz-module.js.
 * When the browser executes it, it self-registers with the host via
 * window.__NKZ__.register(). The host's SlotRegistry then re-renders
 * the affected slots with the new widgets.
 *
 * IMPORTANT: The module id MUST match the marketplace_modules.id in PostgreSQL.
 */

import { defineModule } from '@nekazari/module-kit';
import './i18n';
import ModuleApp from './App';
import { moduleSlots } from './slots';

const MODULE_ID = 'connectivity';

const moduleConfig = defineModule({
  id: MODULE_ID,
  displayName: 'Connectivity',
  accent: { base: '#3B82F6', soft: '#DBEAFE', strong: '#1D4ED8' },
  hostApiVersion: '^2.0.0',
  api: { basePath: '/api/connectivity' },
});

declare global {
  interface Window {
    __NKZ__: {
      register: (module: {
        id: string;
        main?: React.ComponentType<any>;
        viewerSlots?: typeof moduleSlots;
        version?: string;
      }) => void;
    };
  }
}

if (typeof window !== 'undefined' && window.__NKZ__) {
  window.__NKZ__.register({
    id: MODULE_ID,
    main: ModuleApp,
    viewerSlots: moduleSlots,
    version: '1.0.0',
  });
} else {
  console.error(`[${MODULE_ID}] window.__NKZ__ not found. Is this bundle loaded inside the NKZ host?`);
}

export default moduleConfig;
