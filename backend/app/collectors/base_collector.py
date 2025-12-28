"""
Base Collector Class
All data collectors inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session


class BaseCollector(ABC):
    """Base class for all data collectors"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect data from the source
        Returns list of dictionaries representing collected data
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate collected data to ensure it meets quality standards
        Returns True if valid, False otherwise
        """
        pass
    
    def store(self, data: List[Dict[str, Any]]) -> int:
        """
        Store collected data in database
        Returns number of records stored
        """
        # Default implementation - override in subclasses
        return 0
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the full collection process
        Returns summary of collection results
        """
        try:
            data = self.collect(**kwargs)
            validated_data = [d for d in data if self.validate_data(d)]
            stored_count = self.store(validated_data)
            
            return {
                "status": "success",
                "collected": len(data),
                "validated": len(validated_data),
                "stored": stored_count,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "collected": 0,
                "validated": 0,
                "stored": 0,
            }

