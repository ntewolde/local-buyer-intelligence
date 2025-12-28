"""
Client and User Models for Multi-Tenancy
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    ANALYST = "analyst"
    CLIENT = "client"


class Client(Base):
    """Client/tenant organization"""
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="client")
    geographies = relationship("Geography", back_populates="client")
    channels = relationship("Channel", back_populates="client")
    ingestion_runs = relationship("IngestionRun", back_populates="client")
    intelligence_reports = relationship("IntelligenceReport", back_populates="client")
    campaigns = relationship("Campaign", back_populates="client")
    leads = relationship("Lead", back_populates="client")
    landing_pages = relationship("LandingPage", back_populates="client")
    
    def __repr__(self):
        return f"<Client {self.name}>"


class User(Base):
    """User account (multi-tenant)"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="users")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"






