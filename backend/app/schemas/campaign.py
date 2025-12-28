"""
Campaign Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.campaign import CampaignStatus
import uuid


class CampaignCreate(BaseModel):
    """Schema for creating a campaign"""
    name: str
    description: Optional[str] = None
    service_category: str
    geography_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_budget: Optional[float] = None
    budget_allocation: Optional[Dict[str, float]] = None  # {channel_id: amount}
    channel_ids: Optional[List[uuid.UUID]] = None
    messaging: Optional[str] = None
    target_reach: Optional[int] = None
    target_leads: Optional[int] = None


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_budget: Optional[float] = None
    budget_allocation: Optional[Dict[str, float]] = None
    channel_ids: Optional[List[uuid.UUID]] = None
    messaging: Optional[str] = None
    target_reach: Optional[int] = None
    target_leads: Optional[int] = None
    actual_reach: Optional[int] = None
    actual_leads: Optional[int] = None


class CampaignResponse(BaseModel):
    """Schema for campaign response"""
    id: uuid.UUID
    client_id: uuid.UUID
    geography_id: Optional[int]
    name: str
    description: Optional[str]
    service_category: str
    status: CampaignStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    total_budget: Optional[float]
    budget_allocation: Optional[Dict[str, float]]
    channel_ids: Optional[List[uuid.UUID]]
    assets: Optional[Dict[str, Any]]
    messaging: Optional[str]
    target_reach: Optional[int]
    actual_reach: Optional[int]
    target_leads: Optional[int]
    actual_leads: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        use_enum_values = True


class CampaignReportCreate(BaseModel):
    """Schema for creating a campaign report"""
    campaign_id: uuid.UUID
    metrics: Optional[Dict[str, Any]] = None
    channel_performance: Optional[Dict[str, Any]] = None
    insights: Optional[str] = None


class CampaignReportResponse(BaseModel):
    """Schema for campaign report response"""
    id: uuid.UUID
    client_id: uuid.UUID
    campaign_id: uuid.UUID
    report_date: datetime
    metrics: Optional[Dict[str, Any]]
    channel_performance: Optional[Dict[str, Any]]
    insights: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

