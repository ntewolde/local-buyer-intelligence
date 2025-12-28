"""
Channel Outreach Tracking Models
Tracks outreach attempts to institutional channels (NO personal contacts)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class OutreachStatus(str, enum.Enum):
    """Outreach status enumeration"""
    PLANNED = "planned"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    FOLLOWED_UP = "followed_up"
    PARTNERED = "partnered"
    DECLINED = "declined"
    NO_RESPONSE = "no_response"


class ChannelOutreach(Base):
    """
    Tracks outreach attempts to channels
    NO personal contacts - only organizational outreach
    """
    __tablename__ = "channel_outreaches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=False, index=True)
    
    # Outreach details
    outreach_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(Enum(OutreachStatus), nullable=False, default=OutreachStatus.PLANNED)
    method = Column(String(50), nullable=True)  # e.g., "email", "phone", "website_form", "in_person"
    notes = Column(Text, nullable=True)  # Notes about the outreach (NO personal info)
    response_received = Column(DateTime(timezone=True), nullable=True)
    next_followup_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client")
    channel = relationship("Channel")
    
    def __repr__(self):
        return f"<ChannelOutreach {self.channel_id} - {self.status.value}>"

