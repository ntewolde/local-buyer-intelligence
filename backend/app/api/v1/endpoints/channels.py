"""
Channel API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.core.pii_guard import assert_no_pii_keys
from app.models.channel import Channel, ChannelType
from app.schemas.channel import ChannelCreate, ChannelResponse
import uuid

router = APIRouter()


@router.post("/", response_model=ChannelResponse, status_code=201)
async def create_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a new channel"""
    channel_data = channel.model_dump(exclude={"client_id"})
    # PII guard: validate no PII in input
    assert_no_pii_keys(channel_data)
    db_channel = Channel(
        client_id=client_id,
        **channel_data
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


@router.get("/", response_model=List[ChannelResponse])
async def list_channels(
    geography_id: Optional[int] = Query(None),
    channel_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List channels for current client"""
    query = db.query(Channel).filter(Channel.client_id == client_id)
    
    if geography_id:
        query = query.filter(Channel.geography_id == geography_id)
    
    if channel_type:
        try:
            ChannelType(channel_type)
            query = query.filter(Channel.channel_type == channel_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid channel type")
    
    channels = query.offset(offset).limit(limit).all()
    return channels


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific channel"""
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
    
    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str,
    channel_update: ChannelCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Update a channel"""
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
    
    # Update fields
    update_data = channel_update.model_dump(exclude={"client_id"}, exclude_unset=True)
    # PII guard: validate no PII in input
    assert_no_pii_keys(update_data)
    for field, value in update_data.items():
        setattr(channel, field, value)
    
    db.commit()
    db.refresh(channel)
    return channel


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Delete a channel"""
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
    
    db.delete(channel)
    db.commit()
    return None




