"""
File Upload API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.core.file_storage import save_uploaded_file
import uuid

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """
    Upload a CSV file for import
    Returns file reference for use in import endpoints
    """
    # Validate file type
    if not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Save file
    file_ref = save_uploaded_file(content, file.filename)
    
    return {
        "file_ref": file_ref,
        "filename": file.filename,
        "size": len(content)
    }

