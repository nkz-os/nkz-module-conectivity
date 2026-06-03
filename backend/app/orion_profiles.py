"""
NGSI-LD DeviceProfile entity builder and helpers.

Entity type: DeviceProfile (custom — no exact match in Smart Data Models).
Per AGENTS.md: "If unavailable, use a generic entity or Property."

Each DeviceProfile entity belongs to a tenant via refTenant relationship.
"""

import json
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


PROFILE_ENTITY_TYPE = "DeviceProfile"


def build_device_profile_entity(
    tenant_id: str,
    name: str,
    sdm_entity_type: str,
    mappings: list[dict[str, Any]],
    description: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    is_public: bool = False,
    created_by: Optional[str] = None,
    profile_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Build a DeviceProfile NGSI-LD entity dict ready for OrionClient.create_entity().

    The @context is injected by OrionClient._ensure_context() automatically.
    """
    now = datetime.now(timezone.utc).isoformat()
    entity_id = profile_id or f"urn:ngsi-ld:DeviceProfile:{uuid4().hex[:12]}"

    entity: dict[str, Any] = {
        "id": entity_id,
        "type": PROFILE_ENTITY_TYPE,
        "name": {"type": "Property", "value": name},
        "sdmEntityType": {"type": "Property", "value": sdm_entity_type},
        "mappings": {"type": "Property", "value": mappings},
        "isPublic": {"type": "Property", "value": is_public},
        "createdAt": {"type": "Property", "value": now},
        "updatedAt": {"type": "Property", "value": now},
        "refTenant": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:Tenant:{tenant_id}",
        },
    }

    if description:
        entity["description"] = {"type": "Property", "value": description}
    if manufacturer:
        entity["manufacturer"] = {"type": "Property", "value": manufacturer}
    if model:
        entity["model"] = {"type": "Property", "value": model}
    if created_by:
        entity["createdBy"] = {"type": "Property", "value": created_by}

    return entity


def profile_entity_to_response(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Convert NGSI-LD entity dict to flat API response dict.

    Handles Orion-LD returning JSON strings for StructuredValue properties.
    """

    def _prop(key: str, default: Any = None) -> Any:
        attr = entity.get(key, {})
        if isinstance(attr, dict):
            return attr.get("value", default)
        return default

    mappings_raw = _prop("mappings", [])
    if isinstance(mappings_raw, str):
        try:
            mappings_raw = json.loads(mappings_raw)
        except json.JSONDecodeError:
            mappings_raw = []

    return {
        "id": entity.get("id", ""),
        "name": _prop("name", ""),
        "description": _prop("description"),
        "manufacturer": _prop("manufacturer"),
        "model": _prop("model"),
        "sdm_entity_type": _prop("sdmEntityType", ""),
        "mappings": mappings_raw if isinstance(mappings_raw, list) else [],
        "is_public": _prop("isPublic", False),
        "tenant_id": _extract_tenant_id(entity),
        "created_by": _prop("createdBy"),
        "created_at": _prop("createdAt", ""),
        "updated_at": _prop("updatedAt", ""),
    }


def _extract_tenant_id(entity: dict[str, Any]) -> str:
    """Extract tenant ID from refTenant relationship URN."""
    ref = entity.get("refTenant", {})
    if isinstance(ref, dict):
        obj = ref.get("object", "")
        if isinstance(obj, str) and ":" in obj:
            return obj.rsplit(":", 1)[-1]
    return ""


def build_profile_update_attrs(
    name: Optional[str] = None,
    description: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    sdm_entity_type: Optional[str] = None,
    mappings: Optional[list[dict[str, Any]]] = None,
    is_public: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Build partial NGSI-LD attribute dict for OrionClient.update_entity_attrs().

    Only includes fields that are explicitly provided (None = skip).
    Always updates ``updatedAt`` timestamp.
    """
    attrs: dict[str, Any] = {}
    now = datetime.now(timezone.utc).isoformat()
    attrs["updatedAt"] = {"type": "Property", "value": now}

    if name is not None:
        attrs["name"] = {"type": "Property", "value": name}
    if description is not None:
        attrs["description"] = {"type": "Property", "value": description}
    if manufacturer is not None:
        attrs["manufacturer"] = {"type": "Property", "value": manufacturer}
    if model is not None:
        attrs["model"] = {"type": "Property", "value": model}
    if sdm_entity_type is not None:
        attrs["sdmEntityType"] = {"type": "Property", "value": sdm_entity_type}
    if mappings is not None:
        attrs["mappings"] = {"type": "Property", "value": mappings}
    if is_public is not None:
        attrs["isPublic"] = {"type": "Property", "value": is_public}

    return attrs
