"""
Census Data Collector
Collects aggregate census data (no PII) using US Census Bureau API
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import requests
import time
import json
from app.collectors.base_collector import BaseCollector
from app.core.pii_guard import assert_no_pii_keys
from app.models.demand_signal import DemandSignal, SignalType, ServiceCategory
from app.models.geography import Geography, ZIPCode
from app.models.ingestion import IngestionRun, SourceType, IngestionStatus
import uuid


class CensusCollector(BaseCollector):
    """
    Collects census-derived aggregate data by ZIP code using US Census Bureau API
    Uses ACS 5-year estimates
    """
    
    CENSUS_API_BASE = "https://api.census.gov/data"
    ACS5_YEAR = "2022"  # Most recent 5-year estimate year
    
    # Census variables to fetch (ACS 5-year)
    VARIABLES = {
        "B01003_001E": "total_population",
        "B25001_001E": "total_housing_units",
        "B19013_001E": "median_household_income",
        "B01002_001E": "median_age",
        "B25003_002E": "owner_occupied_units",
        "B25003_003E": "renter_occupied_units",
    }
    
    def __init__(self, db: Session, client_id: uuid.UUID):
        super().__init__(db)
        self.client_id = client_id
        self.rate_limit_delay = 0.2  # 200ms between requests (conservative)
    
    def collect(
        self,
        geography_id: Optional[int] = None,
        zip_codes: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Collect census data for given ZIP codes
        Returns list of census data records (non-PII aggregates)
        """
        data = []
        
        # Get ZIP codes to process
        if zip_codes:
            zip_code_list = zip_codes
        elif geography_id:
            geography = self.db.query(Geography).filter(
                Geography.id == geography_id,
                Geography.client_id == self.client_id
            ).first()
            if not geography:
                return []
            zip_code_list = [zc.zip_code for zc in geography.zip_codes]
        else:
            return []
        
        # Fetch data from Census API for each ZIP code
        for zip_code in zip_code_list:
            try:
                zip_data = self._fetch_census_data(zip_code)
                if zip_data:
                    zip_data["zip_code"] = zip_code
                    data.append(zip_data)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
            
            except Exception as e:
                # Log error but continue with other ZIP codes
                print(f"Error fetching census data for ZIP {zip_code}: {e}")
                continue
        
        return data
    
    def _fetch_census_data(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch census data for a single ZIP code
        Uses ACS 5-year estimates
        """
        url = f"{self.CENSUS_API_BASE}/{self.ACS5_YEAR}/acs/acs5"
        
        # Get variables as comma-separated list
        variables = ",".join(self.VARIABLES.keys())
        
        params = {
            "get": variables,
            "for": f"zip code tabulation area:{zip_code}",
            "key": None  # Census API doesn't require key for public data, but can add if needed
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Parse result (first row is headers, second row is data)
            if len(result) < 2:
                return None
            
            headers = result[0]
            values = result[1]
            
            # Create dictionary mapping variable codes to values
            data = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    value = values[i]
                    # Convert to appropriate type
                    try:
                        data[header] = int(value) if value and value != "-" else None
                    except (ValueError, TypeError):
                        data[header] = float(value) if value and value != "-" else None
            
            # Map to friendly names
            mapped_data = {
                "population": data.get("B01003_001E"),
                "total_housing_units": data.get("B25001_001E"),
                "median_household_income": data.get("B19013_001E"),
                "median_age": data.get("B01002_001E"),
                "owner_occupied_units": data.get("B25003_002E"),
                "renter_occupied_units": data.get("B25003_003E"),
            }
            
            return mapped_data
        
        except requests.exceptions.RequestException as e:
            print(f"Census API request failed for ZIP {zip_code}: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error parsing census data for ZIP {zip_code}: {e}")
            return None
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate census data"""
        # Check for PII (should never have any, but enforce guard)
        try:
            assert_no_pii_keys(data)
        except ValueError:
            return False
        
        # Must have zip_code
        if "zip_code" not in data:
            return False
        
        # Should have at least some data
        if not any(data.get(k) for k in ["population", "total_housing_units", "median_household_income"]):
            return False
        
        return True
    
    def store(
        self,
        data: List[Dict[str, Any]],
        geography_id: Optional[int] = None,
        ingestion_run_id: Optional[uuid.UUID] = None
    ) -> int:
        """
        Store census data as DemandSignal rows and update ZIPCode records
        """
        stored = 0
        
        # Update ingestion run status
        if ingestion_run_id:
            ingestion_run = self.db.query(IngestionRun).filter(
                IngestionRun.id == ingestion_run_id
            ).first()
            if ingestion_run:
                ingestion_run.status = IngestionStatus.RUNNING
                ingestion_run.started_at = datetime.utcnow()
                self.db.commit()
        
        for item in data:
            zip_code_str = item.get("zip_code")
            if not zip_code_str:
                continue
            
            # Get or create ZIP code record
            zip_obj = self.db.query(ZIPCode).filter(
                ZIPCode.zip_code == zip_code_str
            ).first()
            
            if not zip_obj:
                # Create ZIP code if it doesn't exist
                if geography_id:
                    zip_obj = ZIPCode(
                        zip_code=zip_code_str,
                        geography_id=geography_id
                    )
                    self.db.add(zip_obj)
                    self.db.flush()
            
            if zip_obj:
                # Update ZIP code statistics
                if item.get("population"):
                    zip_obj.population = item["population"]
                if item.get("total_housing_units"):
                    zip_obj.household_count = item["total_housing_units"]
                if item.get("median_household_income"):
                    zip_obj.median_income = item["median_household_income"]
                if item.get("median_age"):
                    zip_obj.median_age = item["median_age"]
            
            # Store as demand signals (demographic signals)
            # Store population signal
            if item.get("population"):
                signal = DemandSignal(
                    client_id=self.client_id,
                    geography_id=geography_id,
                    zip_code_id=zip_obj.id if zip_obj else None,
                    signal_type=SignalType.DEMOGRAPHIC,
                    service_category=ServiceCategory.GENERAL,
                    title="Total Population",
                    value=float(item["population"]),
                    source_name="census_acs5",
                    source_url=f"{self.CENSUS_API_BASE}/{self.ACS5_YEAR}/acs/acs5",
                    metadata=json.dumps({
                        "source": "census_acs5",
                        "variable": "B01003_001E",
                        "year": self.ACS5_YEAR,
                        "zip_code": zip_code_str
                    })
                )
                self.db.add(signal)
                stored += 1
            
            # Store median income signal
            if item.get("median_household_income"):
                signal = DemandSignal(
                    client_id=self.client_id,
                    geography_id=geography_id,
                    zip_code_id=zip_obj.id if zip_obj else None,
                    signal_type=SignalType.DEMOGRAPHIC,
                    service_category=ServiceCategory.GENERAL,
                    title="Median Household Income",
                    value=float(item["median_household_income"]),
                    source_name="census_acs5",
                    source_url=f"{self.CENSUS_API_BASE}/{self.ACS5_YEAR}/acs/acs5",
                    metadata=json.dumps({
                        "source": "census_acs5",
                        "variable": "B19013_001E",
                        "year": self.ACS5_YEAR,
                        "zip_code": zip_code_str
                    })
                )
                self.db.add(signal)
                stored += 1
        
        # Update geography freshness
        if geography_id:
            geography = self.db.query(Geography).filter(Geography.id == geography_id).first()
            if geography:
                geography.census_last_refreshed_at = datetime.utcnow()
        
        # Update ingestion run
        if ingestion_run_id:
            ingestion_run = self.db.query(IngestionRun).filter(
                IngestionRun.id == ingestion_run_id
            ).first()
            if ingestion_run:
                ingestion_run.status = IngestionStatus.SUCCESS
                ingestion_run.finished_at = datetime.utcnow()
                ingestion_run.records_upserted = stored
        
        self.db.commit()
        return stored
    
    def run(
        self,
        geography_id: int,
        ingestion_run_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run the full collection process with ingestion tracking
        """
        try:
            data = self.collect(geography_id=geography_id, **kwargs)
            validated_data = [d for d in data if self.validate_data(d)]
            stored_count = self.store(
                validated_data,
                geography_id=geography_id,
                ingestion_run_id=ingestion_run_id
            )
            
            return {
                "status": "success",
                "collected": len(data),
                "validated": len(validated_data),
                "stored": stored_count,
            }
        except Exception as e:
            # Update ingestion run on error
            if ingestion_run_id:
                ingestion_run = self.db.query(IngestionRun).filter(
                    IngestionRun.id == ingestion_run_id
                ).first()
                if ingestion_run:
                    ingestion_run.status = IngestionStatus.FAILED
                    ingestion_run.finished_at = datetime.utcnow()
                    ingestion_run.error_message = str(e)
                    self.db.commit()
            
            return {
                "status": "error",
                "error": str(e),
                "collected": 0,
                "validated": 0,
                "stored": 0,
            }
