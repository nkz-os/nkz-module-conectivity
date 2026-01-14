/**
 * Slot Registration for Connectivity Module
 * Defines all slots that integrate with the Unified Viewer.
 * 
 * All widgets include explicit moduleId for proper host integration.
 */

import React from 'react';
// Import slot components
import { ExampleSlot } from '../components/slots/ExampleSlot';

// Module identifier - used for all slot widgets
const MODULE_ID = 'connectivity';

// Type definitions for slot widgets (matching SDK types)
export interface SlotWidgetDefinition {
  id: string;
  /** Module ID that owns this widget. REQUIRED for remote modules. */
  moduleId: string;
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
 * All widgets explicitly declare moduleId for proper provider wrapping.
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
  ],
  'context-panel': [
    // ExampleSlot - demonstrates API integration
    {
      id: 'connectivity-example',
      moduleId: MODULE_ID,
      component: 'ExampleSlot',
      priority: 50,
      localComponent: ExampleSlot,
    }
  ],
  'bottom-panel': [],
  'entity-tree': []
};

/**
 * Export as viewerSlots for host integration
 * The host will look for this export to register slots
 */
export const viewerSlots = moduleSlots;
