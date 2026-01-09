/**
 * Connectivity - Main App Component
 * 
 * NOTE: This module is designed for IoT Device Profile Management.
 * This standalone app can be used independently or integrated into the Unified Viewer.
 */

import React from 'react';
import { DeviceProfileManager } from './components/DeviceProfileManager';
import './index.css';

// Export viewerSlots for host integration
export { viewerSlots } from './slots/index';

const ModuleApp: React.FC = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://nkz.artotxiki.com/api/connectivity';

  return (
\u003cdiv className = "w-full bg-gray-50 min-h-screen"\u003e
{/* Header */ }
\u003cdiv className = "bg-white border-b border-gray-200 shadow-sm"\u003e
\u003cdiv className = "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"\u003e
\u003cdiv className = "flex items-center justify-between h-16"\u003e
\u003cdiv className = "flex items-center gap-3"\u003e
\u003cspan className = "text-3xl"\u003e📡\u003c / span\u003e
\u003ch1 className = "text-2xl font-bold text-gray-900"\u003eConnectivity Manager\u003c / h1\u003e
\u003c / div\u003e
\u003c / div\u003e
\u003c / div\u003e
\u003c / div\u003e

{/* Main Content */ }
\u003cdiv className = "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"\u003e
\u003cDeviceProfileManager apiBaseUrl = { apiBaseUrl } /\u003e
\u003c / div\u003e
\u003c / div\u003e
  );
};

// CRITICAL: Export as default - required for Module Federation
export default ModuleApp;
