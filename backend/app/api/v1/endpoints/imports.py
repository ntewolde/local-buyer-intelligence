"""
CSV Import API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.services.csv_import import CSVImportService
from app.models.ingestion import IngestionRun, SourceType, IngestionStatus
from app.tasks import import_csv_property_task, import_csv_events_task, import_csv_channels_task
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/property")
async def import_property_csv(
    geography_id: int = Query(...),
    file_ref: str = Query(...),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """
    Import property CSV file
    Enqueues background job for processing
    """
    # Verify geography belongs to client
    from app.models.geography import Geography
    geography = db.query(Geography).filter(
        Geography.id == geography_id,
        Geography.client_id == client_id
    ).first()
    
    if not geography:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geography not found"
        )
    
    # Create ingestion run
    ingestion_run = IngestionRun(
        client_id=client_id,
        geography_id=geography_id,
        source_type=SourceType.CSV_PROPERTY,
        status=IngestionStatus.QUEUED,
        file_ref=file_ref
    )
    db.add(ingestion_run)
    db.commit()
    db.refresh(ingestion_run)
    
    # Enqueue Celery task
    import_csv_property_task.delay(str(ingestion_run.id), file_ref, geography_id, str(client_id))
    
    return {
        "ingestion_run_id": str(ingestion_run.id),
        "status": "queued",
        "geography_id": geography_id
    }


@router.post("/events")
async def import_events_csv(
    geography_id: int = Query(...),
    file_ref: str = Query(...),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Import events CSV file"""
    from app.models.geography import Geography
    geography = db.query(Geography).filter(
        Geography.id == geography_id,
        Geography.client_id == client_id
    ).first()
    
    if not geography:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geography not found"
        )
    
    ingestion_run = IngestionRun(
        client_id=client_id,
        geography_id=geography_id,
        source_type=SourceType.CSV_EVENTS,
        status=IngestionStatus.QUEUED,
        file_ref=file_ref
    )
    db.add(ingestion_run)
    db.commit()
    db.refresh(ingestion_run)
    
    import_csv_events_task.delay(str(ingestion_run.id), file_ref, geography_id, str(client_id))
    
    return {
        "ingestion_run_id": str(ingestion_run.id),
        "status": "queued",
        "geography_id": geography_id
    }


@router.post("/channels")
async def import_channels_csv(
    geography_id: int = Query(...),
    file_ref: str = Query(...),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Import channels CSV file"""
    from app.models.geography import Geography
    geography = db.query(Geography).filter(
        Geography.id == geography_id,
        Geography.client_id == client_id
    ).first()
    
    if not geography:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geography not found"
        )
    
    ingestion_run = IngestionRun(
        client_id=client_id,
        geography_id=geography_id,
        source_type=SourceType.CSV_CHANNELS,
        status=IngestionStatus.QUEUED,
        file_ref=file_ref
    )
    db.add(ingestion_run)
    db.commit()
    db.refresh(ingestion_run)
    
    import_csv_channels_task.delay(str(ingestion_run.id), file_ref, geography_id, str(client_id))
    
    return {
        "ingestion_run_id": str(ingestion_run.id),
        "status": "queued",
        "geography_id": geography_id
    }

