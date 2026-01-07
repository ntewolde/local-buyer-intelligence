"""
Tests for Intelligence Engine Service
Tests demand scoring algorithms and buyer profile generation
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.intelligence_engine import IntelligenceEngine
from app.models.household import Household, PropertyType, OwnershipType
from app.models.demand_signal import ServiceCategory


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def engine(mock_db):
    """Create an IntelligenceEngine instance with mock db"""
    return IntelligenceEngine(mock_db)


def create_household(
    ownership_type=OwnershipType.OWNER,
    property_type=PropertyType.SINGLE_FAMILY,
    lot_size_sqft=None,
    income_band_min=None,
    income_band_max=None,
    property_sqft_min=None,
    property_sqft_max=None,
):
    """Helper to create a Household with specified attributes"""
    household = Household()
    household.ownership_type = ownership_type
    household.property_type = property_type
    household.lot_size_sqft = lot_size_sqft
    household.income_band_min = income_band_min
    household.income_band_max = income_band_max
    household.property_sqft_min = property_sqft_min
    household.property_sqft_max = property_sqft_max
    return household


class TestLawnCareDemandScore:
    """Tests for lawn care demand scoring"""

    def test_owner_gets_higher_base_score(self, engine):
        """Owners should score higher than renters for lawn care"""
        owner = create_household(ownership_type=OwnershipType.OWNER)
        renter = create_household(ownership_type=OwnershipType.RENTER)

        owner_score = engine.calculate_household_demand_score(owner, ServiceCategory.LAWN_CARE)
        renter_score = engine.calculate_household_demand_score(renter, ServiceCategory.LAWN_CARE)

        assert owner_score > renter_score

    def test_large_lot_increases_score(self, engine):
        """Larger lots should increase lawn care score"""
        small_lot = create_household(lot_size_sqft=2000)
        medium_lot = create_household(lot_size_sqft=6000)
        large_lot = create_household(lot_size_sqft=12000)

        small_score = engine.calculate_household_demand_score(small_lot, ServiceCategory.LAWN_CARE)
        medium_score = engine.calculate_household_demand_score(medium_lot, ServiceCategory.LAWN_CARE)
        large_score = engine.calculate_household_demand_score(large_lot, ServiceCategory.LAWN_CARE)

        assert large_score > medium_score > small_score

    def test_single_family_scores_higher(self, engine):
        """Single family homes should score higher than multi-family"""
        single_family = create_household(property_type=PropertyType.SINGLE_FAMILY)
        multi_family = create_household(property_type=PropertyType.MULTI_FAMILY)
        condo = create_household(property_type=PropertyType.CONDO)

        sf_score = engine.calculate_household_demand_score(single_family, ServiceCategory.LAWN_CARE)
        mf_score = engine.calculate_household_demand_score(multi_family, ServiceCategory.LAWN_CARE)
        condo_score = engine.calculate_household_demand_score(condo, ServiceCategory.LAWN_CARE)

        assert sf_score > mf_score
        assert sf_score > condo_score

    def test_high_income_increases_score(self, engine):
        """Higher income households should score higher"""
        low_income = create_household(income_band_min=30000, income_band_max=40000)
        mid_income = create_household(income_band_min=55000, income_band_max=65000)
        high_income = create_household(income_band_min=80000, income_band_max=100000)

        low_score = engine.calculate_household_demand_score(low_income, ServiceCategory.LAWN_CARE)
        mid_score = engine.calculate_household_demand_score(mid_income, ServiceCategory.LAWN_CARE)
        high_score = engine.calculate_household_demand_score(high_income, ServiceCategory.LAWN_CARE)

        assert high_score > mid_score > low_score


class TestSecurityDemandScore:
    """Tests for security services demand scoring"""

    def test_owner_gets_much_higher_score(self, engine):
        """Owners should score significantly higher for security"""
        owner = create_household(ownership_type=OwnershipType.OWNER)
        renter = create_household(ownership_type=OwnershipType.RENTER)

        owner_score = engine.calculate_household_demand_score(owner, ServiceCategory.SECURITY)
        renter_score = engine.calculate_household_demand_score(renter, ServiceCategory.SECURITY)

        # Owners get 50 points vs renters getting 5
        assert owner_score >= renter_score + 40

    def test_high_income_increases_security_score(self, engine):
        """High income households should score higher for security"""
        low_income = create_household(income_band_min=40000, income_band_max=50000)
        high_income = create_household(income_band_min=110000, income_band_max=130000)

        low_score = engine.calculate_household_demand_score(low_income, ServiceCategory.SECURITY)
        high_score = engine.calculate_household_demand_score(high_income, ServiceCategory.SECURITY)

        assert high_score > low_score


class TestITServicesDemandScore:
    """Tests for IT services demand scoring"""

    def test_high_income_is_primary_factor(self, engine):
        """Income should be the primary factor for IT services"""
        low_income = create_household(income_band_min=30000, income_band_max=40000)
        high_income = create_household(income_band_min=80000, income_band_max=100000)

        low_score = engine.calculate_household_demand_score(low_income, ServiceCategory.IT_SERVICES)
        high_score = engine.calculate_household_demand_score(high_income, ServiceCategory.IT_SERVICES)

        assert high_score > low_score

    def test_larger_property_increases_score(self, engine):
        """Larger properties (potential home offices) should score higher"""
        small_home = create_household(property_sqft_min=1500)
        large_home = create_household(property_sqft_min=2500)

        small_score = engine.calculate_household_demand_score(small_home, ServiceCategory.IT_SERVICES)
        large_score = engine.calculate_household_demand_score(large_home, ServiceCategory.IT_SERVICES)

        assert large_score > small_score


class TestFireworksDemandScore:
    """Tests for fireworks demand scoring"""

    def test_owner_scores_higher(self, engine):
        """Owners (who host events) should score higher"""
        owner = create_household(ownership_type=OwnershipType.OWNER)
        renter = create_household(ownership_type=OwnershipType.RENTER)

        owner_score = engine.calculate_household_demand_score(owner, ServiceCategory.FIREWORKS)
        renter_score = engine.calculate_household_demand_score(renter, ServiceCategory.FIREWORKS)

        assert owner_score > renter_score

    def test_large_lot_for_events(self, engine):
        """Large lots (space for events) should score higher"""
        small_lot = create_household(lot_size_sqft=3000)
        large_lot = create_household(lot_size_sqft=8000)

        small_score = engine.calculate_household_demand_score(small_lot, ServiceCategory.FIREWORKS)
        large_score = engine.calculate_household_demand_score(large_lot, ServiceCategory.FIREWORKS)

        assert large_score > small_score


class TestGeneralServiceScore:
    """Tests for general service demand scoring"""

    def test_has_base_score(self, engine):
        """General service should have a base score"""
        household = create_household()
        score = engine.calculate_household_demand_score(household, ServiceCategory.GENERAL)

        # Should have base score of 50 plus ownership bonus
        assert score >= 50

    def test_owner_bonus(self, engine):
        """Owners should get bonus for general services"""
        owner = create_household(ownership_type=OwnershipType.OWNER)
        renter = create_household(ownership_type=OwnershipType.RENTER)

        owner_score = engine.calculate_household_demand_score(owner, ServiceCategory.GENERAL)
        renter_score = engine.calculate_household_demand_score(renter, ServiceCategory.GENERAL)

        assert owner_score > renter_score


class TestScoreClamping:
    """Tests for score clamping to 0-100 range"""

    def test_score_never_exceeds_100(self, engine):
        """Score should be capped at 100"""
        # Create household with all high-scoring attributes
        household = create_household(
            ownership_type=OwnershipType.OWNER,
            property_type=PropertyType.SINGLE_FAMILY,
            lot_size_sqft=15000,
            income_band_min=150000,
            income_band_max=200000,
        )

        score = engine.calculate_household_demand_score(household, ServiceCategory.LAWN_CARE)
        assert score <= 100.0

    def test_score_never_below_zero(self, engine):
        """Score should never be negative"""
        household = create_household(
            ownership_type=OwnershipType.UNKNOWN,
            property_type=PropertyType.UNKNOWN,
        )

        score = engine.calculate_household_demand_score(household, ServiceCategory.LAWN_CARE)
        assert score >= 0.0


class TestBuyerProfileGeneration:
    """Tests for buyer profile generation"""

    def test_empty_households_returns_zeros(self, engine):
        """Empty household list should return zeroed profile"""
        profile = engine.generate_buyer_profile([], ServiceCategory.LAWN_CARE)

        assert profile["total_households"] == 0
        assert profile["homeowner_percentage"] == 0.0
        assert profile["renter_percentage"] == 0.0

    def test_profile_calculates_ownership_percentages(self, engine):
        """Profile should correctly calculate ownership percentages"""
        households = [
            create_household(ownership_type=OwnershipType.OWNER),
            create_household(ownership_type=OwnershipType.OWNER),
            create_household(ownership_type=OwnershipType.RENTER),
            create_household(ownership_type=OwnershipType.UNKNOWN),
        ]

        profile = engine.generate_buyer_profile(households, ServiceCategory.LAWN_CARE)

        assert profile["total_households"] == 4
        assert profile["homeowner_percentage"] == 50.0  # 2 out of 4
        assert profile["renter_percentage"] == 25.0  # 1 out of 4

    def test_profile_counts_property_types(self, engine):
        """Profile should count property types"""
        households = [
            create_household(property_type=PropertyType.SINGLE_FAMILY),
            create_household(property_type=PropertyType.SINGLE_FAMILY),
            create_household(property_type=PropertyType.CONDO),
        ]

        profile = engine.generate_buyer_profile(households, ServiceCategory.LAWN_CARE)

        assert profile["property_types"]["single_family"] == 2
        assert profile["property_types"]["condo"] == 1

    def test_profile_calculates_income_distribution(self, engine):
        """Profile should calculate income distribution"""
        households = [
            create_household(income_band_min=30000, income_band_max=40000),  # low
            create_household(income_band_min=60000, income_band_max=70000),  # medium
            create_household(income_band_min=80000, income_band_max=100000),  # high
        ]

        profile = engine.generate_buyer_profile(households, ServiceCategory.LAWN_CARE)

        assert profile["income_distribution"]["low"] == 1
        assert profile["income_distribution"]["medium"] == 1
        assert profile["income_distribution"]["high"] == 1
