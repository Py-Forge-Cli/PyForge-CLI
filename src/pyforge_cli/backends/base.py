"""Base database backend interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class DatabaseBackend(ABC):
    """Abstract base class for database connection backends."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend dependencies are available.
        
        Returns:
            True if backend can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to database.
        
        Args:
            db_path: Path to database file
            password: Optional password for protected databases
            
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_tables(self) -> List[str]:
        """List all readable tables in the database.
        
        Returns:
            List of table names
        """
        pass
    
    @abstractmethod
    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data as DataFrame.
        
        Args:
            table_name: Name of table to read
            
        Returns:
            DataFrame containing table data
            
        Raises:
            Exception: If table cannot be read
        """
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection and cleanup resources."""
        pass