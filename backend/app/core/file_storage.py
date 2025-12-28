"""
File Storage Utilities for CSV Uploads
"""
import os
from pathlib import Path
from typing import Optional
import uuid
from datetime import datetime


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file and return file reference
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        
    Returns:
        file_ref: Unique file reference (UUID-based)
    """
    # Generate unique file reference
    file_ref = str(uuid.uuid4())
    
    # Get file extension
    ext = Path(filename).suffix or ".csv"
    
    # Create file path
    file_path = UPLOAD_DIR / f"{file_ref}{ext}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_ref


def get_file_path(file_ref: str) -> Optional[Path]:
    """
    Get file path from file reference
    
    Args:
        file_ref: File reference UUID
        
    Returns:
        Path to file if exists, None otherwise
    """
    # Try to find file with common extensions
    for ext in [".csv", ".txt"]:
        file_path = UPLOAD_DIR / f"{file_ref}{ext}"
        if file_path.exists():
            return file_path
    
    return None


def delete_file(file_ref: str) -> bool:
    """
    Delete uploaded file
    
    Args:
        file_ref: File reference UUID
        
    Returns:
        True if deleted, False if not found
    """
    file_path = get_file_path(file_ref)
    if file_path and file_path.exists():
        file_path.unlink()
        return True
    return False

