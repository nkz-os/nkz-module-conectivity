"""
Connectivity Module — Device Profiles API (NGSI-LD backend).

Uses OrionClient (nkz-platform-sdk) for all storage.
ZERO direct DB writes — Orion-LD is the sole source of truth.

Auth is handled by api-gateway headers via require_auth().
No JWT validation in the module — the gateway already validated.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from nkz_platform_sdk import AuthContext, require_auth

from app.orion_profiles import (
    PROFILE_ENTITY_TYPE,
    build_device_profile_entity,
    build_profile_update_attrs,
    profile_entity_to_response,
)

router = APIRouter(prefix="/profiles", tags=["Device Profiles"])


# =============================================================================
# Pydantic Models
# =============================================================================


class MappingEntry(BaseModel):
    """Single attribute mapping from incoming key to NGSI-LD attribute."""

    incoming_key: str = Field(..., description="Key from incoming device data")
    target_attribute: str = Field(..., description="Target NGSI-LD attribute name")
    type: str = Field(
        default="Number", description="Data type (Number, Text, Boolean)"
    )
    transformation: Optional[str] = Field(
        None, description="JEXL expression (e.g. 'val * 100')"
    )
    unit: Optional[str] = Field(None, description="Unit of measurement")


class DeviceProfileCreate(BaseModel):
    """Payload for creating a new device profile."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    manufacturer: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=200)
    sdm_entity_type: str = Field(..., min_length=1)
    mappings: list[MappingEntry] = Field(default_factory=list)
    is_public: bool = Field(default=False)


class DeviceProfileUpdate(BaseModel):
    """Payload for updating an existing profile (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    manufacturer: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=200)
    sdm_entity_type: Optional[str] = Field(None, min_length=1)
    mappings: Optional[list[MappingEntry]] = None
    is_public: Optional[bool] = None


class DeviceProfileResponse(BaseModel):
    """API response for a single device profile."""

    id: str
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    sdm_entity_type: str
    mappings: list[MappingEntry] = []
    is_public: bool = False
    tenant_id: str = ""
    created_by: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class DeviceProfileListResponse(BaseModel):
    """Paginated list response for device profiles."""

    items: list[DeviceProfileResponse]
    total: int
    offset: int
    limit: int


# =============================================================================
# Quota enforcement (fail-open per AGENTS.md)
# =============================================================================


async def _check_profile_quota(ctx: AuthContext, request: Request) -> None:
    """
    Check tenant has not exceeded profile creation limit.

    Design: fail-open. If tier_quotas is unavailable or Orion-LD is unreachable,
    the operation proceeds. Only enforced when all dependencies are available.
    """
    try:
        from services.common.tier_quotas import quotas_for_tier
    except ImportError:
        return  # tier_quotas not available in this deployment — fail open

    try:
        orion = request.app.orion(ctx)

        # Read tenant tier from Orion-LD
        try:
            tenant_entity = await orion.get_entity(
                f"urn:ngsi-ld:Tenant:{ctx.tenant_id}"
            )
            tier = (
                (tenant_entity.get("tier", {}) or {}).get("value")
                or (tenant_entity.get("planName", {}) or {}).get("value")
                or "basic"
            )
        except Exception:
            tier = "basic"

        quotas = quotas_for_tier(tier)
        max_entities = quotas.get("max_entities_total")

        if max_entities is not None:
            existing = await orion.query_entities(
                type=PROFILE_ENTITY_TYPE,
                q=f'refTenant=="urn:ngsi-ld:Tenant:{ctx.tenant_id}"',
                limit=0,
                attrs="id",
            )
            if len(existing) >= max_entities:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        f"Profile limit reached for tier '{tier}' "
                        f"({max_entities} max). Upgrade your plan."
                    ),
                )
    except HTTPException:
        raise
    except Exception:
        pass  # fail open — allow creation if quota check fails


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/", response_model=DeviceProfileListResponse)
async def list_profiles(
    request: Request,
    ctx: AuthContext = require_auth(),
    sdm_entity_type: Optional[str] = Query(None, description="Filter by SDM entity type"),
    include_public: bool = Query(True, description="Include public template profiles"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List device profiles for the current tenant, with pagination."""
    orion = request.app.orion(ctx)

    # Build NGSI-LD query
    q_parts = []
    if include_public:
        q_parts.append(
            f'(refTenant=="urn:ngsi-ld:Tenant:{ctx.tenant_id}"|isPublic==true)'
        )
    else:
        q_parts.append(f'refTenant=="urn:ngsi-ld:Tenant:{ctx.tenant_id}"')

    if sdm_entity_type:
        q_parts.append(f'sdmEntityType=="{sdm_entity_type}"')

    q = ";".join(q_parts) if q_parts else None

    entities = await orion.query_entities(
        type=PROFILE_ENTITY_TYPE,
        q=q,
        limit=limit,
        offset=offset,
    )

    items = [DeviceProfileResponse(**profile_entity_to_response(e)) for e in entities]

    return DeviceProfileListResponse(
        items=items,
        total=len(items),
        offset=offset,
        limit=limit,
    )


@router.post("/", response_model=DeviceProfileResponse, status_code=201)
async def create_profile(
    profile: DeviceProfileCreate,
    request: Request,
    ctx: AuthContext = require_auth(),
):
    """Create a new device profile for the current tenant."""
    orion = request.app.orion(ctx)

    # Enforce tier quotas (fail-open)
    await _check_profile_quota(ctx, request)

    entity = build_device_profile_entity(
        tenant_id=ctx.tenant_id,
        name=profile.name,
        sdm_entity_type=profile.sdm_entity_type,
        mappings=[m.model_dump() for m in profile.mappings],
        description=profile.description,
        manufacturer=profile.manufacturer,
        model=profile.model,
        is_public=profile.is_public,
        created_by=ctx.user_id,
    )

    result = await orion.create_entity(entity)
    entity_id = result.get("id") or entity["id"]

    # Fetch the created entity for full response
    created = await orion.get_entity(entity_id)
    return DeviceProfileResponse(**profile_entity_to_response(created))


@router.get("/{profile_id}", response_model=DeviceProfileResponse)
async def get_profile(
    profile_id: str,
    request: Request,
    ctx: AuthContext = require_auth(),
):
    """Get a specific device profile by ID (URN or short ID)."""
    orion = request.app.orion(ctx)

    # Normalize ID: accept both "urn:ngsi-ld:DeviceProfile:abc" and "abc"
    if not profile_id.startswith("urn:"):
        profile_id = f"urn:ngsi-ld:DeviceProfile:{profile_id}"

    try:
        entity = await orion.get_entity(profile_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Profile not found")

    if entity.get("type") != PROFILE_ENTITY_TYPE:
        raise HTTPException(status_code=404, detail="Not a DeviceProfile entity")

    # Access control: tenant-owned or public
    resp = profile_entity_to_response(entity)
    if resp["tenant_id"] != ctx.tenant_id and not resp["is_public"]:
        raise HTTPException(status_code=404, detail="Profile not found")

    return DeviceProfileResponse(**resp)


@router.put("/{profile_id}", response_model=DeviceProfileResponse)
async def update_profile(
    profile_id: str,
    updated: DeviceProfileUpdate,
    request: Request,
    ctx: AuthContext = require_auth(),
):
    """Update a device profile (tenant ownership required)."""
    orion = request.app.orion(ctx)

    if not profile_id.startswith("urn:"):
        profile_id = f"urn:ngsi-ld:DeviceProfile:{profile_id}"

    try:
        entity = await orion.get_entity(profile_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Profile not found")

    if entity.get("type") != PROFILE_ENTITY_TYPE:
        raise HTTPException(status_code=404, detail="Not a DeviceProfile entity")

    # Ownership check
    resp = profile_entity_to_response(entity)
    if resp["tenant_id"] != ctx.tenant_id:
        raise HTTPException(status_code=403, detail="Not owned by your tenant")

    # Build update attrs (only provided fields)
    attrs = build_profile_update_attrs(
        name=updated.name,
        description=updated.description,
        manufacturer=updated.manufacturer,
        model=updated.model,
        sdm_entity_type=updated.sdm_entity_type,
        mappings=(
            [m.model_dump() for m in updated.mappings]
            if updated.mappings is not None
            else None
        ),
        is_public=updated.is_public,
    )

    await orion.update_entity_attrs(profile_id, attrs)

    # Fetch and return updated entity
    updated_entity = await orion.get_entity(profile_id)
    return DeviceProfileResponse(**profile_entity_to_response(updated_entity))


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: str,
    request: Request,
    ctx: AuthContext = require_auth(),
):
    """Delete a device profile (tenant ownership required)."""
    orion = request.app.orion(ctx)

    if not profile_id.startswith("urn:"):
        profile_id = f"urn:ngsi-ld:DeviceProfile:{profile_id}"

    try:
        entity = await orion.get_entity(profile_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Profile not found")

    if entity.get("type") != PROFILE_ENTITY_TYPE:
        raise HTTPException(status_code=404, detail="Not a DeviceProfile entity")

    resp = profile_entity_to_response(entity)
    if resp["tenant_id"] != ctx.tenant_id:
        raise HTTPException(status_code=403, detail="Not owned by your tenant")

    await orion.delete_entity(profile_id)


@router.get("/schemas/sdm-types")
async def get_sdm_schemas(request: Request, ctx: AuthContext = require_auth()):
    """
    Get available SDM entity types for mapping.

    Returns known IoT-related types. In the future this could dynamically
    proxy Orion-LD to discover registered entity types.
    """
    return {
        "types": {
            "AgriSensor": [
                "temperature",
                "humidity",
                "soilMoisture",
                "batteryLevel",
                "rssi",
            ],
            "WeatherStation": [
                "temperature",
                "humidity",
                "pressure",
                "windSpeed",
                "windDirection",
                "precipitation",
            ],
            "Device": [
                "value",
                "batteryLevel",
                "rssi",
                "status",
            ],
            "AgriParcel": [
                "area",
                "crop",
                "soilType",
                "irrigation",
            ],
        }
    }
