"""
Household API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.models.household import Household
from app.schemas.household import HouseholdCreate, HouseholdResponse
from app.services.intelligence_engine import IntelligenceEngine
from app.models.demand_signal import ServiceCategory
import uuid

router = APIRouter()


@router.post("/", response_model=HouseholdResponse)
async def create_household(
    household: HouseholdCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a new household record"""
    household_data = household.model_dump()
    household_data["client_id"] = client_id
    db_household = Household(**household_data)
    db.add(db_household)
    db.commit()
    db.refresh(db_household)
    return db_household


@router.get("/", response_model=List[HouseholdResponse])
async def list_households(
    geography_id: Optional[int] = Query(None),
    zip_code_id: Optional[int] = Query(None),
    neighborhood_id: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List households with optional filters"""
    query = db.query(Household).filter(Household.client_id == client_id)
    
    if geography_id:
        query = query.filter(Household.geography_id == geography_id)
    
    if zip_code_id:
        query = query.filter(Household.zip_code_id == zip_code_id)
    
    if neighborhood_id:
        query = query.filter(Household.neighborhood_id == neighborhood_id)
    
    households = query.offset(offset).limit(limit).all()
    return households


@router.get("/{household_id}", response_model=HouseholdResponse)
async def get_household(
    household_id: int,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific household"""
    household = db.query(Household).filter(
        Household.id == household_id,
        Household.client_id == client_id
    ).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return household


@router.post("/batch", response_model=List[HouseholdResponse])
async def create_households_batch(
    households: List[HouseholdCreate],
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create multiple household records"""
    db_households = []
    for h in households:
        h_data = h.model_dump()
        h_data["client_id"] = client_id
        db_households.append(Household(**h_data))
    
    db.add_all(db_households)
    db.commit()
    
    for h in db_households:
        db.refresh(h)
    
    return db_households


@router.get("/geography/{geography_id}/demand-scores")
async def get_household_demand_scores(
    geography_id: int,
    service_category: str = Query("general"),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get households with demand scores for a geography"""
    try:
        service_cat = ServiceCategory(service_category)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service category")
    
    engine = IntelligenceEngine(db)
    households = engine.get_households_by_geography(
        client_id=client_id,
        geography_id=geography_id,
        service_category=service_cat,
        min_demand_score=min_score
    )
    
    # Calculate scores for each household
    results = []
    for household in households[offset:offset+limit]:
        score = engine.calculate_household_demand_score(household, service_cat)
        household_dict = HouseholdResponse.model_validate(household).model_dump()
        household_dict["demand_score"] = score
        results.append(household_dict)
    
    return {
        "households": results,
        "total": len(households),
        "limit": limit,
        "offset": offset
    }

