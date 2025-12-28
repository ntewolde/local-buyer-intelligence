"""
Data Freshness API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.models.geography import Geography
import uuid

router = APIRouter()


@router.get("/geography/{geography_id}/freshness")
async def get_geography_freshness(
    geography_id: int,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get data freshness timestamps for a geography"""
    geography = db.query(Geography).filter(
        Geography.id == geography_id,
        Geography.client_id == client_id
    ).first()
    
    if not geography:
        raise HTTPException(
            status_code=404,
            detail="Geography not found"
        )
    
    return {
        "geography_id": geography_id,
        "geography_name": geography.name,
        "census_last_refreshed_at": geography.census_last_refreshed_at.isoformat() if geography.census_last_refreshed_at else None,
        "property_last_refreshed_at": geography.property_last_refreshed_at.isoformat() if geography.property_last_refreshed_at else None,
        "events_last_refreshed_at": geography.events_last_refreshed_at.isoformat() if geography.events_last_refreshed_at else None,
        "channels_last_refreshed_at": geography.channels_last_refreshed_at.isoformat() if geography.channels_last_refreshed_at else None,
    }






