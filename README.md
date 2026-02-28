# Nekazari Module: Connectivity

**IoT Device Connectivity Manager** — Manages Device Profiles and configures data transformation from raw IoT sensor payloads to NGSI-LD/SDM compliant attributes in the Nekazari Platform.

## Overview

Connectivity is an external addon module for Nekazari that enables tenants to:

- **Create and manage Device Profiles** — Templates that define how raw IoT data maps to NGSI-LD entities
- **Configure attribute mappings** — Map incoming keys (e.g., `t`, `h`) to target attributes (e.g., `temperature`, `humidity`)
- **Apply JEXL transformations** — Optional expressions (e.g., `val * 100`) for unit conversion or scaling
- **Support SDM entity types** — AgriSensor, WeatherStation, Device (FIWARE Smart Data Models)

The module sits between IoT telemetry ingestion (MQTT, HTTP, telemetry-worker) and the FIWARE Context Broker (Orion-LD). Device profiles define the transformation rules used when ingesting raw data into NGSI-LD entities.

## Architecture

| Component     | Technology           | Description                              |
|--------------|----------------------|------------------------------------------|
| Frontend     | React 18 + TypeScript + Vite | DeviceProfileManager UI, slot integration |
| Backend      | Python + FastAPI     | REST API for device profile CRUD         |
| Persistence  | MongoDB              | Collection `device_profiles` in `nekazari` db |
| Auth         | Keycloak JWT         | Multi-tenant, RLS via `tenant_id`        |
| Deployment   | Kubernetes           | GHCR images, `nekazari` namespace        |

## Project Structure

```
nekazari-module-connectivity/
├── src/                          # Frontend React application
│   ├── App.tsx                   # Main app (standalone + fallback)
│   ├── components/
│   │   ├── DeviceProfileManager.tsx  # Main UI for profile management
│   │   └── slots/
│   │       └── ExampleSlot.tsx       # Example slot widget for Unified Viewer
│   ├── slots/index.ts            # Slot registration (context-panel, etc.)
│   ├── services/api.ts           # SDK-based API client
│   └── hooks/useUIKit.tsx        # UI Kit access hook
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI application
│   │   ├── config.py             # Environment configuration
│   │   ├── device_profiles.py    # Device profile CRUD API
│   │   └── middleware/           # Keycloak JWT auth
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile                # Multi-stage build
│   └── nginx.conf                # CORS & /modules/connectivity/ rewrite
├── k8s/
│   ├── frontend-deployment.yaml
│   ├── backend-deployment.yaml
│   └── registration.sql          # marketplace_modules registration
├── manifest.json                 # Module metadata for platform
└── env.example                   # Environment template
```

## Quick Start

### Local Development

```bash
# Install frontend dependencies
npm install

# Start frontend dev server (port 5003)
npm run dev

# Backend (separate terminal)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Frontend: http://localhost:5003  
- Backend API: http://localhost:8000  
- API docs: http://localhost:8000/api/connectivity/docs  

### Environment

Copy `env.example` to `.env.local` and adjust as needed. For local dev, the frontend proxies `/api` to production (`nkz.artotxiki.com`) unless overridden.

## API Reference

### Device Profiles

| Method | Endpoint                  | Description                 |
|--------|---------------------------|-----------------------------|
| GET    | `/api/connectivity/profiles/` | List profiles (tenant + public) |
| POST   | `/api/connectivity/profiles/` | Create profile              |
| GET    | `/api/connectivity/profiles/{id}` | Get profile                 |
| PUT    | `/api/connectivity/profiles/{id}` | Update profile (tenant only) |
| DELETE | `/api/connectivity/profiles/{id}` | Delete profile (tenant only) |
| GET    | `/api/connectivity/profiles/schemas/sdm-types` | SDM entity types and attributes |

### Profile Model

- `name`, `description`, `manufacturer`, `model`
- `sdm_entity_type` — Target SDM entity (AgriSensor, WeatherStation, Device)
- `mappings` — List of `{ incoming_key, target_attribute, type, transformation?, unit? }`
- `is_public` — Public template (read-only for other tenants)

## Slot Integration

The module registers a slot widget in the Unified Viewer:

- **context-panel** — ExampleSlot (demo with viewer context, API integration)

See `src/slots/index.ts` for registration and `src/components/slots/ExampleSlot.tsx` for the implementation.

## Deployment

### Prerequisites

- Access to Kubernetes cluster (namespace `nekazari`)
- GHCR credentials as `ghcr-secret` in namespace
- `kubectl` configured
- MongoDB secret (`mongodb-secret`) for backend
- Ingress routes for `/api/connectivity` and `/modules/connectivity`

### Build and Push Images

```bash
# Frontend
docker build -f frontend/Dockerfile -t ghcr.io/k8-benetis/connectivity-frontend:v1.0.0 .
docker push ghcr.io/k8-benetis/connectivity-frontend:v1.0.0

# Backend
docker build -f backend/Dockerfile -t ghcr.io/k8-benetis/connectivity-backend:v1.0.0 ./backend
docker push ghcr.io/k8-benetis/connectivity-backend:v1.0.0
```

### Apply Kubernetes Manifests

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Ingress Routes

Add to `nekazari-public` Ingress (`k8s/core/networking/ingress.yaml`):

```yaml
# API route
- path: /api/connectivity
  pathType: Prefix
  backend:
    service:
      name: connectivity-api-service
      port:
        number: 8000

# Frontend (MUST come before generic /modules)
- path: /modules/connectivity
  pathType: Prefix
  backend:
    service:
      name: connectivity-frontend-service
      port:
        number: 80
```

### Register Module

```bash
kubectl exec -it -n nekazari <postgres-pod> -- psql -U nekazari -d nekazari -f - < k8s/registration.sql
```

### Verify

```bash
curl https://nkz.artotxiki.com/api/connectivity/health
curl -I https://nekazari.artotxiki.com/modules/connectivity/assets/remoteEntry.js
```

See [EXTERNAL_MODULE_INSTALLATION](../nekazari-public/docs/modules/EXTERNAL_MODULE_INSTALLATION.md) for full platform installation guide.

## Module Metadata

| Field         | Value                             |
|---------------|-----------------------------------|
| ID            | `connectivity`                    |
| Route         | `/connectivity`                   |
| Category      | `iot`                             |
| Module Type   | `ADDON_CORE`                      |
| Required Roles| Farmer, TenantAdmin, PlatformAdmin |

## Security

- **Public repo** — No hardcoded secrets, paths, or emails
- All credentials via environment variables and Kubernetes secrets
- JWT validation via Keycloak JWKS; tenant isolation via `tenant_id`

## License

AGPL-3.0 (same as Nekazari Platform)
