"""
Property/Assessor Data Collector
Collects public property records (no PII - only property characteristics)
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.collectors.base_collector import BaseCollector
from app.models.household import Household, PropertyType, OwnershipType
from app.models.geography import ZIPCode
import re


class PropertyCollector(BaseCollector):
    """
    Collects property assessor data from public records
    NO PII - only property characteristics, ownership type, size, etc.
    """
    
    def collect(
        self,
        geography_id: Optional[int] = None,
        zip_codes: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Collect property records from public assessor data
        Returns property characteristics (no owner names, emails, phones)
        """
        # Note: This is a template implementation
        # Actual implementation depends on local assessor data availability
        # Many cities/states provide open data portals with property records
        
        data = []
        
        # Example data structure (actual would come from assessor database/API):
        # {
        #     "property_id": "12345",
        #     "zip_code": "12345",
        #     "property_type": "single_family",
        #     "ownership_type": "owner",  # inferred from tax records
        #     "sqft": 2500,
        #     "lot_size_sqft": 8000,
        #     "income_band_min": 50000,  # from census block data
        #     "income_band_max": 75000,
        #     "property_age_years": 15,
        #     "last_sale_year": 2015,
        #     "latitude": 40.7128,
        #     "longitude": -74.0060,
        # }
        
        # Implementation would:
        # 1. Connect to assessor database/API
        # 2. Filter by geography/ZIP
        # 3. Extract ONLY property characteristics (no names, emails, phones)
        # 4. Aggregate income data from census blocks (not individual records)
        # 5. Return structured data
        
        return data
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate property data"""
        # Must have at least zip_code and property_type
        required_fields = ["zip_code"]
        if not all(field in data for field in required_fields):
            return False
        
        # Validate property_type if present
        if "property_type" in data:
            try:
                PropertyType(data["property_type"])
            except ValueError:
                return False
        
        return True
    
    def store(self, data: List[Dict[str, Any]]) -> int:
        """Store property data as household records"""
        stored = 0
        
        for item in data:
            # Get ZIP code
            zip_code_str = item.get("zip_code")
            if not zip_code_str:
                continue
            
            zip_obj = self.db.query(ZIPCode).filter(ZIPCode.zip_code == zip_code_str).first()
            if not zip_obj:
                continue  # Skip if ZIP code doesn't exist
            
            # Create household record
            household_data = {
                "zip_code_id": zip_obj.id,
                "geography_id": zip_obj.geography_id,
                "data_source": "property_assessor",
            }
            
            # Map property type
            if "property_type" in item:
                try:
                    household_data["property_type"] = PropertyType(item["property_type"])
                except ValueError:
                    household_data["property_type"] = PropertyType.UNKNOWN
            
            # Map ownership type
            if "ownership_type" in item:
                try:
                    household_data["ownership_type"] = OwnershipType(item["ownership_type"])
                except ValueError:
                    household_data["ownership_type"] = OwnershipType.UNKNOWN
            
            # Property size
            if "sqft" in item:
                sqft = item["sqft"]
                household_data["property_sqft_min"] = sqft
                household_data["property_sqft_max"] = sqft
            
            # Lot size
            if "lot_size_sqft" in item:
                household_data["lot_size_sqft"] = item["lot_size_sqft"]
            
            # Income band
            if "income_band_min" in item:
                household_data["income_band_min"] = item["income_band_min"]
            if "income_band_max" in item:
                household_data["income_band_max"] = item["income_band_max"]
            
            # Geographic coordinates
            if "latitude" in item:
                household_data["latitude"] = item["latitude"]
            if "longitude" in item:
                household_data["longitude"] = item["longitude"]
            
            # Timing indicators
            if "property_age_years" in item:
                household_data["property_age_years"] = item["property_age_years"]
            if "last_sale_year" in item:
                household_data["last_sale_year"] = item["last_sale_year"]
            
            household = Household(**household_data)
            self.db.add(household)
            stored += 1
        
        self.db.commit()
        return stored






