"""
Intelligence Engine Service
Calculates demand scores and generates buyer profiles
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.household import Household, PropertyType, OwnershipType
from app.models.demand_signal import ServiceCategory
from app.models.geography import ZIPCode
from sqlalchemy import func, and_
import uuid


class IntelligenceEngine:
    """Service for generating intelligence reports and demand scores"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_household_demand_score(
        self,
        household: Household,
        service_category: ServiceCategory
    ) -> float:
        """
        Calculate demand score for a household based on service category
        Returns score from 0-100
        """
        score = 0.0
        
        if service_category == ServiceCategory.LAWN_CARE:
            score = self._calculate_lawn_care_score(household)
        elif service_category == ServiceCategory.SECURITY:
            score = self._calculate_security_score(household)
        elif service_category == ServiceCategory.IT_SERVICES:
            score = self._calculate_it_services_score(household)
        elif service_category == ServiceCategory.FIREWORKS:
            score = self._calculate_fireworks_score(household)
        else:
            score = self._calculate_general_service_score(household)
        
        return min(100.0, max(0.0, score))
    
    def _calculate_lawn_care_score(self, household: Household) -> float:
        """Calculate lawn care demand score"""
        score = 0.0
        
        # Ownership (owners more likely to use lawn care)
        if household.ownership_type == OwnershipType.OWNER:
            score += 40.0
        elif household.ownership_type == OwnershipType.RENTER:
            score += 10.0
        
        # Lot size (larger lots need more care)
        if household.lot_size_sqft:
            if household.lot_size_sqft > 10000:
                score += 30.0
            elif household.lot_size_sqft > 5000:
                score += 20.0
            elif household.lot_size_sqft > 2500:
                score += 10.0
        
        # Property type
        if household.property_type == PropertyType.SINGLE_FAMILY:
            score += 20.0
        elif household.property_type == PropertyType.MULTI_FAMILY:
            score += 10.0
        
        # Income (higher income more likely to outsource)
        if household.income_band_min and household.income_band_max:
            avg_income = (household.income_band_min + household.income_band_max) / 2
            if avg_income > 75000:
                score += 10.0
            elif avg_income > 50000:
                score += 5.0
        
        return score
    
    def _calculate_security_score(self, household: Household) -> float:
        """Calculate security services demand score"""
        score = 0.0
        
        # Ownership (owners invest in security)
        if household.ownership_type == OwnershipType.OWNER:
            score += 50.0
        elif household.ownership_type == OwnershipType.RENTER:
            score += 5.0
        
        # Property value proxy (income band)
        if household.income_band_min and household.income_band_max:
            avg_income = (household.income_band_min + household.income_band_max) / 2
            if avg_income > 100000:
                score += 30.0
            elif avg_income > 50000:
                score += 15.0
        
        # Property type
        if household.property_type == PropertyType.SINGLE_FAMILY:
            score += 20.0
        
        return score
    
    def _calculate_it_services_score(self, household: Household) -> float:
        """Calculate IT services demand score"""
        score = 0.0
        
        # Income (higher income = more tech)
        if household.income_band_min and household.income_band_max:
            avg_income = (household.income_band_min + household.income_band_max) / 2
            if avg_income > 75000:
                score += 50.0
            elif avg_income > 50000:
                score += 30.0
            else:
                score += 10.0
        
        # Property type (home offices)
        if household.property_type == PropertyType.SINGLE_FAMILY:
            score += 30.0
        
        # Property size (larger = more likely home office)
        if household.property_sqft_min and household.property_sqft_min > 2000:
            score += 20.0
        
        return score
    
    def _calculate_fireworks_score(self, household: Household) -> float:
        """Calculate fireworks demand score"""
        score = 0.0
        
        # Ownership (owners host events)
        if household.ownership_type == OwnershipType.OWNER:
            score += 40.0
        
        # Lot size (larger lots for events)
        if household.lot_size_sqft and household.lot_size_sqft > 5000:
            score += 30.0
        
        # Income (discretionary spending)
        if household.income_band_min and household.income_band_max:
            avg_income = (household.income_band_min + household.income_band_max) / 2
            if avg_income > 50000:
                score += 30.0
        
        return score
    
    def _calculate_general_service_score(self, household: Household) -> float:
        """Calculate general service demand score"""
        score = 50.0  # Base score
        
        # Ownership
        if household.ownership_type == OwnershipType.OWNER:
            score += 20.0
        
        # Income
        if household.income_band_min and household.income_band_max:
            avg_income = (household.income_band_min + household.income_band_max) / 2
            if avg_income > 75000:
                score += 20.0
            elif avg_income > 50000:
                score += 10.0
        
        return score
    
    def get_households_by_geography(
        self,
        client_id: uuid.UUID,
        geography_id: Optional[int] = None,
        zip_code_ids: Optional[List[int]] = None,
        service_category: ServiceCategory = ServiceCategory.GENERAL,
        min_demand_score: float = 0.0
    ) -> List[Household]:
        """Get households filtered by geography and demand score"""
        query = self.db.query(Household).filter(Household.client_id == client_id)
        
        if geography_id:
            query = query.filter(Household.geography_id == geography_id)
        
        if zip_code_ids:
            query = query.filter(Household.zip_code_id.in_(zip_code_ids))
        
        households = query.all()
        
        # Also consider DemandSignal data for scoring
        # Get demographic signals that might affect scoring
        from app.models.demand_signal import DemandSignal, SignalType
        signals = self.db.query(DemandSignal).filter(
            DemandSignal.client_id == client_id,
            DemandSignal.geography_id == geography_id,
            DemandSignal.signal_type == SignalType.DEMOGRAPHIC
        ).all()
        
        # Filter by demand score
        filtered = []
        for household in households:
            score = self.calculate_household_demand_score(household, service_category)
            
            # Boost score based on demographic signals (income, population density)
            for signal in signals:
                if signal.zip_code_id == household.zip_code_id:
                    # If median income signal, boost score for higher income areas
                    if "income" in (signal.metadata or "").lower() and signal.value:
                        if signal.value > 75000:
                            score += 5.0
                        elif signal.value > 50000:
                            score += 2.0
            
            if score >= min_demand_score:
                filtered.append(household)
        
        return filtered
    
    def generate_buyer_profile(
        self,
        households: List[Household],
        service_category: ServiceCategory
    ) -> Dict[str, Any]:
        """Generate buyer profile from household list"""
        if not households:
            return {
                "total_households": 0,
                "target_households": 0,
                "homeowner_percentage": 0.0,
                "renter_percentage": 0.0,
                "property_types": {},
                "income_distribution": {},
                "average_property_age": 0.0,
                "average_lot_size": 0.0,
            }
        
        total = len(households)
        owners = sum(1 for h in households if h.ownership_type == OwnershipType.OWNER)
        renters = sum(1 for h in households if h.ownership_type == OwnershipType.RENTER)
        
        property_types = {}
        for h in households:
            prop_type = h.property_type.value if h.property_type else "unknown"
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        # Income distribution (simplified)
        income_dist = {"low": 0, "medium": 0, "high": 0}
        for h in households:
            if h.income_band_min and h.income_band_max:
                avg = (h.income_band_min + h.income_band_max) / 2
                if avg > 75000:
                    income_dist["high"] += 1
                elif avg > 50000:
                    income_dist["medium"] += 1
                else:
                    income_dist["low"] += 1
        
        ages = [h.property_age_years for h in households if h.property_age_years]
        avg_age = sum(ages) / len(ages) if ages else 0.0
        
        lot_sizes = [h.lot_size_sqft for h in households if h.lot_size_sqft]
        avg_lot = sum(lot_sizes) / len(lot_sizes) if lot_sizes else 0.0
        
        return {
            "total_households": total,
            "target_households": total,  # Could filter by score if needed
            "homeowner_percentage": (owners / total * 100) if total > 0 else 0.0,
            "renter_percentage": (renters / total * 100) if total > 0 else 0.0,
            "property_types": property_types,
            "income_distribution": income_dist,
            "average_property_age": avg_age,
            "average_lot_size": avg_lot,
        }
    
    def calculate_zip_demand_scores(
        self,
        client_id: uuid.UUID,
        zip_code_ids: List[int],
        service_category: ServiceCategory
    ) -> Dict[str, float]:
        """Calculate demand scores by ZIP code"""
        zip_codes = self.db.query(ZIPCode).filter(ZIPCode.id.in_(zip_code_ids)).all()
        scores = {}
        
        # Get demographic signals for ZIP codes
        from app.models.demand_signal import DemandSignal, SignalType
        signals_by_zip = {}
        signals = self.db.query(DemandSignal).filter(
            DemandSignal.client_id == client_id,
            DemandSignal.zip_code_id.in_(zip_code_ids),
            DemandSignal.signal_type == SignalType.DEMOGRAPHIC
        ).all()
        for signal in signals:
            if signal.zip_code_id not in signals_by_zip:
                signals_by_zip[signal.zip_code_id] = []
            signals_by_zip[signal.zip_code_id].append(signal)
        
        for zip_code in zip_codes:
            households = self.db.query(Household).filter(
                Household.client_id == client_id,
                Household.zip_code_id == zip_code.id
            ).all()
            
            if not households:
                scores[zip_code.zip_code] = 0.0
                continue
            
            total_score = sum(
                self.calculate_household_demand_score(h, service_category)
                for h in households
            )
            avg_score = total_score / len(households) if households else 0.0
            
            # Boost based on demographic signals
            zip_signals = signals_by_zip.get(zip_code.id, [])
            for signal in zip_signals:
                if "income" in (signal.metadata or "").lower() and signal.value:
                    if signal.value > 75000:
                        avg_score += 5.0
                    elif signal.value > 50000:
                        avg_score += 2.0
            
            scores[zip_code.zip_code] = round(min(100.0, max(0.0, avg_score)), 2)
        
        return scores

