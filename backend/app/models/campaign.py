"""
Campaign Models (Option 5: Campaign Orchestrator)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """
    Campaign planning and orchestration
    """
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"), nullable=True, index=True)
    
    # Campaign details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    service_category = Column(String(50), nullable=False)  # ServiceCategory enum value
    status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)
    
    # Timing
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Budget and allocation
    total_budget = Column(Float, nullable=True)  # Total budget in USD
    budget_allocation = Column(JSON, nullable=True)  # {channel_id: amount, ...}
    
    # Channel mix (JSON array of channel IDs)
    channel_ids = Column(JSON, nullable=True)  # Array of channel UUIDs
    
    # Assets and content
    assets = Column(JSON, nullable=True)  # Generated assets metadata
    messaging = Column(Text, nullable=True)  # Campaign messaging/description
    
    # Performance tracking
    target_reach = Column(Integer, nullable=True)
    actual_reach = Column(Integer, nullable=True, default=0)
    target_leads = Column(Integer, nullable=True)
    actual_leads = Column(Integer, nullable=True, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    client = relationship("Client")
    geography = relationship("Geography")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<Campaign {self.name} ({self.status.value})>"


class CampaignReport(Base):
    """
    Campaign performance reports
    """
    __tablename__ = "campaign_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Report data
    report_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metrics = Column(JSON, nullable=True)  # Performance metrics
    channel_performance = Column(JSON, nullable=True)  # Per-channel performance
    insights = Column(Text, nullable=True)  # Analysis and insights
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client")
    campaign = relationship("Campaign")
    
    def __repr__(self):
        return f"<CampaignReport {self.campaign_id} - {self.report_date}>"

