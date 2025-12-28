"""
Geographic Data Models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Geography(Base):
    """Base geographic entity (city, state, county)"""
    __tablename__ = "geographies"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # city, state, county
    state_code = Column(String(2), nullable=False, index=True)
    county_name = Column(String(255))
    
    # Geographic coordinates (center point)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="geographies")
    zip_codes = relationship("ZIPCode", back_populates="geography")
    neighborhoods = relationship("Neighborhood", back_populates="geography")
    households = relationship("Household", back_populates="geography")
    demand_signals = relationship("DemandSignal", back_populates="geography")
    channels = relationship("Channel", back_populates="geography")
    ingestion_runs = relationship("IngestionRun", back_populates="geography")
    
    def __repr__(self):
        return f"<Geography {self.name}, {self.state_code}>"


class ZIPCode(Base):
    """ZIP Code data"""
    __tablename__ = "zip_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    zip_code = Column(String(10), unique=True, nullable=False, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"))
    
    # Geographic coordinates
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Aggregate statistics (census-derived)
    population = Column(Integer)
    household_count = Column(Integer)
    median_income = Column(Integer)  # USD
    median_age = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    geography = relationship("Geography", back_populates="zip_codes")
    neighborhoods = relationship("Neighborhood", back_populates="zip_code")
    households = relationship("Household", back_populates="zip_code")
    demand_signals = relationship("DemandSignal", back_populates="zip_code")
    
    def __repr__(self):
        return f"<ZIPCode {self.zip_code}>"


class Neighborhood(Base):
    """Neighborhood-level geographic entity"""
    __tablename__ = "neighborhoods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"))
    zip_code_id = Column(Integer, ForeignKey("zip_codes.id"))
    
    # Geographic boundaries (stored as GeoJSON string or use PostGIS)
    boundary_geojson = Column(String)
    
    # Geographic center
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Aggregate statistics
    household_count = Column(Integer)
    median_income = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    geography = relationship("Geography", back_populates="neighborhoods")
    zip_code = relationship("ZIPCode", back_populates="neighborhoods")
    households = relationship("Household", back_populates="neighborhood")
    
    def __repr__(self):
        return f"<Neighborhood {self.name}>"

