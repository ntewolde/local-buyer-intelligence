"""
CSV Import API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.core.file_storage import save_uploaded_file
from app.services.csv_import import CSVImportService
from app.models.ingestion import IngestionRun, SourceType, IngestionStatus
from app.tasks import import_csv_property_task, import_csv_events_task, import_csv_channels_task
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/property")
async def import_property_csv(
    geography_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """
    Import property CSV file
    Accepts file upload directly, validates for PII, and enqueues background job for processing
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
    
    # Validate file type
    if not file.filename or not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read and save file
    content = await file.read()
    file_ref = save_uploaded_file(content, file.filename or "property.csv")
    
    # Validate CSV for PII before queuing
    try:
        import_service = CSVImportService(db, client_id)
        # This will raise ValueError if PII is detected
        rows = import_service.parse_csv_file(file_ref)
    except ValueError as e:
        # PII detected - reject the import
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    db.flush()  # Flush to get the ID without committing
    ingestion_run_id = str(ingestion_run.id)  # Get ID before commit
    db.commit()
    
    # Enqueue Celery task
    import_csv_property_task.delay(ingestion_run_id, file_ref, geography_id, str(client_id))
    
    return {
        "ingestion_run_id": ingestion_run_id,
        "status": "queued",
        "geography_id": geography_id
    }


@router.post("/events")
async def import_events_csv(
    geography_id: int = Query(...),
    file: UploadFile = File(...),
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
    
    # Validate file type
    if not file.filename or not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read and save file
    content = await file.read()
    file_ref = save_uploaded_file(content, file.filename or "events.csv")
    
    # Validate CSV for PII before queuing
    try:
        import_service = CSVImportService(db, client_id)
        rows = import_service.parse_csv_file(file_ref)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    # Refresh not needed - ID is available after commit
    
    import_csv_events_task.delay(str(ingestion_run.id), file_ref, geography_id, str(client_id))
    
    return {
        "ingestion_run_id": str(ingestion_run.id),
        "status": "queued",
        "geography_id": geography_id
    }


@router.post("/channels")
async def import_channels_csv(
    geography_id: int = Query(...),
    file: UploadFile = File(...),
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
    
    # Validate file type
    if not file.filename or not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read and save file
    content = await file.read()
    file_ref = save_uploaded_file(content, file.filename or "channels.csv")
    
    # Validate CSV for PII before queuing
    try:
        import_service = CSVImportService(db, client_id)
        rows = import_service.parse_csv_file(file_ref)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    # Refresh not needed - ID is available after commit
    
    import_csv_channels_task.delay(str(ingestion_run.id), file_ref, geography_id, str(client_id))
    
    return {
        "ingestion_run_id": str(ingestion_run.id),
        "status": "queued",
        "geography_id": geography_id
    }






