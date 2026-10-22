import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation, useAuth } from '@nekazari/sdk';
import { useUIKit } from '@/hooks/useUIKit';
import { useModuleApi } from '@/services/api';
import { Plus, Edit, Trash2, Save, X, AlertCircle, Loader2 } from 'lucide-react';

interface MappingEntry {
  incoming_key: string;
  target_attribute: string;
  type: string;
  transformation?: string;
  unit?: string;
}

interface DeviceProfile {
  id?: string;
  name: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  sdm_entity_type: string;
  mappings: MappingEntry[];
  is_public: boolean;
}

export const DeviceProfileManager: React.FC = () => {
  const { t } = useTranslation('connectivity');
  const { isAuthenticated } = useAuth();
  const { Card, Button } = useUIKit();
  const api = useModuleApi();

  const [profiles, setProfiles] = useState<DeviceProfile[]>([]);
  const [editingProfile, setEditingProfile] = useState<DeviceProfile | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProfiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listProfiles();
      setProfiles(data?.items || []);
    } catch (err: any) {
      setError(err.message || t('profiles.errors.loadProfiles'));
      setProfiles([]);
    } finally {
      setLoading(false);
    }
  }, [api, t]);

  useEffect(() => {
    if (isAuthenticated) loadProfiles();
  }, [isAuthenticated, loadProfiles]);

  const handleSave = async (profile: DeviceProfile) => {
    setError(null);
    try {
      if (profile.id) {
        await api.updateProfile(profile.id, profile as any);
      } else {
        await api.createProfile(profile as any);
      }
      await loadProfiles();
      setEditingProfile(null);
      setIsCreating(false);
    } catch (err: any) {
      setError(err.message || t('profiles.errors.save'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('profiles.confirmDelete'))) return;
    setError(null);
    try {
      await api.deleteProfile(id);
      await loadProfiles();
    } catch (err: any) {
      setError(err.message || t('profiles.errors.delete'));
    }
  };

  const handleAddMapping = (profile: DeviceProfile) => {
    setEditingProfile({
      ...profile,
      mappings: [...profile.mappings, { incoming_key: '', target_attribute: '', type: 'Number' }],
    });
  };

  const handleRemoveMapping = (profile: DeviceProfile, index: number) => {
    setEditingProfile({
      ...profile,
      mappings: profile.mappings.filter((_, i) => i !== index),
    });
  };

  const handleMappingChange = (profile: DeviceProfile, index: number, field: keyof MappingEntry, value: string) => {
    const updated = [...profile.mappings];
    updated[index] = { ...updated[index], [field]: value };
    setEditingProfile({ ...profile, mappings: updated });
  };

  if (loading && profiles.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-nkz-muted">
        <Loader2 className="w-5 h-5 animate-spin mr-2" />
        {t('profiles.loading')}
      </div>
    );
  }

  const inputClass = 'w-full px-3 py-2 border border-nkz-border rounded-md bg-nkz-surface text-nkz-foreground focus:outline-none focus:ring-2 focus:ring-nkz-primary focus:border-transparent';
  const labelClass = 'block text-sm font-medium text-nkz-muted mb-1';

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {error && (
        <div className="mb-4 p-4 bg-nkz-danger-soft border border-nkz-danger-border rounded-lg text-nkz-danger">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-nkz-foreground">{t('profiles.title')}</h1>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            setIsCreating(true);
            setEditingProfile({ name: '', sdm_entity_type: 'AgriSensor', mappings: [], is_public: false });
          }}
        >
          <Plus className="w-4 h-4 mr-1" />{t('profiles.newButton')}
        </Button>
      </div>

      {(isCreating || editingProfile) && (
        <Card padding="lg" className="mb-6 border-2 border-nkz-primary">
          <h2 className="text-lg font-semibold text-nkz-foreground mb-4">
            {isCreating ? t('profiles.createTitle') : t('profiles.editTitle')}
          </h2>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className={labelClass}>{t('profiles.nameLabel')}</label>
              <input type="text" value={editingProfile?.name || ''} className={inputClass}
                onChange={(e) => setEditingProfile({ ...editingProfile!, name: e.target.value })} />
            </div>
            <div>
              <label className={labelClass}>{t('profiles.sdmTypeLabel')}</label>
              <select value={editingProfile?.sdm_entity_type || 'AgriSensor'} className={inputClass}
                onChange={(e) => setEditingProfile({ ...editingProfile!, sdm_entity_type: e.target.value })}>
                <option value="AgriSensor">AgriSensor</option>
                <option value="WeatherStation">WeatherStation</option>
                <option value="Device">Device</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>{t('profiles.manufacturerLabel')}</label>
              <input type="text" value={editingProfile?.manufacturer || ''} className={inputClass}
                onChange={(e) => setEditingProfile({ ...editingProfile!, manufacturer: e.target.value })} />
            </div>
            <div>
              <label className={labelClass}>{t('profiles.modelLabel')}</label>
              <input type="text" value={editingProfile?.model || ''} className={inputClass}
                onChange={(e) => setEditingProfile({ ...editingProfile!, model: e.target.value })} />
            </div>
          </div>

          <div className="mb-4">
            <label className={labelClass}>{t('profiles.descriptionLabel')}</label>
            <textarea value={editingProfile?.description || ''} className={inputClass} rows={2}
              onChange={(e) => setEditingProfile({ ...editingProfile!, description: e.target.value })} />
          </div>

          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold text-nkz-foreground">{t('profiles.mappingsTitle')}</h3>
              <Button variant="secondary" size="sm" onClick={() => handleAddMapping(editingProfile!)}>
                <Plus className="w-3 h-3 mr-1" />{t('profiles.addMapping')}
              </Button>
            </div>
            <div className="space-y-2">
              {editingProfile?.mappings.map((mapping, index) => (
                <div key={index} className="flex gap-2 items-start p-3 bg-nkz-surface-raised rounded-md border border-nkz-border">
                  <input type="text" placeholder={t('profiles.placeholderIncoming')} value={mapping.incoming_key}
                    className="flex-1 px-2 py-1 border border-nkz-border rounded text-sm bg-nkz-surface text-nkz-foreground"
                    onChange={(e) => handleMappingChange(editingProfile, index, 'incoming_key', e.target.value)} />
                  <span className="py-1 text-nkz-muted">→</span>
                  <input type="text" placeholder={t('profiles.placeholderTarget')} value={mapping.target_attribute}
                    className="flex-1 px-2 py-1 border border-nkz-border rounded text-sm bg-nkz-surface text-nkz-foreground"
                    onChange={(e) => handleMappingChange(editingProfile, index, 'target_attribute', e.target.value)} />
                  <select value={mapping.type}
                    className="px-2 py-1 border border-nkz-border rounded text-sm bg-nkz-surface text-nkz-foreground"
                    onChange={(e) => handleMappingChange(editingProfile, index, 'type', e.target.value)}>
                    <option value="Number">{t('profiles.typeNumber')}</option>
                    <option value="Text">{t('profiles.typeText')}</option>
                    <option value="Boolean">{t('profiles.typeBoolean')}</option>
                  </select>
                  <input type="text" placeholder={t('profiles.placeholderTransform')} value={mapping.transformation || ''}
                    className="flex-1 px-2 py-1 border border-nkz-border rounded text-sm bg-nkz-surface text-nkz-foreground"
                    onChange={(e) => handleMappingChange(editingProfile, index, 'transformation', e.target.value)} />
                  <button onClick={() => handleRemoveMapping(editingProfile, index)}
                    className="p-1 text-nkz-danger hover:bg-nkz-danger-soft rounded" type="button">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-2 justify-end">
            <Button variant="ghost" size="sm" onClick={() => { setEditingProfile(null); setIsCreating(false); }}>
              <X className="w-4 h-4 mr-1" />{t('profiles.cancel')}
            </Button>
            <Button variant="primary" size="sm" onClick={() => handleSave(editingProfile!)}>
              <Save className="w-4 h-4 mr-1" />{t('profiles.save')}
            </Button>
          </div>
        </Card>
      )}

      <div className="space-y-3">
        {profiles.length === 0 ? (
          <Card padding="lg" className="text-center text-nkz-muted">{t('profiles.empty')}</Card>
        ) : (
          profiles.map((profile) => (
            <Card key={profile.id} padding="md" className="hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div className="min-w-0">
                  <h3 className="text-base font-semibold text-nkz-foreground">{profile.name}</h3>
                  <p className="text-sm text-nkz-muted mt-0.5">
                    {[profile.manufacturer, profile.model].filter(Boolean).join(' ')}
                    {(profile.manufacturer || profile.model) ? ' → ' : ''}{profile.sdm_entity_type}
                  </p>
                  {profile.description && (
                    <p className="text-sm text-nkz-muted mt-1 truncate max-w-md">{profile.description}</p>
                  )}
                  <p className="text-xs text-nkz-muted mt-1">
                    {t('profiles.mappingsCount', { count: profile.mappings?.length || 0 })}
                  </p>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <Button variant="ghost" size="sm" onClick={() => setEditingProfile(profile)}>
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(profile.id!)}>
                    <Trash2 className="w-4 h-4 text-nkz-danger" />
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default DeviceProfileManager;
