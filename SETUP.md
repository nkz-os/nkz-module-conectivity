# Connectivity Module — Setup & Deployment

Module-specific setup and deployment instructions. For platform-wide installation, see [EXTERNAL_MODULE_INSTALLATION](../nekazari-public/docs/modules/EXTERNAL_MODULE_INSTALLATION.md).

## Local Development

### 1. Environment

```bash
cp env.example .env.local
# Edit .env.local if needed (MONGODB_URL for backend, VITE_API_BASE_URL for frontend)
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
# Set MONGODB_URL or use local MongoDB
export MONGODB_URL=mongodb://localhost:27017/
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
npm install
npm run dev
```

Frontend runs at http://localhost:5003. API calls to `/api` are proxied to production (`nkz.artotxiki.com`) by default. To use the local backend, set `VITE_API_BASE_URL=http://localhost:8000/api/connectivity` in `.env.local`.

### 4. MongoDB (Local)

For local backend, MongoDB must be running. The backend uses `nekazari.device_profiles`.

```bash
# Using Docker
docker run -d -p 27017:27017 mongo:7
```

## Build

### Frontend

```bash
npm run build
```

### Docker Images

```bash
# Frontend (from module root)
docker build -f frontend/Dockerfile -t ghcr.io/nkz-os/connectivity-frontend:v1.0.0 .

# Backend
docker build -f backend/Dockerfile -t ghcr.io/nkz-os/connectivity-backend:v1.0.0 ./backend
```

## Deployment (Production)

### 1. Push Images to GHCR

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker push ghcr.io/nkz-os/connectivity-frontend:v1.0.0
docker push ghcr.io/nkz-os/connectivity-backend:v1.0.0
```

### 2. Apply Kubernetes Manifests

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### 3. Update Ingress (nekazari-public)

Add routes in `k8s/core/networking/ingress.yaml` (before generic `/modules`):

```yaml
- path: /api/connectivity
  pathType: Prefix
  backend:
    service:
      name: connectivity-api-service
      port:
        number: 8000

- path: /modules/connectivity
  pathType: Prefix
  backend:
    service:
      name: connectivity-frontend-service
      port:
        number: 80
```

Apply:

```bash
cd nekazari-public
kubectl apply -f k8s/core/networking/ingress.yaml
```

### 4. Register Module

```bash
kubectl exec -it -n nekazari <postgresql-pod> -- psql -U nekazari -d nekazari -f - < k8s/registration.sql
```

Or from inside a pod with DB access:

```bash
psql $DATABASE_URL -f k8s/registration.sql
```

### 5. Verify

```bash
# API health
curl https://nkz.artotxiki.com/api/connectivity/health

# Frontend remoteEntry.js
curl -I https://nekazari.artotxiki.com/modules/connectivity/assets/remoteEntry.js
# Should return 200 and Content-Type: application/javascript
```

## Required Secrets

| Secret         | Keys                    | Purpose                |
|----------------|-------------------------|------------------------|
| ghcr-secret    | -                       | Pull images from GHCR  |
| mongodb-secret | root-username, root-password | MongoDB auth     |
| module-secrets | management-key (optional) | Service-to-service auth |

## Rollback

```bash
# Remove registration
kubectl exec -it -n nekazari <postgresql-pod> -- psql -U nekazari -d nekazari -c \
  "DELETE FROM marketplace_modules WHERE id = 'connectivity';"

# Remove Ingress routes (edit nekazari-public k8s)
# Remove deployments
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/frontend-deployment.yaml
```
