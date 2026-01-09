import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';

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

interface DeviceProfileManagerProps {
    apiBaseUrl: string;
}

export const DeviceProfileManager: React.FC<DeviceProfileManagerProps> = ({ apiBaseUrl }) => {
    const [profiles, setProfiles] = useState<DeviceProfile[]>([]);
    const [editingProfile, setEditingProfile] = useState<DeviceProfile | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadProfiles();
    }, []);

    const loadProfiles = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${apiBaseUrl}/profiles/`);
            const data = await response.json();
            setProfiles(data);
        } catch (error) {
            console.error('Error loading profiles:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (profile: DeviceProfile) => {
        try {
            const url = profile.id
                ? `${apiBaseUrl}/profiles/${profile.id}`
                : `${apiBaseUrl}/profiles/`;

            const method = profile.id ? 'PUT' : 'POST';

            await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profile),
            });

            await loadProfiles();
            setEditingProfile(null);
            setIsCreating(false);
        } catch (error) {
            console.error('Error saving profile:', error);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('¿Eliminar este perfil?')) return;

        try {
            await fetch(`${apiBaseUrl}/profiles/${id}`, { method: 'DELETE' });
            await loadProfiles();
        } catch (error) {
            console.error('Error deleting profile:', error);
        }
    };

    const handleAddMapping = (profile: DeviceProfile) => {
        const newMapping: MappingEntry = {
            incoming_key: '',
            target_attribute: '',
            type: 'Number',
        };
        setEditingProfile({
            ...profile,
            mappings: [...profile.mappings, newMapping],
        });
    };

    const handleRemoveMapping = (profile: DeviceProfile, index: number) => {
        setEditingProfile({
            ...profile,
            mappings: profile.mappings.filter((_, i) => i !== index),
        });
    };

    const handleMappingChange = (
        profile: DeviceProfile,
        index: number,
        field: keyof MappingEntry,
        value: string
    ) => {
        const updatedMappings = [...profile.mappings];
        updatedMappings[index] = { ...updatedMappings[index], [field]: value };
        setEditingProfile({ ...profile, mappings: updatedMappings });
    };

    if (loading) {
        return <div className="p-8 text-center">Cargando...</div>;
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Perfiles de Dispositivo</h1>
                <button
                    onClick={() => {
                        setIsCreating(true);
                        setEditingProfile({
                            name: '',
                            sdm_entity_type: 'AgriSensor',
                            mappings: [],
                            is_public: false,
                        });
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                    <Plus className="w-5 h-5" />
                    Nuevo Perfil
                </button>
            </div>

            {(isCreating || editingProfile) && (
                <div className="mb-6 p-6 border-2 border-green-500 rounded-xl bg-green-50">
                    <h2 className="text-xl font-semibold mb-4">
                        {isCreating ? 'Crear Perfil' : 'Editar Perfil'}
                    </h2>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Nombre *</label>
                            <input
                                type="text"
                                value={editingProfile?.name || ''}
                                onChange={(e) =>
                                    setEditingProfile({ ...editingProfile!, name: e.target.value })
                                }
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Tipo SDM *</label>
                            <select
                                value={editingProfile?.sdm_entity_type || 'AgriSensor'}
                                onChange={(e) =>
                                    setEditingProfile({
                                        ...editingProfile!,
                                        sdm_entity_type: e.target.value,
                                    })
                                }
                                className="w-full px-3 py-2 border rounded-lg"
                            >
                                <option value="AgriSensor">AgriSensor</option>
                                <option value="WeatherStation">WeatherStation</option>
                                <option value="Device">Device</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Fabricante</label>
                            <input
                                type="text"
                                value={editingProfile?.manufacturer || ''}
                                onChange={(e) =>
                                    setEditingProfile({
                                        ...editingProfile!,
                                        manufacturer: e.target.value,
                                    })
                                }
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Modelo</label>
                            <input
                                type="text"
                                value={editingProfile?.model || ''}
                                onChange={(e) =>
                                    setEditingProfile({ ...editingProfile!, model: e.target.value })
                                }
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                    </div>

                    <div className="mb-4">
                        <label className="block text-sm font-medium mb-1">Descripción</label>
                        <textarea
                            value={editingProfile?.description || ''}
                            onChange={(e) =>
                                setEditingProfile({
                                    ...editingProfile!,
                                    description: e.target.value,
                                })
                            }
                            className="w-full px-3 py-2 border rounded-lg"
                            rows={2}
                        />
                    </div>

                    <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                            <h3 className="font-semibold">Mapeos de Atributos</h3>
                            <button
                                onClick={() => handleAddMapping(editingProfile!)}
                                className="text-sm px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                + Añadir Mapeo
                            </button>
                        </div>

                        <div className="space-y-2">
                            {editingProfile?.mappings.map((mapping, index) => (
                                <div key={index} className="flex gap-2 items-start p-3 bg-white rounded-lg">
                                    <input
                                        type="text"
                                        placeholder="Clave entrante (ej: t)"
                                        value={mapping.incoming_key}
                                        onChange={(e) =>
                                            handleMappingChange(
                                                editingProfile,
                                                index,
                                                'incoming_key',
                                                e.target.value
                                            )
                                        }
                                        className="flex-1 px-2 py-1 border rounded text-sm"
                                    />
                                    <span className="py-1">→</span>
                                    <input
                                        type="text"
                                        placeholder="Atributo destino (ej: temperature)"
                                        value={mapping.target_attribute}
                                        onChange={(e) =>
                                            handleMappingChange(
                                                editingProfile,
                                                index,
                                                'target_attribute',
                                                e.target.value
                                            )
                                        }
                                        className="flex-1 px-2 py-1 border rounded text-sm"
                                    />
                                    <select
                                        value={mapping.type}
                                        onChange={(e) =>
                                            handleMappingChange(editingProfile, index, 'type', e.target.value)
                                        }
                                        className="px-2 py-1 border rounded text-sm"
                                    >
                                        <option value="Number">Number</option>
                                        <option value="Text">Text</option>
                                        <option value="Boolean">Boolean</option>
                                    </select>
                                    <input
                                        type="text"
                                        placeholder="Transformación (ej: val * 100)"
                                        value={mapping.transformation || ''}
                                        onChange={(e) =>
                                            handleMappingChange(
                                                editingProfile,
                                                index,
                                                'transformation',
                                                e.target.value
                                            )
                                        }
                                        className="flex-1 px-2 py-1 border rounded text-sm"
                                    />
                                    <button
                                        onClick={() => handleRemoveMapping(editingProfile, index)}
                                        className="p-1 text-red-500 hover:bg-red-50 rounded"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex gap-2 justify-end">
                        <button
                            onClick={() => {
                                setEditingProfile(null);
                                setIsCreating(false);
                            }}
                            className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50"
                        >
                            <X className="w-4 h-4" />
                            Cancelar
                        </button>
                        <button
                            onClick={() => handleSave(editingProfile!)}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                            <Save className="w-4 h-4" />
                            Guardar
                        </button>
                    </div>
                </div>
            )}

            <div className="grid gap-4">
                {profiles.map((profile) => (
                    <div key={profile.id} className="p-4 border rounded-lg hover:shadow-md transition">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <h3 className="text-lg font-semibold">{profile.name}</h3>
                                <p className="text-sm text-gray-600">
                                    {profile.manufacturer} {profile.model} → {profile.sdm_entity_type}
                                </p>
                                {profile.description && (
                                    <p className="text-sm text-gray-500 mt-1">{profile.description}</p>
                                )}
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setEditingProfile(profile)}
                                    className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                                >
                                    <Edit className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => handleDelete(profile.id!)}
                                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                        <div className="text-sm text-gray-500">
                            {profile.mappings.length} mapeos configurados
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
