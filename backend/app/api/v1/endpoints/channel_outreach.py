"""
Channel Outreach API Endpoints (Option 4: Institutional Channel CRM)

NOTE: This module is gated by feature flag FEATURE_CHANNEL_CRM_ENABLED.
The router is conditionally included in app.api.v1.api based on settings.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.core.pii_guard import assert_no_pii_keys
from app.models.channel_outreach import ChannelOutreach, OutreachStatus
from app.models.channel import Channel
from app.schemas.channel_outreach import (
    ChannelOutreachCreate,
    ChannelOutreachResponse,
    ChannelOutreachUpdate
)
import uuid

router = APIRouter()


@router.post("/", response_model=ChannelOutreachResponse, status_code=201)
async def create_channel_outreach(
    outreach: ChannelOutreachCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a new channel outreach record"""
    # Verify channel belongs to client
    channel = db.query(Channel).filter(
        Channel.id == outreach.channel_id,
        Channel.client_id == client_id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    outreach_data = outreach.model_dump()
    assert_no_pii_keys(outreach_data)
    
    db_outreach = ChannelOutreach(
        client_id=client_id,
        **outreach_data
    )
    db.add(db_outreach)
    
    # Update channel's last_contacted_at and contact_status
    channel.last_contacted_at = outreach.outreach_date or db_outreach.outreach_date
    channel.contact_status = outreach.status.value
    
    db.commit()
    db.refresh(db_outreach)
    return db_outreach


@router.get("/", response_model=List[ChannelOutreachResponse])
async def list_channel_outreaches(
    channel_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List channel outreaches for current client"""
    query = db.query(ChannelOutreach).filter(ChannelOutreach.client_id == client_id)
    
    if channel_id:
        try:
            channel_uuid = uuid.UUID(channel_id)
            query = query.filter(ChannelOutreach.channel_id == channel_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid channel ID")
    
    if status:
        try:
            OutreachStatus(status)
            query = query.filter(ChannelOutreach.status == status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    outreaches = query.order_by(ChannelOutreach.outreach_date.desc()).offset(offset).limit(limit).all()
    return outreaches


@router.get("/{outreach_id}", response_model=ChannelOutreachResponse)
async def get_channel_outreach(
    outreach_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific channel outreach"""
    try:
        outreach_uuid = uuid.UUID(outreach_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid outreach ID")
    
    outreach = db.query(ChannelOutreach).filter(
        ChannelOutreach.id == outreach_uuid,
        ChannelOutreach.client_id == client_id
    ).first()
    
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")
    
    return outreach


@router.put("/{outreach_id}", response_model=ChannelOutreachResponse)
async def update_channel_outreach(
    outreach_id: str,
    outreach_update: ChannelOutreachUpdate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Update a channel outreach"""
    try:
        outreach_uuid = uuid.UUID(outreach_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid outreach ID")
    
    outreach = db.query(ChannelOutreach).filter(
        ChannelOutreach.id == outreach_uuid,
        ChannelOutreach.client_id == client_id
    ).first()
    
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")
    
    update_data = outreach_update.model_dump(exclude_unset=True)
    assert_no_pii_keys(update_data)
    
    for field, value in update_data.items():
        setattr(outreach, field, value)
    
    # Update channel status if outreach status changed
    if "status" in update_data:
        channel = db.query(Channel).filter(Channel.id == outreach.channel_id).first()
        if channel:
            channel.contact_status = update_data["status"].value
    
    db.commit()
    db.refresh(outreach)
    return outreach


@router.post("/channels/{channel_id}/score")
async def calculate_channel_score(
    channel_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Calculate quality and engagement scores for a channel (Option 4: Channel scoring)"""
    try:
        channel_uuid = uuid.UUID(channel_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid channel ID")
    
    channel = db.query(Channel).filter(
        Channel.id == channel_uuid,
        Channel.client_id == client_id
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Calculate quality score based on channel characteristics
    quality_score = 50  # Base score
    
    if channel.estimated_reach:
        if channel.estimated_reach > 10000:
            quality_score += 20
        elif channel.estimated_reach > 5000:
            quality_score += 10
        elif channel.estimated_reach > 1000:
            quality_score += 5
    
    if channel.website:
        quality_score += 10
    
    if channel.source_url:
        quality_score += 5
    
    # Calculate engagement score based on outreach history
    engagement_score = 50  # Base score
    
    outreaches = db.query(ChannelOutreach).filter(
        ChannelOutreach.channel_id == channel_uuid,
        ChannelOutreach.client_id == client_id
    ).all()
    
    if outreaches:
        responded_count = sum(1 for o in outreaches if o.status == OutreachStatus.RESPONDED)
        partnered_count = sum(1 for o in outreaches if o.status == OutreachStatus.PARTNERED)
        
        if partnered_count > 0:
            engagement_score += 30
        elif responded_count > 0:
            engagement_score += 20
        elif len(outreaches) > 0:
            engagement_score += 10
    
    # Update channel scores
    channel.quality_score = min(100, max(0, quality_score))
    channel.engagement_score = min(100, max(0, engagement_score))
    db.commit()
    
    return {
        "channel_id": str(channel.id),
        "quality_score": channel.quality_score,
        "engagement_score": channel.engagement_score
    }

