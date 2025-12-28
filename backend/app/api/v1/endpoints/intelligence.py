"""
Intelligence Report API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_client_id
from app.services.intelligence_engine import IntelligenceEngine
from app.models.intelligence_report import IntelligenceReport
from app.models.geography import Geography, ZIPCode
from app.schemas.intelligence_report import (
    IntelligenceReportCreate,
    IntelligenceReportResponse,
    BuyerProfileResponse,
)
from app.models.demand_signal import ServiceCategory
import uuid

router = APIRouter()


@router.post("/reports", response_model=IntelligenceReportResponse)
async def create_intelligence_report(
    report_data: IntelligenceReportCreate,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Create a new intelligence report"""
    engine = IntelligenceEngine(db)
    
    # Validate geography belongs to client
    geography = db.query(Geography).filter(
        Geography.id == report_data.geography_id,
        Geography.client_id == client_id
    ).first()
    if not geography:
        raise HTTPException(status_code=404, detail="Geography not found")
    
    # Parse ZIP codes
    zip_code_list = [z.strip() for z in report_data.zip_codes.split(",")]
    zip_codes = db.query(ZIPCode).filter(ZIPCode.zip_code.in_(zip_code_list)).all()
    zip_code_ids = [zc.id for zc in zip_codes]
    
    # Get service category
    try:
        service_category = ServiceCategory(report_data.service_category)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service category")
    
    # Get households
    households = engine.get_households_by_geography(
        client_id=client_id,
        geography_id=report_data.geography_id,
        zip_code_ids=zip_code_ids,
        service_category=service_category
    )
    
    # Generate buyer profile
    buyer_profile = engine.generate_buyer_profile(households, service_category)
    
    # Calculate ZIP demand scores
    zip_demand_scores = engine.calculate_zip_demand_scores(client_id, zip_code_ids, service_category)
    
    # Get top ZIP codes with rationale (per spec section 8)
    top_zips = engine.get_top_zip_codes_with_rationale(
        client_id, zip_code_ids, service_category, top_n=5
    )
    
    # Calculate average demand score
    if households:
        total_score = sum(
            engine.calculate_household_demand_score(h, service_category)
            for h in households
        )
        avg_demand_score = total_score / len(households)
    else:
        avg_demand_score = 0.0
    
    # Generate channel recommendations
    channel_recommendations = _generate_channel_recommendations(
        buyer_profile, service_category, db, client_id, report_data.geography_id
    )
    
    # Generate timing recommendations
    timing_recommendations = _generate_timing_recommendations(
        service_category, avg_demand_score
    )
    
    # Create report
    report = IntelligenceReport(
        client_id=client_id,
        geography_id=report_data.geography_id,
        zip_codes=report_data.zip_codes,
        service_category=report_data.service_category,
        report_name=report_data.report_name or f"{service_category.value} Report",
        total_households=buyer_profile["total_households"],
        target_households=buyer_profile["target_households"],
        average_demand_score=avg_demand_score,
        buyer_profile=buyer_profile,
        zip_demand_scores=zip_demand_scores,
        channel_recommendations=channel_recommendations,
        timing_recommendations=timing_recommendations,
        report_data={
            "buyer_profile": buyer_profile,
            "zip_demand_scores": zip_demand_scores,
            "top_zip_codes": top_zips,  # Top ZIPs with rationale (per spec section 8)
            "channel_recommendations": channel_recommendations,
            "timing_recommendations": timing_recommendations,
        }
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/reports", response_model=List[IntelligenceReportResponse])
async def list_intelligence_reports(
    geography_id: Optional[int] = Query(None),
    service_category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """List intelligence reports with optional filters"""
    query = db.query(IntelligenceReport).filter(IntelligenceReport.client_id == client_id)
    
    if geography_id:
        query = query.filter(IntelligenceReport.geography_id == geography_id)
    
    if service_category:
        query = query.filter(IntelligenceReport.service_category == service_category)
    
    reports = query.order_by(IntelligenceReport.generated_at.desc()).offset(offset).limit(limit).all()
    return reports


@router.get("/reports/{report_id}", response_model=IntelligenceReportResponse)
async def get_intelligence_report(
    report_id: int,
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Get a specific intelligence report"""
    report = db.query(IntelligenceReport).filter(
        IntelligenceReport.id == report_id,
        IntelligenceReport.client_id == client_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/buyer-profile", response_model=BuyerProfileResponse)
async def generate_buyer_profile(
    geography_id: Optional[int] = Query(None),
    zip_codes: Optional[str] = Query(None),  # Comma-separated
    service_category: str = Query("general"),
    min_demand_score: float = Query(0.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
    client_id: uuid.UUID = Depends(get_current_active_client_id)
):
    """Generate buyer profile for given geography and service category"""
    engine = IntelligenceEngine(db)
    
    zip_code_ids = None
    if zip_codes:
        zip_code_list = [z.strip() for z in zip_codes.split(",")]
        zip_codes_obj = db.query(ZIPCode).filter(ZIPCode.zip_code.in_(zip_code_list)).all()
        zip_code_ids = [zc.id for zc in zip_codes_obj]
    
    try:
        service_cat = ServiceCategory(service_category)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service category")
    
    households = engine.get_households_by_geography(
        client_id=client_id,
        geography_id=geography_id,
        zip_code_ids=zip_code_ids,
        service_category=service_cat,
        min_demand_score=min_demand_score
    )
    
    profile = engine.generate_buyer_profile(households, service_cat)
    return BuyerProfileResponse(**profile)


def _generate_channel_recommendations(
    buyer_profile: dict,
    service_category: ServiceCategory,
    db: Session,
    client_id: uuid.UUID,
    geography_id: int
) -> List[dict]:
    """Generate channel recommendations based on buyer profile and available channels"""
    from app.models.channel import Channel
    
    recommendations = []
    
    # Get channels from database for this geography
    channels = db.query(Channel).filter(
        Channel.client_id == client_id,
        Channel.geography_id == geography_id
    ).all()
    
    # Add institutional channels from database
    for channel in channels:
        recommendations.append({
            "channel_type": channel.channel_type.value,
            "name": channel.name,
            "rationale": f"Institutional channel: {channel.name}",
            "estimated_reach": channel.estimated_reach or "Unknown",
            "website": channel.website,
            "source_url": channel.source_url
        })
    
    # Add generic recommendations if no channels found
    if not channels:
        # Direct mail for homeowners
        if buyer_profile.get("homeowner_percentage", 0) > 60:
            recommendations.append({
                "channel_type": "direct_mail",
                "rationale": "High percentage of homeowners who respond well to direct mail",
                "estimated_reach": buyer_profile.get("target_households", 0),
                "estimated_cost_range": "$0.50-$1.00 per household"
            })
        
        # Digital ads for higher income areas
        income_dist = buyer_profile.get("income_distribution", {})
        if income_dist.get("high", 0) > income_dist.get("low", 0):
            recommendations.append({
                "channel_type": "digital_ads",
                "rationale": "Higher income demographic active online",
                "estimated_reach": buyer_profile.get("target_households", 0) * 3,
                "estimated_cost_range": "$2-$5 per 1000 impressions"
            })
        
        # Door hangers for local services
        if service_category in [ServiceCategory.LAWN_CARE, ServiceCategory.SECURITY]:
            recommendations.append({
                "channel_type": "door_hangers",
                "rationale": "Effective for local service providers in residential areas",
                "estimated_reach": buyer_profile.get("target_households", 0),
                "estimated_cost_range": "$0.15-$0.30 per household"
            })
    
    return recommendations


def _generate_timing_recommendations(
    service_category: ServiceCategory,
    demand_score: float
) -> List[dict]:
    """Generate timing recommendations based on service category"""
    recommendations = []
    
    if service_category == ServiceCategory.LAWN_CARE:
        recommendations.extend([
            {
                "time_period": "Spring (March-May)",
                "rationale": "Peak season for lawn care services as grass begins growing",
                "demand_score": min(100.0, demand_score * 1.3),
                "recommended_actions": [
                    "Launch campaigns in early March",
                    "Focus on fertilization and aeration services",
                    "Target new homeowners"
                ]
            },
            {
                "time_period": "Summer (June-August)",
                "rationale": "Ongoing maintenance season with high demand",
                "demand_score": demand_score,
                "recommended_actions": [
                    "Maintain consistent messaging",
                    "Offer seasonal packages",
                    "Target properties with larger lots"
                ]
            }
        ])
    elif service_category == ServiceCategory.FIREWORKS:
        recommendations.append({
            "time_period": "Late June - Early July",
            "rationale": "Fourth of July holiday peak demand",
            "demand_score": min(100.0, demand_score * 1.5),
            "recommended_actions": [
                "Begin marketing 2-3 weeks before holiday",
                "Focus on neighborhoods with larger lots",
                "Highlight safety and compliance"
            ]
        })
    else:
        recommendations.append({
            "time_period": "Year-round",
            "rationale": "Consistent demand throughout the year",
            "demand_score": demand_score,
            "recommended_actions": [
                "Maintain consistent presence",
                "Adjust messaging seasonally",
                "Focus on property turnover events"
            ]
        })
    
    return recommendations

