"""
Ingestion Run API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.models.ingestion import IngestionRun, SourceType, IngestionStatus
from app.schemas.ingestion import IngestionRunResponse
import uuid

router = APIRouter()


@router.get("/", response_model=List[IngestionRunResponse])
async def list_ingestion_runs(
    geography_id: Optional[int] = Query(None),
    source_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List ingestion runs for current client"""
    query = db.query(IngestionRun).filter(IngestionRun.client_id == client_id)
    
    if geography_id:
        query = query.filter(IngestionRun.geography_id == geography_id)
    
    if source_type:
        try:
            SourceType(source_type)
            query = query.filter(IngestionRun.source_type == source_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid source type")
    
    if status:
        try:
            IngestionStatus(status)
            query = query.filter(IngestionRun.status == status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    runs = query.order_by(IngestionRun.created_at.desc()).offset(offset).limit(limit).all()
    return runs


@router.get("/{ingestion_run_id}", response_model=IngestionRunResponse)
async def get_ingestion_run(
    ingestion_run_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific ingestion run"""
    try:
        run_uuid = uuid.UUID(ingestion_run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ingestion run ID")
    
    run = db.query(IngestionRun).filter(
        IngestionRun.id == run_uuid,
        IngestionRun.client_id == client_id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    
    return run


@router.post("/census/refresh")
async def refresh_census(
    geography_id: int = Query(...),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Trigger census data refresh for a geography"""
    from app.models.geography import Geography
    from app.tasks import refresh_census_task
    
    geography = db.query(Geography).filter(
        Geography.id == geography_id,
        Geography.client_id == client_id
    ).first()
    
    if not geography:
        raise HTTPException(
            status_code=404,
            detail="Geography not found"
        )
    
    # Create ingestion run
    ingestion_run = IngestionRun(
        client_id=client_id,
        geography_id=geography_id,
        source_type=SourceType.CENSUS,
        status=IngestionStatus.QUEUED
    )
    db.add(ingestion_run)
    db.commit()
    db.refresh(ingestion_run)
    
    # Enqueue Celery task
    refresh_census_task.delay(str(ingestion_run.id), geography_id, str(client_id))
    
    return {
        "ingestion_run_id": str(ingestion_run.id),
        "status": "queued",
        "geography_id": geography_id
    }

