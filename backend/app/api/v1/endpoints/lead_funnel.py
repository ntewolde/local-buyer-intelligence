# NOTE: This module is future work and not part of the MVP contract.
# It is gated or disabled pending stabilization and compliance review.
"""
Lead Funnel API Endpoints (Option 2: Opt-in Lead Funnel Builder)

NOTE: This module is gated by feature flag FEATURE_LEAD_FUNNEL_ENABLED.
The router is conditionally included in app.api.v1.api based on settings.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id, get_current_user
from app.core.pii_guard import assert_no_pii_keys
from app.models.lead_funnel import LandingPage, Lead, LeadStatus
from app.models.client import User
from app.schemas.lead_funnel import (
    LandingPageCreate,
    LandingPageResponse,
    LeadCreate,
    LeadResponse,
    LeadUpdate
)
import uuid

router = APIRouter()


@router.post("/landing-pages", response_model=LandingPageResponse, status_code=201)
async def create_landing_page(
    landing_page: LandingPageCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a new landing page"""
    # Check if slug already exists
    existing = db.query(LandingPage).filter(LandingPage.slug == landing_page.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    landing_page_data = landing_page.model_dump()
    assert_no_pii_keys(landing_page_data)
    
    db_landing_page = LandingPage(
        client_id=client_id,
        **landing_page_data
    )
    db.add(db_landing_page)
    db.commit()
    db.refresh(db_landing_page)
    return db_landing_page


@router.get("/landing-pages", response_model=List[LandingPageResponse])
async def list_landing_pages(
    geography_id: Optional[int] = Query(None),
    service_category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List landing pages for current client"""
    query = db.query(LandingPage).filter(LandingPage.client_id == client_id)
    
    if geography_id:
        query = query.filter(LandingPage.geography_id == geography_id)
    
    if service_category:
        query = query.filter(LandingPage.service_category == service_category)
    
    if is_active is not None:
        query = query.filter(LandingPage.is_active == is_active)
    
    landing_pages = query.order_by(LandingPage.created_at.desc()).offset(offset).limit(limit).all()
    return landing_pages


@router.get("/landing-pages/{slug}", response_model=LandingPageResponse)
async def get_landing_page_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a landing page by slug (public endpoint for lead capture)"""
    landing_page = db.query(LandingPage).filter(
        LandingPage.slug == slug,
        LandingPage.is_active == True
    ).first()
    
    if not landing_page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    
    return landing_page


@router.post("/leads", response_model=LeadResponse, status_code=201)
async def create_lead(
    lead: LeadCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new lead from landing page (public endpoint with client_id from landing page)"""
    # Get client_id from landing page if provided
    client_id = None
    if lead.landing_page_id:
        landing_page = db.query(LandingPage).filter(LandingPage.id == lead.landing_page_id).first()
        if not landing_page:
            raise HTTPException(status_code=404, detail="Landing page not found")
        client_id = landing_page.client_id
    else:
        raise HTTPException(status_code=400, detail="landing_page_id is required")
    
    # Validate consent
    if not lead.email_consent and not lead.sms_consent:
        raise HTTPException(status_code=400, detail="At least one consent type is required")
    
    if lead.email and not lead.email_consent:
        raise HTTPException(status_code=400, detail="Email provided but email consent not given")
    
    if lead.phone and not lead.sms_consent:
        raise HTTPException(status_code=400, detail="Phone provided but SMS consent not given")
    
    # Get client IP for consent tracking
    client_ip = request.client.host if request.client else None
    
    lead_data = lead.model_dump()
    lead_data["client_id"] = client_id
    lead_data["consent_ip"] = client_ip
    assert_no_pii_keys(lead_data)
    
    db_lead = Lead(**lead_data)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    landing_page_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    geography_id: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List leads for current client (CRM pipeline)"""
    query = db.query(Lead).filter(Lead.client_id == client_id)
    
    if landing_page_id:
        try:
            landing_page_uuid = uuid.UUID(landing_page_id)
            query = query.filter(Lead.landing_page_id == landing_page_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid landing page ID")
    
    if status:
        try:
            LeadStatus(status)
            query = query.filter(Lead.status == status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    if geography_id:
        query = query.filter(Lead.geography_id == geography_id)
    
    leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()
    return leads


@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Update a lead (CRM pipeline management)"""
    try:
        lead_uuid = uuid.UUID(lead_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    lead = db.query(Lead).filter(
        Lead.id == lead_uuid,
        Lead.client_id == client_id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_update.model_dump(exclude_unset=True)
    assert_no_pii_keys(update_data)
    
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    return lead


@router.post("/leads/{lead_id}/unsubscribe")
async def unsubscribe_lead(
    lead_id: str,
    db: Session = Depends(get_db)
):
    """Unsubscribe a lead (public endpoint)"""
    try:
        lead_uuid = uuid.UUID(lead_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    lead = db.query(Lead).filter(Lead.id == lead_uuid).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.status = LeadStatus.UNSUBSCRIBED
    lead.email_consent = False
    lead.sms_consent = False
    db.commit()
    
    return {"status": "unsubscribed", "lead_id": str(lead.id)}

