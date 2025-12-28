"""
Intelligence Report Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from app.models.demand_signal import ServiceCategory


class BuyerProfileResponse(BaseModel):
    """Buyer profile data structure"""
    total_households: int
    target_households: int
    homeowner_percentage: float
    renter_percentage: float
    property_types: Dict[str, int]
    income_distribution: Dict[str, int]
    average_property_age: float
    average_lot_size: float


class ChannelRecommendation(BaseModel):
    """Channel recommendation structure"""
    channel_type: str  # direct_mail, digital_ads, door_hangers, etc.
    rationale: str
    estimated_reach: int
    estimated_cost_range: str


class TimingRecommendation(BaseModel):
    """Timing recommendation structure"""
    time_period: str
    rationale: str
    demand_score: float
    recommended_actions: List[str]


class IntelligenceReportCreate(BaseModel):
    """Schema for creating intelligence report"""
    geography_id: int
    zip_codes: str  # Comma-separated
    service_category: str
    report_name: Optional[str] = None


class ZIPDemandScore(BaseModel):
    """ZIP code demand score"""
    zip_code: str
    demand_score: float
    household_count: int
    target_households: int


class NeighborhoodInsight(BaseModel):
    """Neighborhood insight structure"""
    neighborhood_id: int
    neighborhood_name: str
    demand_score: float
    household_count: int
    key_characteristics: List[str]


class IntelligenceReportResponse(BaseModel):
    """Schema for intelligence report response"""
    id: int
    geography_id: Optional[int]
    zip_codes: str
    service_category: str
    report_name: Optional[str]
    generated_at: datetime
    valid_until: Optional[datetime]
    total_households: Optional[int]
    target_households: Optional[int]
    average_demand_score: Optional[float]
    buyer_profile: Optional[Dict[str, Any]]
    zip_demand_scores: Optional[Dict[str, float]]
    neighborhood_insights: Optional[List[Dict[str, Any]]]
    channel_recommendations: Optional[List[Dict[str, Any]]]
    timing_recommendations: Optional[List[Dict[str, Any]]]
    report_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

