"""
Connectivity Backend — ModuleApp entry point.

Uses nkz-platform-sdk for:
- Gateway-based auth (X-Tenant-ID, X-User-ID, X-User-Roles headers)
- Orion-LD typed client with automatic FIWARE header injection
- JSON structured logging, CORS, /health, /ready
"""
from nkz_platform_sdk import ModuleApp
from app.config import get_settings

settings = get_settings()

app = ModuleApp(
    id="connectivity",
    description="IoT Device Connectivity Manager — Nekazari Platform",
    version=settings.app_version,
)

# Include Device Profiles routes
from app.device_profiles import router as profiles_router
app.include_router(profiles_router, prefix=settings.api_prefix)
