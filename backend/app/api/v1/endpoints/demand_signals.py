"""
Demand Signal API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.models.demand_signal import DemandSignal, ServiceCategory, SignalType
from app.schemas.demand_signal import DemandSignalCreate, DemandSignalResponse
import uuid

router = APIRouter()


@router.post("/", response_model=DemandSignalResponse)
async def create_demand_signal(
    signal: DemandSignalCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a new demand signal"""
    signal_data = signal.model_dump()
    signal_data["client_id"] = client_id
    db_signal = DemandSignal(**signal_data)
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal


@router.get("/", response_model=List[DemandSignalResponse])
async def list_demand_signals(
    geography_id: Optional[int] = Query(None),
    zip_code_id: Optional[int] = Query(None),
    service_category: Optional[str] = Query(None),
    signal_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List demand signals with optional filters"""
    query = db.query(DemandSignal).filter(DemandSignal.client_id == client_id)
    
    if geography_id:
        query = query.filter(DemandSignal.geography_id == geography_id)
    
    if zip_code_id:
        query = query.filter(DemandSignal.zip_code_id == zip_code_id)
    
    if service_category:
        try:
            ServiceCategory(service_category)
            query = query.filter(DemandSignal.service_category == service_category)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid service category")
    
    if signal_type:
        try:
            SignalType(signal_type)
            query = query.filter(DemandSignal.signal_type == signal_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid signal type")
    
    if is_active is not None:
        query = query.filter(DemandSignal.is_active == is_active)
    
    if start_date:
        query = query.filter(DemandSignal.event_start_date >= start_date)
    
    if end_date:
        query = query.filter(DemandSignal.event_end_date <= end_date)
    
    signals = query.order_by(DemandSignal.event_start_date.desc()).offset(offset).limit(limit).all()
    return signals


@router.get("/{signal_id}", response_model=DemandSignalResponse)
async def get_demand_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific demand signal"""
    signal = db.query(DemandSignal).filter(
        DemandSignal.id == signal_id,
        DemandSignal.client_id == client_id
    ).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Demand signal not found")
    return signal


@router.post("/batch", response_model=List[DemandSignalResponse])
async def create_demand_signals_batch(
    signals: List[DemandSignalCreate],
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create multiple demand signals"""
    db_signals = []
    for s in signals:
        s_data = s.model_dump()
        s_data["client_id"] = client_id
        db_signals.append(DemandSignal(**s_data))
    
    db.add_all(db_signals)
    db.commit()
    
    for s in db_signals:
        db.refresh(s)
    
    return db_signals

