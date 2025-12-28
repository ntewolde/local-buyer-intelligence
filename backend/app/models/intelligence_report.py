"""
Intelligence Report Models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.demand_signal import ServiceCategory


class IntelligenceReport(Base):
    """
    Generated intelligence reports for clients
    Contains buyer profiles, demand scores, and recommendations
    """
    __tablename__ = "intelligence_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Geographic scope
    geography_id = Column(Integer, ForeignKey("geographies.id"))
    zip_codes = Column(String)  # Comma-separated list of ZIP codes
    
    # Service focus
    service_category = Column(String(50))  # ServiceCategory enum value
    
    # Report metadata
    report_name = Column(String(255))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    
    # Summary statistics
    total_households = Column(Integer)
    target_households = Column(Integer)
    average_demand_score = Column(Float)
    
    # Buyer profile (JSON)
    buyer_profile = Column(JSON)  # Structured profile data
    
    # ZIP-level scores (JSON)
    zip_demand_scores = Column(JSON)  # {zip_code: score}
    
    # Neighborhood insights (JSON)
    neighborhood_insights = Column(JSON)  # Array of neighborhood data
    
    # Channel recommendations (JSON)
    channel_recommendations = Column(JSON)  # Array of channel suggestions
    
    # Timing recommendations (JSON)
    timing_recommendations = Column(JSON)  # Seasonal/time-based suggestions
    
    # Full report data (JSON)
    report_data = Column(JSON)  # Complete report structure
    
    # Client/User reference (if needed)
    client_id = Column(Integer)  # Reference to client/user
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    geography = relationship("Geography")
    
    def __repr__(self):
        return f"<IntelligenceReport {self.report_name} - {self.service_category}>"

