"""
Lead Funnel Schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.lead_funnel import ConsentType, LeadStatus
import uuid


class LandingPageCreate(BaseModel):
    """Schema for creating a landing page"""
    name: str
    slug: str
    service_category: str
    geography_id: Optional[int] = None
    city_name: Optional[str] = None
    state_code: Optional[str] = None
    headline: Optional[str] = None
    description: Optional[str] = None
    call_to_action: Optional[str] = None
    consent_types: Optional[str] = None  # Comma-separated
    is_active: bool = True


class LandingPageResponse(BaseModel):
    """Schema for landing page response"""
    id: uuid.UUID
    client_id: uuid.UUID
    geography_id: Optional[int]
    name: str
    slug: str
    service_category: str
    city_name: Optional[str]
    state_code: Optional[str]
    headline: Optional[str]
    description: Optional[str]
    call_to_action: Optional[str]
    consent_types: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LeadCreate(BaseModel):
    """Schema for creating a lead (from landing page)"""
    landing_page_id: Optional[uuid.UUID] = None
    geography_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    zip_code: Optional[str] = None
    email_consent: bool = False
    sms_consent: bool = False
    service_category: Optional[str] = None
    consent_ip: Optional[str] = None


class LeadResponse(BaseModel):
    """Schema for lead response"""
    id: uuid.UUID
    client_id: uuid.UUID
    landing_page_id: Optional[uuid.UUID]
    geography_id: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    zip_code: Optional[str]
    email_consent: bool
    sms_consent: bool
    consent_date: datetime
    status: LeadStatus
    service_category: Optional[str]
    assigned_to_user_id: Optional[uuid.UUID]
    last_contacted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        use_enum_values = True


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    assigned_to_user_id: Optional[uuid.UUID] = None
    last_contacted_at: Optional[datetime] = None

