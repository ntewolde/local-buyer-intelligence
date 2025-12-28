"""
Channel Models (Institutional/Gatekeeper directory)
NO personal contacts - only institutional/organizational data
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class ChannelType(str, enum.Enum):
    """Channel type enumeration"""
    HOA = "HOA"
    PROPERTY_MANAGER = "PROPERTY_MANAGER"
    SCHOOL = "SCHOOL"
    CHURCH = "CHURCH"
    VENUE = "VENUE"
    MEDIA = "MEDIA"
    COMMUNITY_NEWSLETTER = "COMMUNITY_NEWSLETTER"
    OTHER = "OTHER"


class Channel(Base):
    """
    Institutional/Gatekeeper directory
    NO personal emails/phones - only organizational data
    """
    __tablename__ = "channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"), nullable=True, index=True)
    channel_type = Column(Enum(ChannelType), nullable=False)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True, index=True)
    estimated_reach = Column(Integer, nullable=True)
    website = Column(String(500), nullable=True)  # Generic website URL only
    notes = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)  # Public page URL if known
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="channels")
    geography = relationship("Geography")
    
    def __repr__(self):
        return f"<Channel {self.name} ({self.channel_type.value})>"






