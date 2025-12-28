"""
ICS Calendar Collector (Option 3: Public Signals Ingestion)
Parses ICS calendar feeds for event data
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import requests
import icalendar
from io import BytesIO
from app.collectors.base_collector import BaseCollector
from app.core.pii_guard import assert_no_pii_keys
from app.models.demand_signal import DemandSignal, ServiceCategory, SignalType
from app.models.geography import Geography, ZIPCode
import uuid
import json


class ICSCalendarCollector(BaseCollector):
    """
    Collects event data from ICS calendar feeds
    Option 3: Public Signals Ingestion
    """
    
    def __init__(self, db: Session, client_id: uuid.UUID):
        super().__init__(db)
        self.client_id = client_id
    
    def collect(
        self,
        ics_url: str,
        geography_id: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Collect events from an ICS calendar feed
        """
        data = []
        
        try:
            # Fetch ICS file
            response = requests.get(ics_url, timeout=10)
            response.raise_for_status()
            
            # Parse ICS file
            calendar = icalendar.Calendar.from_ical(response.content)
            
            for component in calendar.walk():
                if component.name == "VEVENT":
                    event_data = self._parse_event(component, geography_id)
                    if event_data:
                        # Validate for PII
                        assert_no_pii_keys(event_data)
                        data.append(event_data)
        
        except Exception as e:
            print(f"Error fetching/parsing ICS calendar: {e}")
            return []
        
        return data
    
    def _parse_event(self, event_component, geography_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Parse a single VEVENT component"""
        try:
            event_data = {
                "event_name": str(event_component.get("SUMMARY", "")),
                "event_description": str(event_component.get("DESCRIPTION", "")),
                "source": "ics_calendar",
                "source_url": None,  # ICS file URL
            }
            
            # Parse dates
            dtstart = event_component.get("DTSTART")
            dtend = event_component.get("DTEND")
            
            if dtstart:
                dt = dtstart.dt
                if isinstance(dt, datetime):
                    event_data["event_start_date"] = dt.isoformat()
                else:
                    event_data["event_start_date"] = datetime.combine(dt, datetime.min.time()).isoformat()
            
            if dtend:
                dt = dtend.dt
                if isinstance(dt, datetime):
                    event_data["event_end_date"] = dt.isoformat()
                else:
                    event_data["event_end_date"] = datetime.combine(dt, datetime.min.time()).isoformat()
            
            # Parse location
            location = event_component.get("LOCATION")
            if location:
                event_data["location_name"] = str(location)
                # Try to extract ZIP code from location string
                import re
                zip_match = re.search(r'\b\d{5}(-\d{4})?\b', str(location))
                if zip_match:
                    event_data["zip_code"] = zip_match.group(0).split("-")[0]
            
            # Determine service category
            event_data["service_category"] = self._map_to_service_category(
                event_data["event_name"],
                event_data.get("event_description", "")
            )
            
            event_data["geography_id"] = geography_id
            
            return event_data
        
        except Exception as e:
            print(f"Error parsing event: {e}")
            return None
    
    def _map_to_service_category(self, title: str, description: str) -> str:
        """Map event to service category"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ["firework", "4th", "july", "independence"]):
            return ServiceCategory.FIREWORKS.value
        elif any(word in text for word in ["park", "festival", "outdoor", "lawn"]):
            return ServiceCategory.LAWN_CARE.value
        elif any(word in text for word in ["security", "safety"]):
            return ServiceCategory.SECURITY.value
        else:
            return ServiceCategory.GENERAL.value
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate event data"""
        required_fields = ["event_name", "event_start_date"]
        return all(field in data for field in required_fields)
    
    def store(self, data: List[Dict[str, Any]], geography_id: Optional[int] = None) -> int:
        """Store collected events as DemandSignals"""
        stored = 0
        
        for event in data:
            if not self.validate_data(event):
                continue
            
            # Get ZIP code if provided
            zip_code_id = None
            if event.get("zip_code"):
                zip_obj = self.db.query(ZIPCode).filter(
                    ZIPCode.zip_code == event["zip_code"]
                ).first()
                if zip_obj:
                    zip_code_id = zip_obj.id
            
            # Parse dates
            start_date = None
            end_date = None
            try:
                if event.get("event_start_date"):
                    start_date = datetime.fromisoformat(event["event_start_date"].replace("Z", "+00:00"))
                if event.get("event_end_date"):
                    end_date = datetime.fromisoformat(event["event_end_date"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
            
            # Create demand signal
            signal = DemandSignal(
                client_id=self.client_id,
                geography_id=geography_id or event.get("geography_id"),
                zip_code_id=zip_code_id,
                signal_type=SignalType.EVENT,
                service_category=ServiceCategory(event.get("service_category", "general")),
                title=event["event_name"],
                description=event.get("event_description"),
                event_start_date=start_date,
                event_end_date=end_date,
                source_name="ics_calendar",
                source_url=event.get("source_url"),
                signal_metadata=json.dumps({
                    "source": "ics_calendar",
                    "location": event.get("location_name"),
                })
            )
            self.db.add(signal)
            stored += 1
        
        self.db.commit()
        return stored

