"""
Campaign API Endpoints (Option 5: Campaign Orchestrator)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id, get_current_user
from app.core.pii_guard import assert_no_pii_keys
from app.models.campaign import Campaign, CampaignReport, CampaignStatus
from app.models.client import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignReportCreate,
    CampaignReportResponse
)
import uuid

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id),
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign"""
    campaign_data = campaign.model_dump()
    assert_no_pii_keys(campaign_data)
    
    db_campaign = Campaign(
        client_id=client_id,
        created_by_user_id=current_user.id,
        **campaign_data
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    geography_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    service_category: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List campaigns for current client"""
    query = db.query(Campaign).filter(Campaign.client_id == client_id)
    
    if geography_id:
        query = query.filter(Campaign.geography_id == geography_id)
    
    if status:
        try:
            CampaignStatus(status)
            query = query.filter(Campaign.status == status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    if service_category:
        query = query.filter(Campaign.service_category == service_category)
    
    campaigns = query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific campaign"""
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_uuid,
        Campaign.client_id == client_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Update a campaign"""
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_uuid,
        Campaign.client_id == client_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    update_data = campaign_update.model_dump(exclude_unset=True)
    assert_no_pii_keys(update_data)
    
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/generate-assets")
async def generate_campaign_assets(
    campaign_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Generate campaign assets (Option 5: Asset generator)"""
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_uuid,
        Campaign.client_id == client_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Generate basic asset metadata
    assets = {
        "headline": f"{campaign.name} - {campaign.service_category}",
        "description": campaign.description or f"Campaign for {campaign.service_category}",
        "call_to_action": "Get Started Today",
        "generated_at": str(db.query(Campaign).filter(Campaign.id == campaign_uuid).first().created_at)
    }
    
    campaign.assets = assets
    db.commit()
    
    return {"campaign_id": str(campaign.id), "assets": assets}


@router.post("/{campaign_id}/reports", response_model=CampaignReportResponse, status_code=201)
async def create_campaign_report(
    campaign_id: str,
    report: CampaignReportCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a campaign performance report"""
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_uuid,
        Campaign.client_id == client_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db_report = CampaignReport(
        client_id=client_id,
        campaign_id=campaign_uuid,
        **report.model_dump()
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/{campaign_id}/reports", response_model=List[CampaignReportResponse])
async def list_campaign_reports(
    campaign_id: str,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List reports for a campaign"""
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    
    reports = db.query(CampaignReport).filter(
        CampaignReport.campaign_id == campaign_uuid,
        CampaignReport.client_id == client_id
    ).order_by(CampaignReport.report_date.desc()).offset(offset).limit(limit).all()
    
    return reports

