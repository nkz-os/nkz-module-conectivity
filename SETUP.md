# Module Template Setup Guide

This guide will help you set up your new module from this template.

## Step 1: Copy Template

```bash
cp -r module-template my-module-name
cd my-module-name
```

## Step 2: Replace Placeholders

Use find-and-replace in your editor to replace:

- `connectivity` → Your module ID (lowercase, hyphens, e.g., `my-module`)
- `Connectivity` → Display name (e.g., `My Module`)
- `connectivity` → Module scope for Module Federation (e.g., `my_module`)
- `/connectivity` → Route path (e.g., `/my-module`)
- `k8-benetis` → Your GitHub organization (e.g., `k8-benetis`)

### Files to Update

1. **package.json**
   - `name`: `connectivity-module`
   - `description`: Update description

2. **vite.config.ts**
   - `name`: `connectivity` (federation name)
   - `exposes`: Update component paths if needed

3. **manifest.json**
   - All `connectivity`, `Connectivity`, `/connectivity`, `connectivity`
   - Update author, description, features

4. **k8s/frontend-deployment.yaml**
   - `name`: `connectivity-frontend`
   - `image`: `ghcr.io/k8-benetis/connectivity-frontend:v1.0.0`
   - Service name: `connectivity-frontend-service`

5. **k8s/registration.sql**
   - All placeholders

6. **frontend/nginx.conf**
   - `location ~ ^/modules/connectivity/`

7. **src/App.tsx**
   - `Connectivity` in title and content

8. **src/slots/index.ts**
   - Comments mentioning `Connectivity`

9. **src/services/api.ts**
   - `baseUrl`: `/api/connectivity`
   - Comments mentioning `Connectivity`

## Step 3: Install Dependencies

```bash
npm install
```

## Step 4: Update Slot Components

1. Edit `src/components/slots/ExampleSlot.tsx` or create new slot components
2. Register them in `src/slots/index.ts`
3. Export them in `vite.config.ts` under `exposes`

## Step 5: Update API Client

Edit `src/services/api.ts` with your actual API endpoints.

## Step 6: Test Locally

```bash
npm run dev
```

Visit `http://localhost:5003` to see your module.

## Step 7: Build

```bash
npm run build
```

## Step 8: Docker Build

```bash
docker build -f frontend/Dockerfile -t ghcr.io/k8-benetis/connectivity-frontend:v1.0.0 .
docker push ghcr.io/k8-benetis/connectivity-frontend:v1.0.0
```

## Step 9: Deploy

1. Update `k8s/frontend-deployment.yaml` with your image
2. Apply deployment:
   ```bash
   kubectl apply -f k8s/frontend-deployment.yaml
   ```
3. Register module:
   ```bash
   kubectl exec -it <postgres-pod> -n nekazari -- psql -U nekazari -d nekazari -f /path/to/k8s/registration.sql
   ```
4. Update Ingress in `nekazari-public`:
   ```yaml
   - path: /modules/connectivity
     backend:
       service:
         name: connectivity-frontend-service
   ```

## Next Steps

- Read the main `README.md` for detailed documentation
- Check examples in `src/components/slots/ExampleSlot.tsx`
- Review SDK documentation for available hooks and APIs
- Follow best practices from Module Development Guide

