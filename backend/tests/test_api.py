"""
Tests for Connectivity Backend — Device Profiles API.

Tests use mocked OrionClient via the conftest.py fixtures.
No real Orion-LD or MongoDB required.
"""

import pytest
from unittest.mock import AsyncMock


class TestHealth:
    """ModuleApp provides /health and /ready automatically."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["module"] == "connectivity"

    def test_ready_check(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestDeviceProfilesAuth:
    """Authentication and authorization tests."""

    def test_missing_auth_headers_returns_401(self, client):
        """Without X-Tenant-ID header, require_auth() rejects with 401."""
        response = client.get("/api/connectivity/profiles/")
        assert response.status_code == 401

    def test_invalid_tenant_id_format(self, client, auth_headers):
        """Tenant ID must match [a-z0-9_-]{3,63}."""
        headers = {**auth_headers, "X-Tenant-ID": "INVALID FORMAT!"}
        response = client.get("/api/connectivity/profiles/", headers=headers)
        assert response.status_code == 401


class TestDeviceProfilesCRUD:
    """Device profile CRUD tests using mocked OrionClient."""

    # ---- List ----

    def test_list_profiles_empty(self, auth_client, mock_orion_client):
        mock_orion_client.query_entities.return_value = []
        response = auth_client.get("/api/connectivity/profiles/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["offset"] == 0

    def test_list_profiles_with_data(self, auth_client, mock_orion_client):
        mock_orion_client.query_entities.return_value = [
            {
                "id": "urn:ngsi-ld:DeviceProfile:abc",
                "type": "DeviceProfile",
                "name": {"type": "Property", "value": "Sensor Profile"},
                "sdmEntityType": {"type": "Property", "value": "AgriSensor"},
                "mappings": {
                    "type": "Property",
                    "value": [
                        {
                            "incoming_key": "t",
                            "target_attribute": "temperature",
                            "type": "Number",
                        }
                    ],
                },
                "isPublic": {"type": "Property", "value": False},
                "refTenant": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Tenant:testtenant",
                },
                "createdAt": {
                    "type": "Property",
                    "value": "2026-01-01T00:00:00+00:00",
                },
                "updatedAt": {
                    "type": "Property",
                    "value": "2026-01-01T00:00:00+00:00",
                },
            }
        ]

        response = auth_client.get("/api/connectivity/profiles/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Sensor Profile"
        assert data["items"][0]["sdm_entity_type"] == "AgriSensor"
        assert len(data["items"][0]["mappings"]) == 1

    def test_list_profiles_pagination(self, auth_client, mock_orion_client):
        mock_orion_client.query_entities.return_value = []
        response = auth_client.get("/api/connectivity/profiles/?offset=10&limit=5")
        assert response.status_code == 200
        call_kwargs = mock_orion_client.query_entities.call_args.kwargs
        assert call_kwargs["offset"] == 10
        assert call_kwargs["limit"] == 5

    def test_list_profiles_filter_by_type(self, auth_client, mock_orion_client):
        mock_orion_client.query_entities.return_value = []
        response = auth_client.get(
            "/api/connectivity/profiles/?sdm_entity_type=Device"
        )
        assert response.status_code == 200
        call_kwargs = mock_orion_client.query_entities.call_args.kwargs
        assert 'sdmEntityType=="Device"' in call_kwargs["q"]

    # ---- Create ----

    def test_create_profile(self, auth_client, mock_orion_client):
        response = auth_client.post(
            "/api/connectivity/profiles/",
            json={
                "name": "New Profile",
                "sdm_entity_type": "Device",
                "mappings": [
                    {
                        "incoming_key": "t",
                        "target_attribute": "temperature",
                        "type": "Number",
                    }
                ],
                "is_public": False,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Profile"  # From default mock get_entity

        # Verify OrionClient was called with correct entity
        mock_orion_client.create_entity.assert_called_once()
        entity_arg = mock_orion_client.create_entity.call_args.args[0]
        assert entity_arg["type"] == "DeviceProfile"
        assert entity_arg["name"]["value"] == "New Profile"
        assert entity_arg["refTenant"]["object"] == "urn:ngsi-ld:Tenant:testtenant"

    def test_create_profile_validation_name_required(self, auth_client):
        response = auth_client.post(
            "/api/connectivity/profiles/",
            json={"sdm_entity_type": "Device", "mappings": []},
        )
        assert response.status_code == 422  # Pydantic validation error

    # ---- Read ----

    def test_get_profile(self, auth_client):
        response = auth_client.get(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:test123"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Profile"
        assert data["sdm_entity_type"] == "AgriSensor"

    def test_get_profile_short_id(self, auth_client, mock_orion_client):
        """Short IDs (without URN prefix) should be normalized."""
        response = auth_client.get("/api/connectivity/profiles/test123")
        assert response.status_code == 200
        # Should have called with full URN
        call_arg = mock_orion_client.get_entity.call_args.args[0]
        assert call_arg == "urn:ngsi-ld:DeviceProfile:test123"

    def test_get_profile_not_found(self, auth_client, mock_orion_client):
        mock_orion_client.get_entity.side_effect = Exception("Not found")
        response = auth_client.get(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:nonexistent"
        )
        assert response.status_code == 404

    def test_get_profile_wrong_type(self, auth_client, mock_orion_client):
        """Entity exists but is not a DeviceProfile."""
        mock_orion_client.get_entity.return_value = {
            "id": "urn:ngsi-ld:DeviceProfile:test123",
            "type": "AgriParcel",  # Wrong type!
            "name": {"type": "Property", "value": "Not a profile"},
        }
        response = auth_client.get(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:test123"
        )
        assert response.status_code == 404

    # ---- Update ----

    def test_update_profile(self, auth_client, mock_orion_client):
        response = auth_client.put(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:test123",
            json={"name": "Updated Name", "is_public": True},
        )
        assert response.status_code == 200
        mock_orion_client.update_entity_attrs.assert_called_once()

    def test_update_profile_not_owned(self, auth_client, mock_orion_client):
        """Profile belongs to a different tenant."""
        mock_orion_client.get_entity.return_value = {
            "id": "urn:ngsi-ld:DeviceProfile:other",
            "type": "DeviceProfile",
            "name": {"type": "Property", "value": "Other Profile"},
            "sdmEntityType": {"type": "Property", "value": "Device"},
            "mappings": {"type": "Property", "value": []},
            "isPublic": {"type": "Property", "value": False},
            "refTenant": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:Tenant:othertenant",
            },
            "createdAt": {
                "type": "Property",
                "value": "2026-01-01T00:00:00+00:00",
            },
            "updatedAt": {
                "type": "Property",
                "value": "2026-01-01T00:00:00+00:00",
            },
        }

        response = auth_client.put(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:other",
            json={"name": "Hacked"},
        )
        assert response.status_code == 403
        # update_entity_attrs should NOT have been called
        mock_orion_client.update_entity_attrs.assert_not_called()

    # ---- Delete ----

    def test_delete_profile(self, auth_client, mock_orion_client):
        response = auth_client.delete(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:test123"
        )
        assert response.status_code == 204
        mock_orion_client.delete_entity.assert_called_once_with(
            "urn:ngsi-ld:DeviceProfile:test123"
        )

    def test_delete_profile_not_owned(self, auth_client, mock_orion_client):
        """Cannot delete another tenant's profile."""
        mock_orion_client.get_entity.return_value = {
            "id": "urn:ngsi-ld:DeviceProfile:other",
            "type": "DeviceProfile",
            "name": {"type": "Property", "value": "Other Profile"},
            "sdmEntityType": {"type": "Property", "value": "Device"},
            "mappings": {"type": "Property", "value": []},
            "isPublic": {"type": "Property", "value": False},
            "refTenant": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:Tenant:othertenant",
            },
            "createdAt": {
                "type": "Property",
                "value": "2026-01-01T00:00:00+00:00",
            },
            "updatedAt": {
                "type": "Property",
                "value": "2026-01-01T00:00:00+00:00",
            },
        }

        response = auth_client.delete(
            "/api/connectivity/profiles/urn:ngsi-ld:DeviceProfile:other"
        )
        assert response.status_code == 403
        mock_orion_client.delete_entity.assert_not_called()


class TestSchemas:
    """SDM schemas endpoint tests."""

    def test_get_sdm_schemas(self, auth_client):
        response = auth_client.get("/api/connectivity/profiles/schemas/sdm-types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert "AgriSensor" in data["types"]
        assert "temperature" in data["types"]["AgriSensor"]
        assert "WeatherStation" in data["types"]


class TestOrionProfileBuilders:
    """Unit tests for the NGSI-LD entity builders in orion_profiles.py."""

    def test_build_device_profile_entity(self):
        from app.orion_profiles import build_device_profile_entity

        entity = build_device_profile_entity(
            tenant_id="t1",
            name="P1",
            sdm_entity_type="AgriSensor",
            mappings=[{"incoming_key": "t", "target_attribute": "temperature", "type": "Number"}],
            description="desc",
            manufacturer="ACME",
            model="M100",
            is_public=True,
            created_by="user1",
            profile_id="urn:ngsi-ld:DeviceProfile:custom-id",
        )

        assert entity["id"] == "urn:ngsi-ld:DeviceProfile:custom-id"
        assert entity["type"] == "DeviceProfile"
        assert entity["name"]["value"] == "P1"
        assert entity["isPublic"]["value"] is True
        assert entity["description"]["value"] == "desc"
        assert entity["manufacturer"]["value"] == "ACME"
        assert entity["model"]["value"] == "M100"
        assert entity["createdBy"]["value"] == "user1"
        assert entity["refTenant"]["object"] == "urn:ngsi-ld:Tenant:t1"

    def test_profile_entity_to_response(self):
        from app.orion_profiles import profile_entity_to_response

        entity = {
            "id": "urn:ngsi-ld:DeviceProfile:abc",
            "type": "DeviceProfile",
            "name": {"type": "Property", "value": "P1"},
            "sdmEntityType": {"type": "Property", "value": "AgriSensor"},
            "mappings": {
                "type": "Property",
                "value": [{"incoming_key": "t", "target_attribute": "temp", "type": "Number"}],
            },
            "isPublic": {"type": "Property", "value": True},
            "description": {"type": "Property", "value": "desc"},
            "refTenant": {"type": "Relationship", "object": "urn:ngsi-ld:Tenant:t1"},
            "createdAt": {"type": "Property", "value": "2026-01-01T00:00:00+00:00"},
            "updatedAt": {"type": "Property", "value": "2026-01-01T00:00:00+00:00"},
        }

        resp = profile_entity_to_response(entity)
        assert resp["id"] == "urn:ngsi-ld:DeviceProfile:abc"
        assert resp["name"] == "P1"
        assert resp["tenant_id"] == "t1"
        assert resp["is_public"] is True
        assert len(resp["mappings"]) == 1
        assert resp["mappings"][0]["incoming_key"] == "t"

    def test_build_profile_update_attrs(self):
        from app.orion_profiles import build_profile_update_attrs

        attrs = build_profile_update_attrs(name="New", is_public=True)

        assert "updatedAt" in attrs
        assert attrs["name"]["value"] == "New"
        assert attrs["isPublic"]["value"] is True
        # description was not provided, should not be in attrs
        assert "description" not in attrs
