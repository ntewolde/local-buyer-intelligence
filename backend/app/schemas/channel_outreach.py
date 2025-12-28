"""
Channel Outreach Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.channel_outreach import OutreachStatus
import uuid


class ChannelOutreachCreate(BaseModel):
    """Schema for creating a channel outreach"""
    channel_id: uuid.UUID
    outreach_date: Optional[datetime] = None
    status: OutreachStatus = OutreachStatus.PLANNED
    method: Optional[str] = None
    notes: Optional[str] = None
    next_followup_date: Optional[datetime] = None


class ChannelOutreachResponse(BaseModel):
    """Schema for channel outreach response"""
    id: uuid.UUID
    client_id: uuid.UUID
    channel_id: uuid.UUID
    outreach_date: datetime
    status: OutreachStatus
    method: Optional[str]
    notes: Optional[str]
    response_received: Optional[datetime]
    next_followup_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        use_enum_values = True


class ChannelOutreachUpdate(BaseModel):
    """Schema for updating a channel outreach"""
    status: Optional[OutreachStatus] = None
    method: Optional[str] = None
    notes: Optional[str] = None
    response_received: Optional[datetime] = None
    next_followup_date: Optional[datetime] = None

