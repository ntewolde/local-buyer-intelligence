"""
Demand Signal Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.demand_signal import ServiceCategory, SignalType
import uuid


class DemandSignalCreate(BaseModel):
    """Schema for creating a demand signal"""
    geography_id: Optional[int] = None
    zip_code_id: Optional[int] = None
    signal_type: SignalType
    service_category: ServiceCategory
    title: Optional[str] = None
    description: Optional[str] = None
    event_start_date: Optional[datetime] = None
    event_end_date: Optional[datetime] = None
    relevance_start_date: Optional[datetime] = None
    relevance_end_date: Optional[datetime] = None
    demand_score: float = Field(default=0.0, ge=0.0, le=100.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    source_data: Optional[str] = None


class DemandSignalResponse(BaseModel):
    """Schema for demand signal response"""
    id: int
    client_id: uuid.UUID
    geography_id: Optional[int]
    zip_code_id: Optional[int]
    signal_type: SignalType
    service_category: ServiceCategory
    title: Optional[str]
    description: Optional[str]
    event_start_date: Optional[datetime]
    event_end_date: Optional[datetime]
    relevance_start_date: Optional[datetime]
    relevance_end_date: Optional[datetime]
    demand_score: float
    latitude: Optional[float]
    longitude: Optional[float]
    source_name: Optional[str]
    source_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        use_enum_values = True

