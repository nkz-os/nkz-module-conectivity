-- =============================================================================
-- Connectivity Module Registration
-- =============================================================================
-- Entry point: remoteEntry.js (Module Federation 2.0 via @nekazari/module-builder)
-- Entity type: DeviceProfile (NGSI-LD custom entity)
-- =============================================================================

INSERT INTO marketplace_modules (
    id, name, display_name, description,
    remote_entry_url, scope, exposed_module, version,
    author, category, route_path, label,
    module_type, required_plan_type, pricing_tier,
    is_local, is_active, required_roles, metadata
) VALUES (
    'connectivity',
    'connectivity',
    'Connectivity',
    'IoT Device Connectivity Manager - Manage Device Profiles and configure data transformation for IoT sensors',
    '/modules/connectivity/remoteEntry.js',
    'connectivity',
    './Module',
    '1.1.0',
    'Nekazari Team',
    'iot',
    '/connectivity',
    'Connectivity',
    'ADDON_CORE',
    'free',
    'FREE',
    false,
    true,
    ARRAY['Farmer', 'TenantAdmin', 'PlatformAdmin'],
    '{"icon": "📡", "color": "#3B82F6", "features": ["Device Profile Management", "No-Code Data Mapping", "SDM Attribute Discovery", "JEXL Transformations", "Ingestion Monitoring"]}'::jsonb
) ON CONFLICT (id) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    remote_entry_url = EXCLUDED.remote_entry_url,
    scope = EXCLUDED.scope,
    exposed_module = EXCLUDED.exposed_module,
    category = EXCLUDED.category,
    route_path = EXCLUDED.route_path,
    module_type = EXCLUDED.module_type,
    required_plan_type = EXCLUDED.required_plan_type,
    pricing_tier = EXCLUDED.pricing_tier,
    version = EXCLUDED.version,
    metadata = EXCLUDED.metadata,
    is_active = true,
    updated_at = NOW();
