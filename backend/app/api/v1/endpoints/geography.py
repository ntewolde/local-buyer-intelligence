"""
Geography API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.geography import Geography, ZIPCode, Neighborhood
from app.schemas.geography import (
    GeographyCreate,
    GeographyResponse,
    ZIPCodeResponse,
    NeighborhoodResponse,
)

router = APIRouter()


@router.post("/", response_model=GeographyResponse)
async def create_geography(
    geography: GeographyCreate,
    db: Session = Depends(get_db)
):
    """Create a new geography record"""
    db_geo = Geography(**geography.model_dump())
    db.add(db_geo)
    db.commit()
    db.refresh(db_geo)
    return db_geo


@router.get("/", response_model=List[GeographyResponse])
async def list_geographies(
    state_code: Optional[str] = Query(None),
    geo_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List geographies with optional filters"""
    query = db.query(Geography)
    
    if state_code:
        query = query.filter(Geography.state_code == state_code.upper())
    
    if geo_type:
        query = query.filter(Geography.type == geo_type)
    
    geographies = query.offset(offset).limit(limit).all()
    return geographies


@router.get("/{geography_id}", response_model=GeographyResponse)
async def get_geography(
    geography_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific geography"""
    geography = db.query(Geography).filter(Geography.id == geography_id).first()
    if not geography:
        raise HTTPException(status_code=404, detail="Geography not found")
    return geography


@router.get("/{geography_id}/zip-codes", response_model=List[ZIPCodeResponse])
async def get_geography_zip_codes(
    geography_id: int,
    db: Session = Depends(get_db)
):
    """Get all ZIP codes for a geography"""
    geography = db.query(Geography).filter(Geography.id == geography_id).first()
    if not geography:
        raise HTTPException(status_code=404, detail="Geography not found")
    
    return geography.zip_codes


@router.get("/zip-codes/{zip_code}", response_model=ZIPCodeResponse)
async def get_zip_code(
    zip_code: str,
    db: Session = Depends(get_db)
):
    """Get ZIP code by code string"""
    zip_obj = db.query(ZIPCode).filter(ZIPCode.zip_code == zip_code).first()
    if not zip_obj:
        raise HTTPException(status_code=404, detail="ZIP code not found")
    return zip_obj


@router.get("/zip-codes/", response_model=List[ZIPCodeResponse])
async def list_zip_codes(
    state_code: Optional[str] = Query(None),
    geography_id: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List ZIP codes with optional filters"""
    query = db.query(ZIPCode)
    
    if geography_id:
        query = query.filter(ZIPCode.geography_id == geography_id)
    elif state_code:
        # Join with geography to filter by state
        query = query.join(Geography).filter(Geography.state_code == state_code.upper())
    
    zip_codes = query.offset(offset).limit(limit).all()
    return zip_codes

