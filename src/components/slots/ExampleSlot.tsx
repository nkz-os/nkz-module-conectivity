/**
 * Example Slot Component with API Integration
 * 
 * This demonstrates:
 * - Accessing viewer context (selected entity, layers)
 * - Making API calls using the SDK
 * - Loading and error states
 * - Using UI Kit components
 * 
 * Slot components should:
 * - Be mobile-first (designed for 300-400px panels)
 * - Use UI Kit components for consistency
 * - Access viewer context via useViewer() hook
 * - Handle loading and error states gracefully
 */

import React, { useState, useEffect } from 'react';
import { useViewer, useAuth, useTranslation } from '@nekazari/sdk';
import { useUIKit } from '@/hooks/useUIKit';
import { useModuleApi } from '@/services/api';
import { RefreshCw, Plus, Trash2, AlertCircle } from 'lucide-react';

interface DataItem {
  id: string;
  name: string;
  description?: string;
  value: number;
}

interface ExampleSlotProps {
  className?: string;
}

export const ExampleSlot: React.FC<ExampleSlotProps> = ({ className }) => {
  const { t } = useTranslation('connectivity');
  const { Card, Button } = useUIKit();
  const { selectedEntityId, selectedEntityType } = useViewer();
  const { user, isAuthenticated } = useAuth();
  const api = useModuleApi();

  // State
  const [items, setItems] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch data from the module API
   */
  const fetchData = async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.getData();
      setItems(response.items || []);
    } catch (err: any) {
      console.error('[ExampleSlot] Error fetching data:', err);
      setError(err.message || t('exampleSlot.errors.load'));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new demo item
   */
  const createItem = async () => {
    setLoading(true);
    setError(null);

    try {
      const newItem = await api.createData({
        name: `Item ${Date.now()}`,
        description: t('exampleSlot.demoDescription'),
        value: Math.random() * 100,
      });
      setItems(prev => [...prev, newItem]);
    } catch (err: any) {
      console.error('[ExampleSlot] Error creating item:', err);
      setError(err.message || t('exampleSlot.errors.create'));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete an item
   */
  const deleteItem = async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      await api.deleteData(id);
      setItems(prev => prev.filter(item => item.id !== id));
    } catch (err: any) {
      console.error('[ExampleSlot] Error deleting item:', err);
      setError(err.message || t('exampleSlot.errors.delete'));
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [isAuthenticated]);

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <Card padding="md" className={className}>
        <div className="flex items-center gap-2 text-amber-600">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{t('exampleSlot.loginRequired')}</span>
        </div>
      </Card>
    );
  }

  return (
    <Card padding="md" className={className}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-800">
            {t('exampleSlot.title')}
          </h3>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchData}
              disabled={loading}
              className="p-1"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={createItem}
              disabled={loading}
              className="p-1"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Viewer Context Info */}
        <div className="text-xs bg-slate-50 rounded p-2 space-y-1">
          <div className="flex justify-between">
            <span className="text-slate-500">{t('exampleSlot.selectedEntity')}:</span>
            <span className="text-slate-700 font-mono">
              {selectedEntityId || t('exampleSlot.none')}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('exampleSlot.entityType')}:</span>
            <span className="text-slate-700">
              {selectedEntityType || t('exampleSlot.none')}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('exampleSlot.user')}:</span>
            <span className="text-slate-700 truncate max-w-[150px]">
              {user?.email || t('exampleSlot.unknownUser')}
            </span>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 rounded p-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Data List */}
        <div className="space-y-2">
          {items.length === 0 && !loading && (
            <div className="text-sm text-slate-500 text-center py-4">
              {t('exampleSlot.emptyList')}
            </div>
          )}

          {items.map(item => (
            <div
              key={item.id}
              className="flex items-center justify-between bg-slate-50 rounded p-2"
            >
              <div className="min-w-0">
                <div className="text-sm font-medium text-slate-800 truncate">
                  {item.name}
                </div>
                <div className="text-xs text-slate-500">
                  {t('exampleSlot.value', { value: item.value.toFixed(2) })}
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteItem(item.id)}
                disabled={loading}
                className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default ExampleSlot;
