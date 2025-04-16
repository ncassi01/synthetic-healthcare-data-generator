"""
Base Database Connector Module

This module provides the base class for all database connectors in the system.
Each specific database connector should inherit from this base class and implement
the required methods.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseDBConnector(ABC):
    """
    Abstract base class for database connectors.
    
    This class defines the common interface that all database connectors must implement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database connector with configuration parameters.
        
        Args:
            config: Dictionary containing configuration parameters for the database connection.
        """
        self.config = config
        self.connection = None
        self.is_connected = False
        logger.info(f"Initializing {self.__class__.__name__} with config: {config}")
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a connection to the database.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close the connection to the database.
        
        Returns:
            bool: True if disconnection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def create_database(self, database_name: str) -> bool:
        """
        Create a new database.
        
        Args:
            database_name: Name of the database to create.
            
        Returns:
            bool: True if database creation was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def create_schema(self) -> bool:
        """
        Create the database schema (tables, collections, etc.).
        
        Returns:
            bool: True if schema creation was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def insert_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   collection_name: str) -> bool:
        """
        Insert data into the database.
        
        Args:
            data: Data to insert, either a single document or a list of documents.
            collection_name: Name of the collection/table to insert data into.
            
        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def query(self, query: Any, collection_name: str) -> List[Dict[str, Any]]:
        """
        Execute a query against the database.
        
        Args:
            query: Query to execute (format depends on the specific database).
            collection_name: Name of the collection/table to query.
            
        Returns:
            List of dictionaries containing the query results.
        """
        pass
    
    @abstractmethod
    def update_data(self, query: Any, update: Dict[str, Any], 
                   collection_name: str) -> bool:
        """
        Update data in the database.
        
        Args:
            query: Query to identify the records to update.
            update: Update operations to perform.
            collection_name: Name of the collection/table to update.
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def delete_data(self, query: Any, collection_name: str) -> bool:
        """
        Delete data from the database.
        
        Args:
            query: Query to identify the records to delete.
            collection_name: Name of the collection/table to delete from.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database.
        
        Returns:
            Dictionary containing database statistics.
        """
        pass
    
    def __enter__(self):
        """Context manager entry method."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method."""
        self.disconnect()