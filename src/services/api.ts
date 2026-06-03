/**
 * API Client for Connectivity Module.
 * Uses NKZClient from @nekazari/sdk for automatic auth headers and tenant context.
 */

import { NKZClient, useAuth } from '@nekazari/sdk';

export function useModuleApi() {
  const { getToken, tenantId } = useAuth();

  const client = new NKZClient({
    baseUrl: '/api/connectivity',
    getToken,
    getTenantId: () => tenantId,
  });

  return {
    // Profile endpoints
    listProfiles: (params?: { sdm_entity_type?: string; offset?: number; limit?: number }) =>
      client.get('/profiles/', params),
    getProfile: (id: string) => client.get(`/profiles/${encodeURIComponent(id)}`),
    createProfile: (profile: Record<string, unknown>) => client.post('/profiles/', profile),
    updateProfile: (id: string, profile: Record<string, unknown>) =>
      client.put(`/profiles/${encodeURIComponent(id)}`, profile),
    deleteProfile: (id: string) => client.delete(`/profiles/${encodeURIComponent(id)}`),
    getSdmSchemas: () => client.get('/profiles/schemas/sdm-types'),
  };
}
