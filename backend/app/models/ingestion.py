"""
Ingestion Run Models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class SourceType(str, enum.Enum):
    """Source type for ingestion"""
    CENSUS = "census"
    CSV_PROPERTY = "csv_property"
    CSV_EVENTS = "csv_events"
    CSV_CHANNELS = "csv_channels"


class IngestionStatus(str, enum.Enum):
    """Status of ingestion run"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class IngestionRun(Base):
    """Tracks refresh/import jobs"""
    __tablename__ = "ingestion_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    geography_id = Column(Integer, ForeignKey("geographies.id"), nullable=True, index=True)
    source_type = Column(Enum(SourceType), nullable=False)
    status = Column(Enum(IngestionStatus), nullable=False, default=IngestionStatus.QUEUED)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    records_upserted = Column(Integer, default=0)
    file_ref = Column(String(500), nullable=True)  # Reference to uploaded file
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="ingestion_runs")
    geography = relationship("Geography")
    
    def __repr__(self):
        return f"<IngestionRun {self.source_type.value} - {self.status.value}>"

