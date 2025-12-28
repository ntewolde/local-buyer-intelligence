"""
Channel Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.channel import ChannelType
import uuid


class ChannelCreate(BaseModel):
    """Schema for creating a channel"""
    geography_id: Optional[int] = None
    channel_type: ChannelType
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    estimated_reach: Optional[int] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    source_url: Optional[str] = None


class ChannelResponse(BaseModel):
    """Schema for channel response"""
    id: uuid.UUID
    client_id: uuid.UUID
    geography_id: Optional[int]
    channel_type: ChannelType
    name: str
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    estimated_reach: Optional[int]
    website: Optional[str]
    notes: Optional[str]
    source_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        use_enum_values = True

