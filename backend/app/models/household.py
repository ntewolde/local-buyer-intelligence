"""
Household Data Models (Non-PII)
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PropertyType(str, enum.Enum):
    """Property type enumeration"""
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    CONDO = "condo"
    APARTMENT = "apartment"
    MOBILE_HOME = "mobile_home"
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"


class OwnershipType(str, enum.Enum):
    """Ownership type enumeration"""
    OWNER = "owner"
    RENTER = "renter"
    UNKNOWN = "unknown"


class Household(Base):
    """
    Household record (non-PII)
    Stores aggregated household characteristics without personal identifiers
    """
    __tablename__ = "households"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Geographic references
    geography_id = Column(Integer, ForeignKey("geographies.id"))
    zip_code_id = Column(Integer, ForeignKey("zip_codes.id"))
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"))
    
    # Property characteristics (from public records)
    property_type = Column(Enum(PropertyType), default=PropertyType.UNKNOWN)
    ownership_type = Column(Enum(OwnershipType), default=OwnershipType.UNKNOWN)
    
    # Property size proxies (square footage ranges)
    property_sqft_min = Column(Integer)  # Lower bound
    property_sqft_max = Column(Integer)  # Upper bound
    
    # Yard/lot size proxy (square feet)
    lot_size_sqft = Column(Integer)
    
    # Income band proxy (from census/assessor data)
    income_band_min = Column(Integer)  # Lower bound in USD
    income_band_max = Column(Integer)  # Upper bound in USD
    
    # Geographic coordinates (approximate, block-level)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Timing indicators
    property_age_years = Column(Integer)  # Years since construction
    last_sale_year = Column(Integer)  # Year of last sale (turnover indicator)
    
    # Demand scoring (calculated fields)
    lawn_care_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    it_services_score = Column(Float, default=0.0)
    fireworks_score = Column(Float, default=0.0)
    general_service_score = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    data_source = Column(String(100))  # Source of data (assessor, census, etc.)
    
    # Relationships
    geography = relationship("Geography", back_populates="households")
    zip_code = relationship("ZIPCode", back_populates="households")
    neighborhood = relationship("Neighborhood", back_populates="households")
    
    def __repr__(self):
        return f"<Household {self.id} - {self.property_type} - {self.ownership_type}>"

