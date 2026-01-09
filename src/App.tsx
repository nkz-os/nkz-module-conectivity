import React from 'react';
import { DeviceProfileManager } from './components/DeviceProfileManager';
import './index.css';

export { viewerSlots } from './slots/index';

const ModuleApp: React.FC = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://nkz.artotxiki.com/api/connectivity';

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
