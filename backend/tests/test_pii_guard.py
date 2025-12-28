"""
Tests for PII Guard Module
"""
import pytest
from app.core.pii_guard import (
    assert_no_pii_keys,
    validate_csv_headers,
    check_key,
    normalize_key,
)


def test_check_key_detects_pii():
    """Test that PII keys are detected"""
    assert check_key("email") is True
    assert check_key("EMAIL") is True
    assert check_key("email_address") is True
    assert check_key("e-mail") is True
    assert check_key("e_mail") is True
    assert check_key("phone") is True
    assert check_key("phone_number") is True
    assert check_key("first_name") is True
    assert check_key("firstname") is True
    assert check_key("last_name") is True
    assert check_key("full_name") is True
    assert check_key("address") is True
    assert check_key("street_address") is True
    assert check_key("ssn") is True
    assert check_key("date_of_birth") is True


def test_check_key_allows_safe_keys():
    """Test that non-PII keys are allowed"""
    assert check_key("zip_code") is False
    assert check_key("property_type") is False
    assert check_key("household_count") is False
    assert check_key("latitude") is False
    assert check_key("longitude") is False
    assert check_key("event_name") is False
    assert check_key("channel_type") is False


def test_assert_no_pii_keys_dict():
    """Test assertion on dictionary with PII"""
    safe_data = {
        "zip_code": "12345",
        "property_type": "single_family",
        "household_count": 100
    }
    # Should not raise
    assert_no_pii_keys(safe_data)
    
    # Should raise on PII
    pii_data = {
        "zip_code": "12345",
        "email": "test@example.com"
    }
    with pytest.raises(ValueError, match="Disallowed PII key detected"):
        assert_no_pii_keys(pii_data)


def test_assert_no_pii_keys_nested():
    """Test assertion on nested dictionaries"""
    safe_data = {
        "data": {
            "zip_code": "12345",
            "properties": {
                "type": "single_family"
            }
        }
    }
    assert_no_pii_keys(safe_data)
    
    pii_data = {
        "data": {
            "zip_code": "12345",
            "owner_name": "John Doe"
        }
    }
    with pytest.raises(ValueError, match="Disallowed PII key detected"):
        assert_no_pii_keys(pii_data)


def test_assert_no_pii_keys_list():
    """Test assertion on list of dictionaries"""
    safe_data = [
        {"zip_code": "12345", "property_type": "single_family"},
        {"zip_code": "12346", "property_type": "condo"}
    ]
    assert_no_pii_keys(safe_data)
    
    pii_data = [
        {"zip_code": "12345", "email": "test@example.com"}
    ]
    with pytest.raises(ValueError, match="Disallowed PII key detected"):
        assert_no_pii_keys(pii_data)


def test_validate_csv_headers_safe():
    """Test CSV header validation with safe headers"""
    safe_headers = ["zip_code", "property_type", "lot_size_sqft", "year_built"]
    # Should not raise
    validate_csv_headers(safe_headers)


def test_validate_csv_headers_pii():
    """Test CSV header validation rejects PII headers"""
    pii_headers = ["zip_code", "email", "phone_number"]
    with pytest.raises(ValueError, match="CSV contains disallowed PII columns"):
        validate_csv_headers(pii_headers)


def test_validate_csv_headers_case_insensitive():
    """Test that CSV header validation is case-insensitive"""
    pii_headers = ["zip_code", "EMAIL", "Phone"]
    with pytest.raises(ValueError, match="CSV contains disallowed PII columns"):
        validate_csv_headers(pii_headers)


def test_normalize_key():
    """Test key normalization"""
    assert normalize_key("email") == "email"
    assert normalize_key("EMAIL") == "email"
    assert normalize_key("e-mail") == "email"
    assert normalize_key("e_mail") == "email"
    assert normalize_key("first_name") == "firstname"
    assert normalize_key("first name") == "firstname"


def test_pii_variations():
    """Test various PII key variations are caught"""
    variations = [
        "email", "e-mail", "e_mail", "email_address",
        "phone", "phone_number", "mobile", "cell",
        "first_name", "firstname", "fname",
        "last_name", "lastname", "surname",
        "address", "street", "street_address",
        "owner_name", "property_owner"
    ]
    
    for key in variations:
        assert check_key(key) is True, f"Failed to detect PII key: {key}"


def test_organizational_name_allowed():
    """Test that organizational 'name' field is allowed (PHASE 1.2)"""
    # Organizational names should be allowed
    org_data = {"name": "Sunset HOA"}
    assert_no_pii_keys(org_data)  # Should not raise
    
    channel_data = {"name": "Community Center", "channel_type": "VENUE"}
    assert_no_pii_keys(channel_data)  # Should not raise
    
    geography_data = {"name": "Atlanta", "state_code": "GA"}
    assert_no_pii_keys(geography_data)  # Should not raise


def test_personal_name_rejected():
    """Test that personal name fields are rejected (PHASE 1.2)"""
    # Personal names should be rejected
    with pytest.raises(ValueError, match="Disallowed PII key detected.*owner_name"):
        assert_no_pii_keys({"owner_name": "John Smith"})
    
    with pytest.raises(ValueError, match="Disallowed PII key detected.*first_name"):
        assert_no_pii_keys({"first_name": "Jane"})
    
    with pytest.raises(ValueError, match="Disallowed PII key detected.*full_name"):
        assert_no_pii_keys({"full_name": "John Doe"})


def test_nested_personal_name_rejected():
    """Test that nested personal names are rejected (PHASE 1.2)"""
    # Nested personal names should be rejected
    with pytest.raises(ValueError, match="Disallowed PII key detected.*owner_name"):
        assert_no_pii_keys({"metadata": {"owner_name": "Jane"}})
    
    with pytest.raises(ValueError, match="Disallowed PII key detected.*first_name"):
        assert_no_pii_keys({"data": {"user": {"first_name": "John"}}})






