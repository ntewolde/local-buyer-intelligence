"""
Geography Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class GeographyCreate(BaseModel):
    """Schema for creating geography record"""
    name: str
    type: str  # city, state, county
    state_code: str
    county_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class GeographyResponse(BaseModel):
    """Schema for geography response"""
    id: int
    name: str
    type: str
    state_code: str
    county_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ZIPCodeResponse(BaseModel):
    """Schema for ZIP code response"""
    id: int
    zip_code: str
    geography_id: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    population: Optional[int]
    household_count: Optional[int]
    median_income: Optional[int]
    median_age: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NeighborhoodResponse(BaseModel):
    """Schema for neighborhood response"""
    id: int
    name: str
    geography_id: Optional[int]
    zip_code_id: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    household_count: Optional[int]
    median_income: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

