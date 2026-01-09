/**
 * Slot Registration for Connectivity
 * Defines all slots that integrate with the Unified Viewer
 */

import React from 'react';
// Import slot components
import { ExampleSlot } from '../components/slots/ExampleSlot';

// Type definitions for slot widgets (matching SDK types)
export interface SlotWidgetDefinition {
  id: string;
  component: string;
  priority: number;
  localComponent: React.ComponentType<any>;
  defaultProps?: Record<string, any>;
  showWhen?: {
    entityType?: string[];
    layerActive?: string[];
  };
}

export type SlotType = 'layer-toggle' | 'context-panel' | 'bottom-panel' | 'entity-tree';

export type ModuleViewerSlots = Record<SlotType, SlotWidgetDefinition[]>;

/**
 * Connectivity Slots Configuration
 * These slots integrate the module into the Unified Viewer
 * 
 * Available slots:
 * - 'layer-toggle': Layer manager controls
 * - 'context-panel': Right panel (entity details)
 * - 'bottom-panel': Bottom panel (timeline, charts)
 * - 'entity-tree': Left panel (entity tree)
 */
export const moduleSlots: ModuleViewerSlots = {
  'layer-toggle': [
    // Add your layer toggle widgets here
    // {
    //   id: 'connectivity-layer-control',
    //   component: 'MyLayerControl',
    //   priority: 10,
    //   localComponent: MyLayerControl,
    // }
  ],
  'context-panel': [
    // ExampleSlot - demonstrates API integration
    {
      id: 'connectivity-example',
      component: 'ExampleSlot',
      priority: 50,  // Lower priority = higher in list
      localComponent: ExampleSlot,
      // Uncomment to show only for specific entity types:
      // showWhen: {
      //   entityType: ['AgriParcel', 'Building']
      // }
    }
  ],
  'bottom-panel': [
    // Add your bottom panel widgets here (charts, timelines, etc.)
  ],
  'entity-tree': [
    // Add your entity tree widgets here
  ]
};

/**
 * Export as viewerSlots for host integration
 * The host will look for this export to register slots
 */
export const viewerSlots = moduleSlots;
