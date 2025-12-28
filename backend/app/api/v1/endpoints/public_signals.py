"""
Public Signals Ingestion API Endpoints (Option 3: Public Signals Ingestion)

NOTE: This module is gated by feature flag FEATURE_PUBLIC_SIGNALS_ENABLED.
The router is conditionally included in app.api.v1.api based on settings.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.collectors.ics_calendar_collector import ICSCalendarCollector
from app.models.ingestion import IngestionRun, SourceType, IngestionStatus
from app.models.geography import Geography
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/ics-calendar")
async def ingest_ics_calendar(
    ics_url: str = Query(..., description="URL of ICS calendar feed"),
    geography_id: int = Query(..., description="Geography ID for the events"),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Ingest events from an ICS calendar feed (Option 3: Public Signals Ingestion)"""
    # Verify geography belongs to client
    geography = db.query(Geography).filter(
        Geography.id == geography_id,
        Geography.client_id == client_id
    ).first()
    
    if not geography:
        raise HTTPException(status_code=404, detail="Geography not found")
    
    # Create ingestion run
    ingestion_run = IngestionRun(
        client_id=client_id,
        geography_id=geography_id,
        source_type=SourceType.CENSUS,  # Reuse existing type or add new one
        status=IngestionStatus.RUNNING
    )
    ingestion_run.started_at = datetime.utcnow()
    db.add(ingestion_run)
    db.flush()
    ingestion_run_id = str(ingestion_run.id)
    db.commit()
    
    try:
        # Collect events from ICS calendar
        collector = ICSCalendarCollector(db, client_id)
        events = collector.collect(ics_url, geography_id)
        
        # Store events
        stored_count = collector.store(events, geography_id)
        
        # Update ingestion run
        ingestion_run.status = IngestionStatus.SUCCESS
        ingestion_run.finished_at = datetime.utcnow()
        ingestion_run.records_upserted = stored_count
        db.commit()
        
        return {
            "ingestion_run_id": ingestion_run_id,
            "status": "success",
            "events_collected": len(events),
            "events_stored": stored_count,
            "geography_id": geography_id
        }
    
    except Exception as e:
        ingestion_run.status = IngestionStatus.FAILED
        ingestion_run.finished_at = datetime.utcnow()
        ingestion_run.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest ICS calendar: {str(e)}"
        )

