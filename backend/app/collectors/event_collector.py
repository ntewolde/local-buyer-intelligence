"""
Event Data Collector
Collects public event calendars (city, schools, parks)
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.collectors.base_collector import BaseCollector
from app.models.demand_signal import DemandSignal, ServiceCategory, SignalType
from app.models.geography import Geography
import requests


class EventCollector(BaseCollector):
    """
    Collects public event data from city calendars, school calendars, park calendars
    Creates demand signals for services related to events
    """
    
    def collect(
        self,
        geography_id: Optional[int] = None,
        city_name: Optional[str] = None,
        state_code: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Collect event data from public calendars
        """
        data = []
        
        # Note: This is a template implementation
        # Actual implementation would:
        # 1. Connect to city event calendar APIs/feeds
        # 2. Connect to school district calendar APIs
        # 3. Connect to park district calendars
        # 4. Filter events by date range
        # 5. Map events to service categories
        # 6. Extract location (ZIP code if available)
        
        # Example event structure:
        # {
        #     "event_title": "Summer Festival",
        #     "event_description": "Annual city summer festival",
        #     "event_start_date": "2024-07-04T00:00:00Z",
        #     "event_end_date": "2024-07-04T23:59:59Z",
        #     "zip_code": "12345",
        #     "location_name": "City Park",
        #     "latitude": 40.7128,
        #     "longitude": -74.0060,
        #     "service_categories": ["fireworks", "food_vendors"],
        #     "source": "city_calendar"
        # }
        
        return data
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate event data"""
        required_fields = ["event_title", "event_start_date"]
        if not all(field in data for field in required_fields):
            return False
        
        # Validate date format
        if isinstance(data["event_start_date"], str):
            try:
                datetime.fromisoformat(data["event_start_date"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return False
        
        return True
    
    def _map_event_to_service_category(self, event: Dict[str, Any]) -> List[ServiceCategory]:
        """Map event characteristics to service categories"""
        categories = []
        title = event.get("event_title", "").lower()
        description = event.get("event_description", "").lower()
        
        # Fireworks events
        if any(word in title + description for word in ["firework", "4th", "july", "independence"]):
            categories.append(ServiceCategory.FIREWORKS)
        
        # Lawn care (community events in parks)
        if any(word in title + description for word in ["park", "festival", "outdoor"]):
            categories.append(ServiceCategory.LAWN_CARE)
        
        # General services
        if not categories:
            categories.append(ServiceCategory.GENERAL)
        
        return categories
    
    def store(self, data: List[Dict[str, Any]]) -> int:
        """Store events as demand signals"""
        stored = 0
        
        for item in data:
            # Get geography/ZIP code
            zip_code_str = item.get("zip_code")
            geography_id = item.get("geography_id")
            
            # Map to service categories
            service_categories = item.get("service_categories", [])
            if not service_categories:
                service_categories = self._map_event_to_service_category(item)
            
            # Create demand signal for each service category
            for service_cat_str in service_categories:
                try:
                    service_cat = ServiceCategory(service_cat_str) if isinstance(service_cat_str, str) else service_cat_str
                except ValueError:
                    continue
                
                signal_data = {
                    "signal_type": SignalType.EVENT,
                    "service_category": service_cat,
                    "title": item.get("event_title"),
                    "description": item.get("event_description"),
                    "source_name": item.get("source", "event_calendar"),
                    "source_url": item.get("source_url"),
                }
                
                # Dates
                if "event_start_date" in item:
                    signal_data["event_start_date"] = item["event_start_date"]
                if "event_end_date" in item:
                    signal_data["event_end_date"] = item["event_end_date"]
                
                # Geography
                if geography_id:
                    signal_data["geography_id"] = geography_id
                
                # Coordinates
                if "latitude" in item:
                    signal_data["latitude"] = item["latitude"]
                if "longitude" in item:
                    signal_data["longitude"] = item["longitude"]
                
                # Demand score (could be calculated based on event size, type, etc.)
                signal_data["demand_score"] = item.get("demand_score", 50.0)
                
                signal = DemandSignal(**signal_data)
                self.db.add(signal)
                stored += 1
        
        self.db.commit()
        return stored

