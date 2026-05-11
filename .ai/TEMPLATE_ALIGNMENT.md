# Template Alignment Report: Connectivity vs module-template

Comparison of `nekazari-module-connectivity` against `nekazari-public/module-template` and EXTERNAL_MODULE_INSTALLATION requirements.

**Date:** 2026-02-09

## Summary

| Area | Status | Notes |
|------|--------|-------|
| manifest.json | ✅ | Connectivity has it; template may not |
| src/slots/index.ts | ✅ | Connectivity has it; template may not |
| imagePullSecrets | ✅ | Both frontend and backend now have ghcr-secret |
| nginx.conf | ✅ | Correct /modules/connectivity/ rewrite |
| vite.config.ts | ✅ | Aligned (viewerSlots, exposes) |
| K8s manifests | ✅ | Placeholders replaced, imagePullSecrets added |
| env.example | ✅ | Includes MONGODB_URL for backend |

## module-template Gaps (Platform)

The `nekazari-public/module-template` has structural gaps that would prevent building:

1. **manifest.json** — Dockerfile copies it but the file does not exist in `module-template/`. The template under `templates/nekazari-module-template/` has a manifest but uses different placeholders (hello-world).

2. **src/slots/index.ts** — `App.tsx` exports `viewerSlots` from `./slots/index` but `module-template` does not have `src/slots/index.ts`. Build would fail.

3. **init-module.sh** — Requires both `manifest.json` and `vite.config.ts`. If run from module-template, it would fail because manifest.json is missing.

**Recommendation:** Add `manifest.json` and `src/slots/index.ts` to `nekazari-public/module-template` so new modules can be initialized correctly.

## Connectivity-Specific Adjustments Made

1. **k8s/frontend-deployment.yaml** — Added `imagePullSecrets: ghcr-secret` (required for GHCR by EXTERNAL_MODULE_INSTALLATION).

2. **env.example** — Added `MONGODB_URL` for local backend development.

## Alignment Checklist (EXTERNAL_MODULE_INSTALLATION)

- [x] k8s/backend-deployment.yaml with imagePullSecrets
- [x] k8s/frontend-deployment.yaml with imagePullSecrets
- [x] k8s/registration.sql
- [x] frontend/nginx.conf with /modules/connectivity/ rewrite
- [x] frontend/Dockerfile (context: ., file: frontend/Dockerfile)
- [x] manifest.json
- [x] vite.config.ts with shared React singleton
- [x] tailwind.config.js (preflight/prefix per guide — verify if needed)
- [x] Documentation (README.md, SETUP.md)

## Minor Notes

- **api.ts / ExampleSlot** — `useModuleApi()` uses `/data` endpoints that the backend does not implement. DeviceProfileManager correctly uses `/profiles/` via direct fetch. ExampleSlot is a demo slot; consider updating api.ts to add profile methods or documenting that ExampleSlot is for demo only.
- **package-lock.json** — Frontend Dockerfile uses `npm ci`; ensure `package-lock.json` exists or use `npm install` in the Dockerfile.
