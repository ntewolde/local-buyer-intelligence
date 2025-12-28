"""
PII Guard Module
Enforces no PII (Personal Identifiable Information) in data collection and storage
"""
from typing import Dict, List, Any, Union
import re


# Disallowed keys/fields (case-insensitive)
DISALLOWED_PII_KEYS = [
    "email", "e-mail", "e_mail", "email_address",
    "phone", "phone_number", "telephone", "mobile", "cell", "cell_phone",
    "firstname", "first_name", "fname",
    "lastname", "last_name", "lname", "surname",
    "fullname", "full_name", "name",
    "owner", "owner_name", "property_owner", "homeowner_name",
    "address", "street", "street_address", "street_address_line_1",
    "apt", "apartment", "unit", "unit_number", "suite",
    "ssn", "social_security_number", "social_security",
    "dob", "date_of_birth", "birthday", "birth_date",
    "facebook", "facebook_id", "facebook_url",
    "instagram", "instagram_id", "instagram_url",
    "linkedin", "linkedin_id", "linkedin_url",
    "twitter", "twitter_id", "twitter_url", "twitter_handle",
    "tiktok", "tiktok_id", "tiktok_url",
    "driver_license", "drivers_license", "dl_number",
    "passport", "passport_number",
]


def normalize_key(key: str) -> str:
    """
    Normalize a key for comparison (lowercase, replace spaces/underscores/dashes)
    """
    normalized = key.lower()
    normalized = re.sub(r'[_\s\-]', '', normalized)
    return normalized


def check_key(key: str) -> bool:
    """
    Check if a key is a disallowed PII key
    Returns True if disallowed, False if allowed
    """
    normalized = normalize_key(key)
    return normalized in [normalize_key(k) for k in DISALLOWED_PII_KEYS]


def assert_no_pii_keys(obj: Union[Dict, List, Any], path: str = "") -> None:
    """
    Recursively check object for disallowed PII keys
    Raises ValueError if any disallowed keys are found
    
    Args:
        obj: Dictionary, list, or value to check
        path: Current path in the object (for error messages)
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if key itself is disallowed
            if check_key(key):
                raise ValueError(
                    f"Disallowed PII key detected: '{key}' at path '{current_path}'. "
                    f"This field contains personal identifiable information and cannot be stored."
                )
            
            # Recursively check nested objects
            if isinstance(value, (dict, list)):
                assert_no_pii_keys(value, current_path)
    
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            current_path = f"{path}[{idx}]"
            if isinstance(item, (dict, list)):
                assert_no_pii_keys(item, current_path)


def validate_csv_headers(headers: List[str]) -> None:
    """
    Validate CSV headers for disallowed PII columns
    Raises ValueError if any disallowed headers are found
    
    Args:
        headers: List of CSV column names
    """
    disallowed_found = []
    for header in headers:
        if check_key(header):
            disallowed_found.append(header)
    
    if disallowed_found:
        raise ValueError(
            f"CSV contains disallowed PII columns: {', '.join(disallowed_found)}. "
            f"These columns contain personal identifiable information and cannot be imported."
        )


def sanitize_for_logging(data: Any) -> Any:
    """
    Sanitize data for logging (remove potential PII)
    This is a defensive measure - should not be primary enforcement
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if check_key(key):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_for_logging(value)
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    else:
        return data

