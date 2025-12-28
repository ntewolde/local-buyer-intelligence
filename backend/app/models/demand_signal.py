"""
Demand Signal Models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.core.database import Base


class ServiceCategory(str, enum.Enum):
    """Service category enumeration"""
    LAWN_CARE = "lawn_care"
    SECURITY = "security"
    IT_SERVICES = "it_services"
    FIREWORKS = "fireworks"
    HOME_IMPROVEMENT = "home_improvement"
    CLEANING = "cleaning"
    PEST_CONTROL = "pest_control"
    HVAC = "hvac"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    GENERAL = "general"


class SignalType(str, enum.Enum):
    """Type of demand signal"""
    EVENT = "event"  # City events, school events
    PERMIT = "permit"  # Building permits
    SEASONAL = "seasonal"  # Time-based
    TURNOVER = "turnover"  # Property sales
    WEATHER = "weather"  # Weather patterns
    CENSUS = "census"  # Census data
    DEMOGRAPHIC = "demographic"  # Demographic aggregates
    CUSTOM = "custom"  # Custom signals


class DemandSignal(Base):
    """
    Demand signals that indicate buying intent
    Aggregated and anonymized, no PII
    """
    __tablename__ = "demand_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    
    # Geographic reference
    geography_id = Column(Integer, ForeignKey("geographies.id"), nullable=True)
    zip_code_id = Column(Integer, ForeignKey("zip_codes.id"), nullable=True)
    
    # Signal classification
    signal_type = Column(Enum(SignalType), nullable=False)
    service_category = Column(Enum(ServiceCategory), nullable=False)
    
    # Signal details
    title = Column(String(255))
    description = Column(Text)
    
    # Timing
    event_start_date = Column(DateTime(timezone=True))
    event_end_date = Column(DateTime(timezone=True))
    relevance_start_date = Column(DateTime(timezone=True))
    relevance_end_date = Column(DateTime(timezone=True))
    
    # Demand score (0-100)
    demand_score = Column(Float, default=0.0)
    
    # Geographic coordinates (if applicable)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Source information
    source_name = Column(String(255))  # e.g., "city_events", "permit_office"
    source_url = Column(String(500))
    source_data = Column(Text)  # JSON string of raw source data
    
    # Value for numeric signals (e.g., population count, income)
    value = Column(Float, nullable=True)
    
    # Metadata JSON for flexible additional data
    metadata = Column(Text)  # JSON string
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    geography = relationship("Geography", back_populates="demand_signals")
    zip_code = relationship("ZIPCode", back_populates="demand_signals")
    
    def __repr__(self):
        return f"<DemandSignal {self.signal_type} - {self.service_category} - {self.demand_score}>"

