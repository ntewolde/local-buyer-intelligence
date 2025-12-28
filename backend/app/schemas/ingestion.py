"""
Ingestion Run Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.ingestion import SourceType, IngestionStatus
import uuid


class IngestionRunResponse(BaseModel):
    """Schema for ingestion run response"""
    id: uuid.UUID
    client_id: uuid.UUID
    geography_id: Optional[int]
    source_type: SourceType
    status: IngestionStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_message: Optional[str]
    records_upserted: Optional[int]
    file_ref: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True






