"""
Household Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.household import PropertyType, OwnershipType
import uuid


class HouseholdCreate(BaseModel):
    """Schema for creating a household record"""
    geography_id: Optional[int] = None
    zip_code_id: Optional[int] = None
    neighborhood_id: Optional[int] = None
    property_type: Optional[PropertyType] = PropertyType.UNKNOWN
    ownership_type: Optional[OwnershipType] = OwnershipType.UNKNOWN
    property_sqft_min: Optional[int] = None
    property_sqft_max: Optional[int] = None
    lot_size_sqft: Optional[int] = None
    income_band_min: Optional[int] = None
    income_band_max: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    property_age_years: Optional[int] = None
    last_sale_year: Optional[int] = None
    data_source: Optional[str] = None


class HouseholdResponse(BaseModel):
    """Schema for household response"""
    id: int
    client_id: uuid.UUID
    geography_id: Optional[int]
    zip_code_id: Optional[int]
    neighborhood_id: Optional[int]
    property_type: PropertyType
    ownership_type: OwnershipType
    property_sqft_min: Optional[int]
    property_sqft_max: Optional[int]
    lot_size_sqft: Optional[int]
    income_band_min: Optional[int]
    income_band_max: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    property_age_years: Optional[int]
    last_sale_year: Optional[int]
    lawn_care_score: float
    security_score: float
    it_services_score: float
    fireworks_score: float
    general_service_score: float
    data_source: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        use_enum_values = True

