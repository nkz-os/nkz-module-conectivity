import React from 'react';
import { DeviceProfileManager } from './components/DeviceProfileManager';
import './index.css';

const ModuleApp: React.FC = () => {
  // API base is injected at runtime by the host nginx (window.__ENV__.VITE_API_URL).
  // Falls back to build-time env, then relative path (same-origin deployment).
  const apiBase =
    (window as any).__ENV__?.VITE_API_URL ||
    (import.meta as any).env?.VITE_API_URL ||
    '';
  const apiBaseUrl = (import.meta as any).env?.VITE_API_BASE_URL || `${apiBase}/api/connectivity`;

  return (
    <div className="w-full bg-gray-50 min-h-screen">
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <span className="text-3xl">📡</span>
              <h1 className="text-2xl font-bold text-gray-900">Connectivity Manager</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DeviceProfileManager apiBaseUrl={apiBaseUrl} />
      </div>
    </div>
  );
};

export default ModuleApp;
