"""
CSV Import Service
Handles parsing and validation of CSV imports
"""
import csv
import io
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.pii_guard import assert_no_pii_keys, validate_csv_headers
from app.core.file_storage import get_file_path
from app.models.household import PropertyType, OwnershipType
from app.models.channel import ChannelType
from app.models.demand_signal import SignalType, ServiceCategory
from datetime import datetime
import json
import uuid


class CSVImportService:
    """Service for importing CSV data"""
    
    def __init__(self, db: Session, client_id: uuid.UUID):
        self.db = db
        self.client_id = client_id
    
    def parse_csv_file(self, file_ref: str) -> List[Dict[str, Any]]:
        """
        Parse CSV file and return list of dictionaries
        """
        file_path = get_file_path(file_ref)
        if not file_path or not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_ref}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            
            # Validate headers for PII
            validate_csv_headers(headers)
            
            # Read all rows
            rows = []
            for row in reader:
                # Clean row (remove None values from CSV parsing)
                clean_row = {k: v for k, v in row.items() if v and v.strip()}
                
                # Validate row for PII
                assert_no_pii_keys(clean_row)
                
                rows.append(clean_row)
            
            return rows
    
    def import_property_csv(
        self,
        rows: List[Dict[str, Any]],
        geography_id: int
    ) -> int:
        """
        Import property CSV data as Household records or aggregated signals
        Uses aggregation strategy: store as signals grouped by ZIP/property type
        """
        from app.models.household import Household
        from app.models.geography import ZIPCode, Geography
        from app.models.demand_signal import DemandSignal
        
        imported = 0
        
        # Group by zip_code, property_type, ownership_type for aggregation
        aggregates = {}
        
        for row in rows:
            zip_code_str = row.get("zip_code", "").strip()
            if not zip_code_str:
                continue
            
            # Get ZIP code
            zip_obj = self.db.query(ZIPCode).filter(
                ZIPCode.zip_code == zip_code_str
            ).first()
            
            if not zip_obj:
                # Create ZIP code if geography provided
                if geography_id:
                    zip_obj = ZIPCode(
                        zip_code=zip_code_str,
                        geography_id=geography_id
                    )
                    self.db.add(zip_obj)
                    self.db.flush()
                else:
                    continue
            
            # Parse property type
            prop_type_str = row.get("property_type", "").strip().upper()
            prop_type = None
            if prop_type_str:
                try:
                    prop_type = PropertyType[prop_type_str]
                except (KeyError, ValueError):
                    prop_type = PropertyType.UNKNOWN
            
            # Parse ownership type
            own_type_str = row.get("ownership_type", "").strip().upper()
            own_type = None
            if own_type_str:
                try:
                    # Handle OWNER_OCCUPIED -> OWNER
                    if "OWNER" in own_type_str:
                        own_type = OwnershipType.OWNER
                    elif "RENTER" in own_type_str:
                        own_type = OwnershipType.RENTER
                    else:
                        own_type = OwnershipType[own_type_str]
                except (KeyError, ValueError):
                    own_type = OwnershipType.UNKNOWN
            
            # Create aggregate key
            agg_key = f"{zip_code_str}:{prop_type.value if prop_type else 'unknown'}:{own_type.value if own_type else 'unknown'}"
            
            if agg_key not in aggregates:
                aggregates[agg_key] = {
                    "zip_code": zip_code_str,
                    "zip_obj": zip_obj,
                    "property_type": prop_type,
                    "ownership_type": own_type,
                    "count": 0,
                    "lot_sizes": [],
                    "years_built": [],
                    "income_bands": [],
                }
            
            aggregates[agg_key]["count"] += 1
            
            # Collect numeric fields
            if row.get("lot_size_sqft"):
                try:
                    aggregates[agg_key]["lot_sizes"].append(int(row["lot_size_sqft"]))
                except (ValueError, TypeError):
                    pass
            
            if row.get("year_built"):
                try:
                    year = int(row["year_built"])
                    current_year = datetime.now().year
                    aggregates[agg_key]["years_built"].append(current_year - year)
                except (ValueError, TypeError):
                    pass
        
        # Create aggregated signals
        for agg_key, agg_data in aggregates.items():
            # Calculate averages
            avg_lot_size = sum(agg_data["lot_sizes"]) / len(agg_data["lot_sizes"]) if agg_data["lot_sizes"] else None
            avg_age = sum(agg_data["years_built"]) / len(agg_data["years_built"]) if agg_data["years_built"] else None
            
            # Create signal with aggregated data
            metadata = {
                "source": "csv_import",
                "property_type": agg_data["property_type"].value if agg_data["property_type"] else None,
                "ownership_type": agg_data["ownership_type"].value if agg_data["ownership_type"] else None,
                "count": agg_data["count"],
                "avg_lot_size_sqft": avg_lot_size,
                "avg_property_age_years": avg_age,
            }
            
            signal = DemandSignal(
                client_id=self.client_id,
                geography_id=geography_id,
                zip_code_id=agg_data["zip_obj"].id if agg_data["zip_obj"] else None,
                signal_type=SignalType.CUSTOM,
                service_category=ServiceCategory.GENERAL,
                title=f"Property Aggregate: {agg_data['zip_code']}",
                value=float(agg_data["count"]),
                source_name="csv_property_import",
                signal_metadata=json.dumps(metadata)
            )
            self.db.add(signal)
            imported += 1
        
        # Update geography freshness
        if geography_id:
            geography = self.db.query(Geography).filter(Geography.id == geography_id).first()
            if geography:
                geography.property_last_refreshed_at = datetime.utcnow()
        
        self.db.commit()
        return imported
    
    def import_events_csv(
        self,
        rows: List[Dict[str, Any]],
        geography_id: int
    ) -> int:
        """Import events CSV as DemandSignal rows"""
        from app.models.demand_signal import DemandSignal
        from app.models.geography import ZIPCode, Geography
        
        imported = 0
        
        for row in rows:
            event_name = row.get("event_name", "").strip()
            if not event_name:
                continue
            
            # Parse dates
            start_date = None
            end_date = None
            try:
                if row.get("start_date"):
                    start_date = datetime.fromisoformat(row["start_date"].replace("Z", "+00:00"))
                if row.get("end_date"):
                    end_date = datetime.fromisoformat(row["end_date"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
            
            # Get ZIP code if provided
            zip_code_id = None
            if row.get("zip_code"):
                zip_obj = self.db.query(ZIPCode).filter(
                    ZIPCode.zip_code == row["zip_code"].strip()
                ).first()
                if zip_obj:
                    zip_code_id = zip_obj.id
            
            # Determine service category from event category
            category = row.get("category", "").lower()
            service_cat = ServiceCategory.GENERAL
            if "firework" in category or "4th" in category or "july" in category:
                service_cat = ServiceCategory.FIREWORKS
            elif "outdoor" in category or "park" in category:
                service_cat = ServiceCategory.LAWN_CARE
            
            # Create demand signal
            signal = DemandSignal(
                client_id=self.client_id,
                geography_id=geography_id,
                zip_code_id=zip_code_id,
                signal_type=SignalType.EVENT,
                service_category=service_cat,
                title=event_name,
                event_start_date=start_date,
                event_end_date=end_date,
                source_name="csv_events_import",
                source_url=row.get("source_url"),
                metadata=json.dumps({
                    "source": "csv_import",
                    "category": row.get("category"),
                    "estimated_attendance": row.get("estimated_attendance"),
                })
            )
            self.db.add(signal)
            imported += 1
        
        # Update geography freshness
        if geography_id:
            geography = self.db.query(Geography).filter(Geography.id == geography_id).first()
            if geography:
                geography.events_last_refreshed_at = datetime.utcnow()
        
        self.db.commit()
        return imported
    
    def import_channels_csv(
        self,
        rows: List[Dict[str, Any]],
        geography_id: int
    ) -> int:
        """Import channels CSV as Channel rows with deduplication"""
        from app.models.channel import Channel
        from app.models.geography import Geography
        
        imported = 0
        
        for row in rows:
            name = row.get("name", "").strip()
            channel_type_str = row.get("channel_type", "").strip().upper()
            
            if not name or not channel_type_str:
                continue
            
            # Parse channel type
            try:
                channel_type = ChannelType[channel_type_str]
            except (KeyError, ValueError):
                continue
            
            # Deduplication: check if channel already exists
            existing = self.db.query(Channel).filter(
                Channel.client_id == self.client_id,
                Channel.geography_id == geography_id,
                Channel.channel_type == channel_type,
                Channel.name == name
            ).first()
            
            if existing:
                # Update existing channel
                if row.get("city"):
                    existing.city = row["city"]
                if row.get("state"):
                    existing.state = row["state"]
                if row.get("zip_code"):
                    existing.zip_code = row["zip_code"]
                if row.get("estimated_reach"):
                    try:
                        existing.estimated_reach = int(row["estimated_reach"])
                    except (ValueError, TypeError):
                        pass
                if row.get("website"):
                    existing.website = row["website"]
                if row.get("source_url"):
                    existing.source_url = row["source_url"]
                if row.get("notes"):
                    existing.notes = row["notes"]
                existing.updated_at = datetime.utcnow()
            else:
                # Create new channel
                channel = Channel(
                    client_id=self.client_id,
                    geography_id=geography_id,
                    channel_type=channel_type,
                    name=name,
                    city=row.get("city"),
                    state=row.get("state"),
                    zip_code=row.get("zip_code"),
                    website=row.get("website"),
                    source_url=row.get("source_url"),
                    notes=row.get("notes"),
                )
                if row.get("estimated_reach"):
                    try:
                        channel.estimated_reach = int(row["estimated_reach"])
                    except (ValueError, TypeError):
                        pass
                
                self.db.add(channel)
                imported += 1
        
        # Update geography freshness
        if geography_id:
            geography = self.db.query(Geography).filter(Geography.id == geography_id).first()
            if geography:
                geography.channels_last_refreshed_at = datetime.utcnow()
        
        self.db.commit()
        return imported

