"""
Shared test fixtures for connectivity backend.

Provides:
- mock_orion_client: AsyncMock for OrionClient
- auth_headers: Standard gateway-injected auth headers
- client: TestClient with mocked OrionClient
- auth_client: Authenticated client wrapper
"""

import sys
import os

# Ensure nkz-platform-sdk is importable (monorepo relative path)
_SDK_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "nkz", "services", "nkz-platform-sdk")
)
if os.path.isdir(_SDK_PATH) and _SDK_PATH not in sys.path:
    sys.path.insert(0, _SDK_PATH)

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_orion_client():
    """Mock OrionClient for testing — all methods are AsyncMock."""
    mock = AsyncMock()

    # Default query_entities returns empty list
    mock.query_entities.return_value = []

    # Default get_entity returns a valid DeviceProfile
    mock.get_entity.return_value = {
        "id": "urn:ngsi-ld:DeviceProfile:test123",
        "type": "DeviceProfile",
        "name": {"type": "Property", "value": "Test Profile"},
        "sdmEntityType": {"type": "Property", "value": "AgriSensor"},
        "mappings": {"type": "Property", "value": []},
        "isPublic": {"type": "Property", "value": False},
        "refTenant": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Tenant:testtenant",
        },
        "createdAt": {"type": "Property", "value": "2026-01-01T00:00:00+00:00"},
        "updatedAt": {"type": "Property", "value": "2026-01-01T00:00:00+00:00"},
    }

    # Default create_entity returns success
    mock.create_entity.return_value = {
        "id": "urn:ngsi-ld:DeviceProfile:test123",
        "status": "created",
    }

    # Default update_entity_attrs returns None (success)
    mock.update_entity_attrs.return_value = None

    # Default delete_entity returns None (success)
    mock.delete_entity.return_value = None

    return mock


@pytest.fixture
def auth_headers():
    """Standard auth headers as injected by the API Gateway."""
    return {
        "X-Tenant-ID": "testtenant",
        "X-User-ID": "testuser",
        "X-User-Roles": "Farmer,TenantAdmin",
    }


@pytest.fixture
def client(mock_orion_client):
    """TestClient with OrionClient.app.orion() patched."""
    with patch("app.main.app.orion", return_value=mock_orion_client):
        from app.main import app

        with TestClient(app) as tc:
            yield tc


class AuthenticatedClient:
    """Wrapper that injects auth headers into every request."""

    def __init__(self, client, headers):
        self._client = client
        self._headers = headers

    def get(self, path, **kwargs):
        h = kwargs.pop("headers", {})
        h.update(self._headers)
        return self._client.get(path, headers=h, **kwargs)

    def post(self, path, **kwargs):
        h = kwargs.pop("headers", {})
        h.update(self._headers)
        return self._client.post(path, headers=h, **kwargs)

    def put(self, path, **kwargs):
        h = kwargs.pop("headers", {})
        h.update(self._headers)
        return self._client.put(path, headers=h, **kwargs)

    def delete(self, path, **kwargs):
        h = kwargs.pop("headers", {})
        h.update(self._headers)
        return self._client.delete(path, headers=h, **kwargs)


@pytest.fixture
def auth_client(client, auth_headers):
    """Authenticated TestClient — auth headers included automatically."""
    return AuthenticatedClient(client, auth_headers)
