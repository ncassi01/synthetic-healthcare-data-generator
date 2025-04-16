"""
Vector Database Connector Module

This module provides a connector for Pinecone vector database.
It implements the BaseDBConnector interface and provides Pinecone-specific
functionality.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

try:
    # Try importing the new package name first
    from pinecone import Pinecone, PodSpec
except ImportError:
    try:
        # Fall back to the old package name if necessary
        from pinecone_client import Pinecone, PodSpec
    except ImportError:
        raise ImportError(
            "Neither 'pinecone' nor 'pinecone-client' package is installed. "
            "Please install the Pinecone package with: pip install pinecone"
        )

from .base import BaseDBConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PineconeConnector(BaseDBConnector):
    """
    Pinecone vector database connector.
    
    This class provides methods to interact with a Pinecone vector database.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Pinecone connector with configuration parameters.
        
        Args:
            config: Dictionary containing configuration parameters for the Pinecone connection.
                   Required keys: api_key
                   Optional keys: environment, project_name, dimension, metric, pod_type,
                                 connection_retries, retry_delay
        """
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.environment = config.get('environment', 'us-west1-gcp')
        self.project_name = config.get('project_name')
        self.dimension = config.get('dimension', 768)  # Default dimension for embeddings
        self.metric = config.get('metric', 'cosine')  # Default similarity metric
        self.pod_type = config.get('pod_type', 'p1.x1')  # Default pod type
        self.connection_retries = config.get('connection_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.index_name = config.get('index_name', 'healthcare-embeddings')
        self.client = None
        self.index = None
    
    def connect(self) -> bool:
        """
        Establish a connection to the Pinecone service.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        for attempt in range(self.connection_retries):
            try:
                logger.info(f"Connecting to Pinecone service")
                
                # Initialize Pinecone client
                self.client = Pinecone(api_key=self.api_key)
                
                # Check if the index exists
                index_list = self.client.list_indexes()
                
                if self.index_name in [index.name for index in index_list]:
                    # Connect to existing index
                    self.index = self.client.Index(self.index_name)
                    logger.info(f"Connected to existing Pinecone index: {self.index_name}")
                else:
                    logger.info(f"Index {self.index_name} does not exist. It will be created when create_database() is called.")
                
                self.is_connected = True
                logger.info("Successfully connected to Pinecone service")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to Pinecone service (attempt {attempt+1}/{self.connection_retries}): {e}")
                if attempt < self.connection_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Maximum connection attempts reached. Could not connect to Pinecone service.")
        return False
    
    def disconnect(self) -> bool:
        """
        Close the connection to the Pinecone service.
        
        Returns:
            bool: True if disconnection was successful, False otherwise.
        """
        # Pinecone client doesn't require explicit disconnection
        self.is_connected = False
        logger.info("Disconnected from Pinecone service")
        return True
    
    def create_database(self, database_name: str) -> bool:
        """
        Create a new Pinecone index.
        
        Args:
            database_name: Name of the index to create.
            
        Returns:
            bool: True if index creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return False
        
        try:
            # Set the index name
            self.index_name = database_name
            
            # Check if index already exists
            index_list = self.client.list_indexes()
            
            if self.index_name in [index.name for index in index_list]:
                logger.info(f"Index {self.index_name} already exists")
                self.index = self.client.Index(self.index_name)
                return True
            
            # Create the index
            self.client.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=PodSpec(
                    environment=self.environment,
                    pod_type=self.pod_type
                )
            )
            
            # Wait for the index to be ready
            logger.info(f"Waiting for index {self.index_name} to be ready...")
            while self.index_name not in [index.name for index in self.client.list_indexes()]:
                time.sleep(5)
            
            # Connect to the new index
            self.index = self.client.Index(self.index_name)
            
            logger.info(f"Created Pinecone index {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating Pinecone index {database_name}: {e}")
            return False
    
    def create_schema(self) -> bool:
        """
        Create the database schema.
        
        For Pinecone, this is a no-op as the schema is defined when creating the index.
        
        Returns:
            bool: True if schema creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return False
        
        if not self.index:
            logger.error("No index selected. Call create_database() first.")
            return False
        
        # Pinecone doesn't require explicit schema creation beyond index creation
        logger.info("Pinecone schema is defined at index creation time")
        return True
    
    def insert_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   collection_name: str = None) -> bool:
        """
        Insert vector data into the Pinecone index.
        
        Args:
            data: Data to insert, either a single vector or a list of vectors.
                 Each vector should have 'id', 'values', and optionally 'metadata'.
            collection_name: Ignored for Pinecone (used for logging only).
            
        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return False
        
        if not self.index:
            logger.error("No index selected. Call create_database() first.")
            return False
        
        # Convert single vector to list
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            logger.warning("No data to insert into Pinecone index")
            return True
        
        try:
            # Format data for Pinecone upsert
            vectors = []
            for item in data:
                vector = {
                    'id': item['id'],
                    'values': item['values']
                }
                if 'metadata' in item:
                    vector['metadata'] = item['metadata']
                vectors.append(vector)
            
            # Upsert vectors in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Successfully inserted {len(vectors)} vectors into Pinecone index {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Error inserting data into Pinecone index {self.index_name}: {e}")
            return False
    
    def query(self, query: Dict[str, Any], collection_name: str = None) -> List[Dict[str, Any]]:
        """
        Query the Pinecone index for similar vectors.
        
        Args:
            query: Query parameters including 'vector', 'top_k', and optionally 'filter'.
            collection_name: Ignored for Pinecone (used for logging only).
            
        Returns:
            List of dictionaries containing the query results.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return []
        
        if not self.index:
            logger.error("No index selected. Call create_database() first.")
            return []
        
        try:
            # Extract query parameters
            vector = query.get('vector')
            top_k = query.get('top_k', 10)
            filter_dict = query.get('filter')
            include_metadata = query.get('include_metadata', True)
            include_values = query.get('include_values', False)
            
            # Execute query
            response = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata,
                include_values=include_values
            )
            
            # Format results
            results = []
            for match in response['matches']:
                result = {
                    'id': match['id'],
                    'score': match['score']
                }
                if include_metadata and 'metadata' in match:
                    result['metadata'] = match['metadata']
                if include_values and 'values' in match:
                    result['values'] = match['values']
                results.append(result)
            
            logger.info(f"Query executed successfully on Pinecone index {self.index_name}, returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error executing query on Pinecone index {self.index_name}: {e}")
            return []
    
    def update_data(self, query: Dict[str, Any], update: Dict[str, Any], 
                   collection_name: str = None) -> bool:
        """
        Update data in the Pinecone index.
        
        For Pinecone, updates are performed using upsert with the same ID.
        
        Args:
            query: Dictionary containing the 'id' of the vector to update.
            update: Dictionary containing the new 'values' and optionally 'metadata'.
            collection_name: Ignored for Pinecone (used for logging only).
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return False
        
        if not self.index:
            logger.error("No index selected. Call create_database() first.")
            return False
        
        try:
            # Extract vector ID
            vector_id = query.get('id')
            if not vector_id:
                logger.error("No vector ID provided for update")
                return False
            
            # Prepare update data
            vector = {
                'id': vector_id,
                'values': update.get('values')
            }
            if 'metadata' in update:
                vector['metadata'] = update['metadata']
            
            # Upsert the vector
            self.index.upsert(vectors=[vector])
            
            logger.info(f"Successfully updated vector {vector_id} in Pinecone index {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating data in Pinecone index {self.index_name}: {e}")
            return False
    
    def delete_data(self, query: Dict[str, Any], collection_name: str = None) -> bool:
        """
        Delete data from the Pinecone index.
        
        Args:
            query: Dictionary containing either 'ids' (list of IDs) or 'filter' (metadata filter).
            collection_name: Ignored for Pinecone (used for logging only).
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return False
        
        if not self.index:
            logger.error("No index selected. Call create_database() first.")
            return False
        
        try:
            # Extract deletion parameters
            ids = query.get('ids')
            filter_dict = query.get('filter')
            
            if ids:
                # Delete by IDs
                self.index.delete(ids=ids)
                logger.info(f"Successfully deleted {len(ids)} vectors from Pinecone index {self.index_name}")
            elif filter_dict:
                # Delete by filter
                self.index.delete(filter=filter_dict)
                logger.info(f"Successfully deleted vectors matching filter from Pinecone index {self.index_name}")
            else:
                logger.error("No IDs or filter provided for deletion")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error deleting data from Pinecone index {self.index_name}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Dictionary containing index statistics.
        """
        if not self.is_connected:
            logger.error("Not connected to Pinecone service. Call connect() first.")
            return {}
        
        if not self.index:
            logger.error("No index selected. Call create_database() first.")
            return {}
        
        stats = {}
        
        try:
            # Get index stats
            index_stats = self.index.describe_index_stats()
            
            stats['total_vector_count'] = index_stats['total_vector_count']
            stats['dimension'] = index_stats['dimension']
            stats['index_fullness'] = index_stats.get('index_fullness', 'N/A')
            
            # Get namespace stats if available
            if 'namespaces' in index_stats:
                stats['namespaces'] = index_stats['namespaces']
            
            logger.info("Successfully retrieved Pinecone index statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting Pinecone index statistics: {e}")
            return {'error': str(e)}