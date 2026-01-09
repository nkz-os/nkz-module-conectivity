# Nekazari Module Template

A production-ready template for creating external modules/addons for the Nekazari Platform. Build modules that integrate seamlessly with the unified viewer via Module Federation, complete with backend API, CI/CD, and Kubernetes deployment.

## Quick Start

### Option A: Using Init Script (Recommended)

```bash
cp -r module-template my-module-name
cd my-module-name
chmod +x scripts/init-module.sh
./scripts/init-module.sh
```

The script will interactively prompt for:
- Module name, display name, scope, route
- GitHub organization
- Author information

### Option B: Manual Setup

1. **Copy this template**:
   ```bash
   cp -r module-template my-module-name
   cd my-module-name
   ```

2. **Replace placeholders** (find & replace in your editor):
   - `connectivity` → Your module name (e.g., `my-module`)
   - `Connectivity` → Display name (e.g., `My Module`)
   - `connectivity` → Module Federation scope (e.g., `my_module`)
   - `/connectivity` → Route path (e.g., `/my-module`)
   - `k8-benetis` → GitHub organization (e.g., `k8-benetis`)

3. **Install dependencies**:
   ```bash
   npm install
   cd backend && pip install -r requirements.txt
   ```

4. **Start development**:
   ```bash
   npm run dev          # Frontend at http://localhost:5003
   cd backend && uvicorn app.main:app --reload  # Backend at http://localhost:8000
   ```

## Project Structure

```
module-template/
├── src/                          # Frontend React application
│   ├── App.tsx                   # Main app (standalone mode)
│   ├── components/slots/         # Unified Viewer slot components
│   │   └── ExampleSlot.tsx       # Example with API integration
│   ├── services/api.ts           # SDK-based API client
│   ├── hooks/useUIKit.tsx        # UI Kit access hook
│   └── slots/index.ts            # Slot registration
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Environment configuration
│   │   ├── api/__init__.py      # CRUD routes with auth
│   │   └── middleware/          # Keycloak JWT middleware
│   ├── tests/                   # Pytest tests
│   ├── Dockerfile               # Backend container
│   └── requirements.txt         # Python dependencies
├── frontend/                     # Frontend Docker config
│   ├── Dockerfile               # Multi-stage build
│   └── nginx.conf               # CORS & Module Federation paths
├── k8s/                          # Kubernetes manifests
│   ├── frontend-deployment.yaml # Frontend service
│   ├── backend-deployment.yaml  # Backend API service
│   └── registration.sql         # Database registration
├── .github/workflows/            # CI/CD
│   └── build-push.yml           # Build & push to GHCR
├── scripts/
│   └── init-module.sh           # Module initialization script
├── vite.config.ts               # Module Federation config
├── manifest.json                # Module metadata
├── docker-compose.yml           # Local development
└── env.example                  # Environment template
```

## Key Concepts

### Module Federation

The template uses **Module Federation** to integrate with the Nekazari host:

- **App Component**: Standalone application (fallback mode)
- **Viewer Slots**: Components that integrate into the unified viewer
- **Shared Dependencies**: React, ReactDOM, UI Kit, SDK

### Slots System

Slots are integration points in the unified viewer:

| Slot | Location | Use Case |
|------|----------|----------|
| `layer-toggle` | Layer manager | Toggle layers/data sources |
| `context-panel` | Right panel | Entity details, properties |
| `bottom-panel` | Bottom panel | Charts, timelines |
| `entity-tree` | Left panel | Entity hierarchy |

See `src/slots/index.ts` for registration.

### SDK Integration

The module uses `@nekazari/sdk` for:

- **`useAuth()`**: Authentication context (user, token, roles)
- **`useViewer()`**: Viewer state (selected entity, layers, date)
- **`NKZClient`**: HTTP client with auth headers
- **`useUIKit()`**: Platform UI components (Card, Button)

## Backend Development

The template includes a FastAPI backend with:

### Authentication Middleware

```python
from app.middleware import get_current_user, require_roles, get_tenant_id

@router.get("/data")
async def get_data(
    user: TokenPayload = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    return {"user": user.email, "tenant": tenant_id}

@router.get("/admin")
async def admin_only(
    user: TokenPayload = Depends(require_roles("TenantAdmin", "PlatformAdmin")),
):
    return {"admin": user.email}
```

### Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## CI/CD with GitHub Actions

The template includes `.github/workflows/build-push.yml`:

- **On push to main**: Builds and pushes images with `main` tag
- **On tag (v**)**: Builds and pushes versioned images
- **On PR**: Runs tests only

### Triggering a Release

```bash
git tag v1.0.0
git push origin v1.0.0
```

Images will be pushed to:
- `ghcr.io/k8-benetis/REPO/connectivity-frontend:v1.0.0`
- `ghcr.io/k8-benetis/REPO/connectivity-backend:v1.0.0`

## Docker Development

### Using Docker Compose

```bash
# Start all services
docker-compose up

# Or build and start in background
docker-compose up -d --build
```

### Manual Docker Build

```bash
# Frontend
docker build -f frontend/Dockerfile -t connectivity-frontend:dev .

# Backend
docker build -f backend/Dockerfile -t connectivity-backend:dev ./backend
```

## Deployment

### 1. Build and Push Images

Either via CI/CD (push tag) or manually:

```bash
docker build -f frontend/Dockerfile -t ghcr.io/k8-benetis/connectivity-frontend:v1.0.0 .
docker push ghcr.io/k8-benetis/connectivity-frontend:v1.0.0

docker build -f backend/Dockerfile -t ghcr.io/k8-benetis/connectivity-backend:v1.0.0 ./backend
docker push ghcr.io/k8-benetis/connectivity-backend:v1.0.0
```

### 2. Apply Kubernetes Manifests

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
```

### 3. Update Core Ingress

Add to `nekazari-public/k8s/core/networking/ingress.yaml`:

```yaml
# API route
- path: /api/connectivity
  pathType: Prefix
  backend:
    service:
      name: connectivity-api-service
      port:
        number: 8000

# Frontend route (MUST come before /modules)
- path: /modules/connectivity
  pathType: Prefix
  backend:
    service:
      name: connectivity-frontend-service
      port:
        number: 80
```

### 4. Register Module

```bash
kubectl exec -it <postgres-pod> -n nekazari -- psql -U nekazari -d nekazari -f /path/to/k8s/registration.sql
```

### 5. Verify

```bash
# Check remoteEntry.js
curl https://nekazari.artotxiki.com/modules/connectivity/assets/remoteEntry.js

# Check API health
curl https://nkz.artotxiki.com/api/connectivity/health
```

## Creating Slot Components

```typescript
// src/components/slots/MySlot.tsx
import React from 'react';
import { useViewer, useAuth } from '@nekazari/sdk';
import { useUIKit } from '@/hooks/useUIKit';

export const MySlot: React.FC = () => {
  const { Card, Button } = useUIKit();
  const { selectedEntityId } = useViewer();
  const { user } = useAuth();

  return (
    <Card padding="md">
      <h3>My Slot</h3>
      <p>Selected: {selectedEntityId}</p>
      <p>User: {user?.email}</p>
      <Button variant="primary">Action</Button>
    </Card>
  );
};
```

Register in `src/slots/index.ts`:

```typescript
import { MySlot } from '../components/slots/MySlot';

export const moduleSlots = {
  'context-panel': [
    {
      id: 'my-slot',
      component: 'MySlot',
      priority: 50,
      localComponent: MySlot,
    }
  ],
  // ...
};
```

## Troubleshooting

### Module not loading

- Check `remoteEntry.js` is accessible (should return JS, not HTML)
- Verify Ingress route order (`/modules/connectivity` before `/modules`)
- Check browser console for Module Federation errors

### API calls failing

- Verify authentication token is present
- Check Ingress API route exists
- Verify backend pod is running: `kubectl logs -l app=connectivity-backend`

### UI Kit not available

- `useUIKit()` returns fallback components until host initializes
- Check that host frontend version supports UI Kit globals

## Resources

- [External Module Installation Guide](../docs/modules/EXTERNAL_MODULE_INSTALLATION.md)
- [SDK Documentation](../packages/sdk/README.md)
- [Nekazari Platform Manual](../PLATFORM_MANUAL.md)

## License

AGPL-3.0 - Same as Nekazari Platform

## Support

- GitHub Issues: https://github.com/k8-benetis/nekazari-public
- Email: nekazari@artotxiki.com
