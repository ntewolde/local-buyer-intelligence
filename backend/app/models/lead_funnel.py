"""
Lead Funnel Models (Option 2: Opt-in Lead Funnel Builder)
Consent-based lead capture - NO PII scraping
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class ConsentType(str, enum.Enum):
    """Consent type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"


class LeadStatus(str, enum.Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    UNSUBSCRIBED = "unsubscribed"


class LandingPage(Base):
    """
    Landing pages per city + service
    """
    __tablename__ = "landing_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"), nullable=True, index=True)
    
    # Landing page details
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    service_category = Column(String(50), nullable=False)
    city_name = Column(String(255), nullable=True)
    state_code = Column(String(2), nullable=True)
    
    # Content
    headline = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    call_to_action = Column(String(255), nullable=True)
    
    # Consent options
    consent_types = Column(String(50), nullable=True)  # Comma-separated consent types
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client")
    geography = relationship("Geography")
    
    def __repr__(self):
        return f"<LandingPage {self.name} ({self.slug})>"


class Lead(Base):
    """
    Opt-in leads with consent
    Stores only consented contact information
    """
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    landing_page_id = Column(UUID(as_uuid=True), ForeignKey("landing_pages.id"), nullable=True, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"), nullable=True, index=True)
    
    # Contact information (consented only)
    email = Column(String(255), nullable=True, index=True)  # Only if email consent given
    phone = Column(String(20), nullable=True)  # Only if SMS consent given
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Consent tracking
    email_consent = Column(Boolean, default=False, nullable=False)
    sms_consent = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    consent_ip = Column(String(45), nullable=True)  # IP address for consent tracking
    
    # Lead details
    status = Column(Enum(LeadStatus), nullable=False, default=LeadStatus.NEW)
    service_category = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    
    # CRM pipeline
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client")
    landing_page = relationship("LandingPage")
    geography = relationship("Geography")
    assigned_to = relationship("User")
    
    def __repr__(self):
        return f"<Lead {self.id} - {self.status.value}>"

