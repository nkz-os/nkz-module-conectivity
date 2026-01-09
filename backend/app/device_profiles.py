"""
Connectivity Module - Device Profiles API

Manages Device Profiles for IoT data transformation from raw incoming data
to NGSI-LD/SDM compliant attributes.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import pymongo
from pymongo import MongoClient

from app.config import get_settings
from app.middleware import get_current_user, get_tenant_id, TokenPayload

router = APIRouter(prefix="/profiles", tags=["Device Profiles"])

# =============================================================================
# Pydantic Models
# =============================================================================

class MappingEntry(BaseModel):
    incoming_key: str = Field(..., description="Key from incoming device data")
    target_attribute: str = Field(..., description="Target NGSI-LD attribute name")
    type: str = Field(default="Number", description="Data type (Number, Text, Boolean, etc.)")
    transformation: Optional[str] = Field(None, description="JEXL transformation expression (e.g., 'val * 100')")
    unit: Optional[str] = Field(None, description="Unit of measurement")

class DeviceProfileCreate(BaseModel):
    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    manufacturer: Optional[str] = Field(None, description="Device manufacturer")
    model: Optional[str] = Field(None, description="Device model")
    sdm_entity_type: str = Field(..., description="Target SDM entity type (e.g., AgriSensor)")
    mappings: List[MappingEntry] = Field(..., description="Data transformations")
    is_public: bool = Field(default=False, description="Public template profile")

class DeviceProfile(DeviceProfileCreate):
    id: str = Field(..., description="Profile ID")
    tenant_id: str = Field(..., description="Owning tenant")
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

# =============================================================================
# MongoDB Connection
# =============================================================================

def get_mongodb():
    """Get MongoDB client"""
    settings = get_settings()
    client = MongoClient(settings.mongodb_url)
    return client

def get_profiles_collection():
    """Get device profiles collection"""
    client = get_mongodb()
    db = client.nekazari
    return db.device_profiles

# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/", response_model=List[DeviceProfile])
async def list_profiles(
    tenant_id: str = Depends(get_tenant_id),
    sdm_entity_type: Optional[str] = None,
    include_public: bool = True
):
    """
    List device profiles for current tenant.
    
    Args:
        sdm_entity_type: Filter by SDM entity type
        include_public: Include public template profiles
    """
    collection = get_profiles_collection()
    
    # Build query
    query = {}
    if include_public:
        query["$or"] = [
            {"tenant_id": tenant_id},
            {"is_public": True}
        ]
    else:
        query["tenant_id"] = tenant_id
    
    if sdm_entity_type:
        query["sdm_entity_type"] = sdm_entity_type
    
    # Fetch profiles
    profiles = list(collection.find(query).sort("name", 1))
    
    # Convert to response model
    result = []
    for profile in profiles:
        profile["id"] = str(profile["_id"])
        del profile["_id"]
        result.append(DeviceProfile(**profile))
    
    return result


@router.post("/", response_model=DeviceProfile, status_code=201)
async def create_profile(
    profile: DeviceProfileCreate,
    user: TokenPayload = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new device profile"""
    collection = get_profiles_collection()
    
    # Build document
    now = datetime.utcnow()
    doc = profile.dict()
    doc["tenant_id"] = tenant_id
    doc["created_by"] = user.email
    doc["created_at"] = now
    doc["updated_at"] = now
    
    # Insert
    result = collection.insert_one(doc)
    
    # Return created profile
    doc["id"] = str(result.inserted_id)
    del doc["_id"]
    return DeviceProfile(**doc)


@router.get("/{profile_id}", response_model=DeviceProfile)
async def get_profile(
    profile_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get a specific device profile"""
    collection = get_profiles_collection()
    
    try:
        profile = collection.find_one({
            "_id": ObjectId(profile_id),
            "$or": [
                {"tenant_id": tenant_id},
                {"is_public": True}
            ]
        })
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid profile ID")
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile["id"] = str(profile["_id"])
    del profile["_id"]
    return DeviceProfile(**profile)


@router.put("/{profile_id}", response_model=DeviceProfile)
async def update_profile(
    profile_id: str,
    updated: DeviceProfileCreate,
    user: TokenPayload = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update a device profile (tenant ownership required)"""
    collection = get_profiles_collection()
    
    try:
        # Check ownership
        existing = collection.find_one({
            "_id": ObjectId(profile_id),
            "tenant_id": tenant_id
        })
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid profile ID")
    
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found or not owned by tenant")
    
    # Update document
    update_doc = updated.dict()
    update_doc["updated_at"] = datetime.utcnow()
    update_doc["updated_by"] = user.email
    
    collection.update_one(
        {"_id": ObjectId(profile_id)},
        {"$set": update_doc}
    )
    
    # Fetch and return updated profile
    profile = collection.find_one({"_id": ObjectId(profile_id)})
    profile["id"] = str(profile["_id"])
    del profile["_id"]
    return DeviceProfile(**profile)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: str,
    user: TokenPayload = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete a device profile (tenant ownership required)"""
    collection = get_profiles_collection()
    
    try:
        result = collection.delete_one({
            "_id": ObjectId(profile_id),
            "tenant_id": tenant_id
        })
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid profile ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found or not owned by tenant")
    
    return None


@router.get("/schemas/sdm-types", response_model=Dict[str, Any])
async def get_sdm_schemas():
    """
    Get available SDM entity types and their attributes for mapping.
    This helps users know what target attributes are available.
    """
    # This could be enhanced to dynamically fetch from SDM service
    # For now, return common IoT types
    return {
        "AgriSensor": {
            "attributes": ["temperature", "humidity", "soilMoisture", "batteryLevel", "rssi"]
        },
        "WeatherStation": {
            "attributes": ["temperature", "humidity", "pressure", "windSpeed", "windDirection", "precipitation"]
        },
        "Device": {
            "attributes": ["value", "batteryLevel", "rssi", "status"]
        }
    }
