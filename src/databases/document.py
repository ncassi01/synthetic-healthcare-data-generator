"""
Document Database Connector Module

This module provides a connector for MongoDB document database.
It implements the BaseDBConnector interface and provides MongoDB-specific
functionality.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from .base import BaseDBConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBConnector(BaseDBConnector):
    """
    MongoDB database connector.
    
    This class provides methods to interact with a MongoDB database.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MongoDB connector with configuration parameters.
        
        Args:
            config: Dictionary containing configuration parameters for the MongoDB connection.
                   Required keys: host, port, database
                   Optional keys: username, password, auth_source, connection_timeout,
                                 connection_retries, retry_delay
        """
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 27017)
        self.database_name = config.get('database', 'healthcare')
        self.username = config.get('username')
        self.password = config.get('password')
        self.auth_source = config.get('auth_source', 'admin')
        self.connection_timeout = config.get('connection_timeout', 30000)  # in milliseconds
        self.connection_retries = config.get('connection_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.client = None
        self.db = None
    
    def connect(self) -> bool:
        """
        Establish a connection to the MongoDB database.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        for attempt in range(self.connection_retries):
            try:
                logger.info(f"Connecting to MongoDB database {self.database_name} on {self.host}:{self.port}")
                
                # Prepare connection URI
                if self.username and self.password:
                    uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}?authSource={self.auth_source}"
                else:
                    uri = f"mongodb://{self.host}:{self.port}/{self.database_name}"
                
                # Connect to MongoDB
                self.client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=self.connection_timeout
                )
                
                # Test the connection
                self.client.admin.command('ping')
                
                # Get database
                self.db = self.client[self.database_name]
                
                self.is_connected = True
                logger.info("Successfully connected to MongoDB database")
                return True
            except (ConnectionFailure, OperationFailure) as e:
                logger.error(f"Failed to connect to MongoDB database (attempt {attempt+1}/{self.connection_retries}): {e}")
                if attempt < self.connection_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Maximum connection attempts reached. Could not connect to MongoDB database.")
        return False
    
    def disconnect(self) -> bool:
        """
        Close the connection to the MongoDB database.
        
        Returns:
            bool: True if disconnection was successful, False otherwise.
        """
        if self.client and self.is_connected:
            try:
                self.client.close()
                self.is_connected = False
                logger.info("Disconnected from MongoDB database")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from MongoDB database: {e}")
                return False
        return True  # Already disconnected
    
    def create_database(self, database_name: str) -> bool:
        """
        Create a new MongoDB database.
        
        In MongoDB, databases are created implicitly when collections are created,
        so this method just sets the database name.
        
        Args:
            database_name: Name of the database to create.
            
        Returns:
            bool: True if database creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            # In MongoDB, databases are created implicitly when collections are created
            self.database_name = database_name
            self.db = self.client[database_name]
            logger.info(f"Set active database to {database_name}")
            
            # Create a dummy collection to ensure the database is created
            self.db.create_collection('_database_info')
            self.db['_database_info'].insert_one({
                'name': database_name,
                'created_at': time.time()
            })
            
            logger.info(f"Created database {database_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating database {database_name}: {e}")
            return False
    
    def create_schema(self) -> bool:
        """
        Create the database schema (collections, indexes, etc.).
        
        Returns:
            bool: True if schema creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            # Create collections
            collections = [
                'clinical_notes',
                'communications',
                'care_plans',
                'authorization_rationales',
                'mental_health_narratives',
                'patient_generated_data',
                'provider_communications',
                'telehealth_documentation',
                'insurance_communications',
                'education_materials'
            ]
            
            for collection_name in collections:
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(collection_name)
                    logger.info(f"Created collection {collection_name}")
            
            # Create indexes
            self._create_clinical_notes_indexes()
            self._create_communications_indexes()
            self._create_care_plans_indexes()
            self._create_authorization_rationales_indexes()
            self._create_mental_health_narratives_indexes()
            self._create_patient_generated_data_indexes()
            self._create_provider_communications_indexes()
            self._create_telehealth_documentation_indexes()
            self._create_insurance_communications_indexes()
            
            logger.info("Successfully created database schema")
            return True
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            return False
    
    def _create_clinical_notes_indexes(self):
        """Create indexes for the clinical_notes collection."""
        self.db.clinical_notes.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.clinical_notes.create_index([('provider_id', pymongo.ASCENDING)], background=True)
        self.db.clinical_notes.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.clinical_notes.create_index([('note_type', pymongo.ASCENDING)], background=True)
        self.db.clinical_notes.create_index([
            ('chief_complaint', pymongo.TEXT),
            ('history_of_present_illness', pymongo.TEXT),
            ('assessment', pymongo.TEXT),
            ('plan', pymongo.TEXT)
        ], background=True, name='text_search')
    
    def _create_communications_indexes(self):
        """Create indexes for the communications collection."""
        self.db.communications.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.communications.create_index([('provider_id', pymongo.ASCENDING)], background=True)
        self.db.communications.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.communications.create_index([('communication_type', pymongo.ASCENDING)], background=True)
        self.db.communications.create_index([('subject', pymongo.TEXT), ('content', pymongo.TEXT)], 
                                          background=True, name='text_search')
    
    def _create_care_plans_indexes(self):
        """Create indexes for the care_plans collection."""
        self.db.care_plans.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.care_plans.create_index([('care_manager_id', pymongo.ASCENDING)], background=True)
        self.db.care_plans.create_index([('created_date', pymongo.DESCENDING)], background=True)
        self.db.care_plans.create_index([('updated_date', pymongo.DESCENDING)], background=True)
        self.db.care_plans.create_index([('status', pymongo.ASCENDING)], background=True)
    
    def _create_authorization_rationales_indexes(self):
        """Create indexes for the authorization_rationales collection."""
        self.db.authorization_rationales.create_index([('authorization_id', pymongo.ASCENDING)], 
                                                   background=True, unique=True)
        self.db.authorization_rationales.create_index([('decision', pymongo.ASCENDING)], background=True)
    
    def _create_mental_health_narratives_indexes(self):
        """Create indexes for the mental_health_narratives collection."""
        self.db.mental_health_narratives.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.mental_health_narratives.create_index([('provider_id', pymongo.ASCENDING)], background=True)
        self.db.mental_health_narratives.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.mental_health_narratives.create_index([('assessment_type', pymongo.ASCENDING)], background=True)
        self.db.mental_health_narratives.create_index([
            ('presenting_problem', pymongo.TEXT),
            ('mental_status_exam', pymongo.TEXT),
            ('treatment_plan', pymongo.TEXT)
        ], background=True, name='text_search')
    
    def _create_patient_generated_data_indexes(self):
        """Create indexes for the patient_generated_data collection."""
        self.db.patient_generated_data.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.patient_generated_data.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.patient_generated_data.create_index([('data_type', pymongo.ASCENDING)], background=True)
        self.db.patient_generated_data.create_index([('tags', pymongo.ASCENDING)], background=True)
        self.db.patient_generated_data.create_index([('content', pymongo.TEXT)], 
                                                 background=True, name='text_search')
    
    def _create_provider_communications_indexes(self):
        """Create indexes for the provider_communications collection."""
        self.db.provider_communications.create_index([('from_provider_id', pymongo.ASCENDING)], background=True)
        self.db.provider_communications.create_index([('to_provider_id', pymongo.ASCENDING)], background=True)
        self.db.provider_communications.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.provider_communications.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.provider_communications.create_index([('communication_type', pymongo.ASCENDING)], background=True)
        self.db.provider_communications.create_index([('subject', pymongo.TEXT), ('content', pymongo.TEXT)], 
                                                  background=True, name='text_search')
    
    def _create_telehealth_documentation_indexes(self):
        """Create indexes for the telehealth_documentation collection."""
        self.db.telehealth_documentation.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.telehealth_documentation.create_index([('provider_id', pymongo.ASCENDING)], background=True)
        self.db.telehealth_documentation.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.telehealth_documentation.create_index([('visit_type', pymongo.ASCENDING)], background=True)
        self.db.telehealth_documentation.create_index([
            ('chief_complaint', pymongo.TEXT),
            ('subjective', pymongo.TEXT),
            ('assessment', pymongo.TEXT),
            ('plan', pymongo.TEXT)
        ], background=True, name='text_search')
    
    def _create_insurance_communications_indexes(self):
        """Create indexes for the insurance_communications collection."""
        self.db.insurance_communications.create_index([('member_id', pymongo.ASCENDING)], background=True)
        self.db.insurance_communications.create_index([('date', pymongo.DESCENDING)], background=True)
        self.db.insurance_communications.create_index([('communication_type', pymongo.ASCENDING)], background=True)
        self.db.insurance_communications.create_index([('related_authorization_id', pymongo.ASCENDING)], 
                                                   background=True)
        self.db.insurance_communications.create_index([('subject', pymongo.TEXT), ('content', pymongo.TEXT)], 
                                                   background=True, name='text_search')
    
    def insert_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   collection_name: str) -> bool:
        """
        Insert data into the MongoDB database.
        
        Args:
            data: Data to insert, either a single document or a list of documents.
            collection_name: Name of the collection to insert data into.
            
        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            collection = self.db[collection_name]
            
            # Insert data
            if isinstance(data, dict):
                result = collection.insert_one(data)
                logger.info(f"Successfully inserted 1 document into {collection_name} with ID {result.inserted_id}")
            else:
                result = collection.insert_many(data)
                logger.info(f"Successfully inserted {len(result.inserted_ids)} documents into {collection_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error inserting data into {collection_name}: {e}")
            return False
    
    def query(self, query: Dict[str, Any], collection_name: str) -> List[Dict[str, Any]]:
        """
        Execute a query against the MongoDB database.
        
        Args:
            query: MongoDB query to execute.
            collection_name: Name of the collection to query.
            
        Returns:
            List of dictionaries containing the query results.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return []
        
        try:
            collection = self.db[collection_name]
            
            # Execute query
            results = list(collection.find(query))
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                if '_id' in result and hasattr(result['_id'], '__str__'):
                    result['_id'] = str(result['_id'])
            
            logger.info(f"Query executed successfully on {collection_name}, returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error executing query on {collection_name}: {e}")
            return []
    
    def update_data(self, query: Dict[str, Any], update: Dict[str, Any], 
                   collection_name: str) -> bool:
        """
        Update data in the MongoDB database.
        
        Args:
            query: MongoDB query to identify the documents to update.
            update: MongoDB update operations to perform.
            collection_name: Name of the collection to update.
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            collection = self.db[collection_name]
            
            # Update data
            result = collection.update_many(query, update)
            
            logger.info(f"Successfully updated {result.modified_count} documents in {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating data in {collection_name}: {e}")
            return False
    
    def delete_data(self, query: Dict[str, Any], collection_name: str) -> bool:
        """
        Delete data from the MongoDB database.
        
        Args:
            query: MongoDB query to identify the documents to delete.
            collection_name: Name of the collection to delete from.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            collection = self.db[collection_name]
            
            # Delete data
            result = collection.delete_many(query)
            
            logger.info(f"Successfully deleted {result.deleted_count} documents from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting data from {collection_name}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the MongoDB database.
        
        Returns:
            Dictionary containing database statistics.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return {}
        
        stats = {}
        
        try:
            # Get database stats
            db_stats = self.db.command('dbStats')
            stats['database_size'] = f"{db_stats['dataSize'] / (1024 * 1024):.2f} MB"
            stats['storage_size'] = f"{db_stats['storageSize'] / (1024 * 1024):.2f} MB"
            stats['num_collections'] = db_stats['collections']
            stats['num_indexes'] = db_stats['indexes']
            
            # Get collection stats
            collection_stats = {}
            for collection_name in self.db.list_collection_names():
                coll_stats = self.db.command('collStats', collection_name)
                collection_stats[collection_name] = {
                    'count': coll_stats['count'],
                    'size': f"{coll_stats['size'] / (1024 * 1024):.2f} MB",
                    'avg_doc_size': f"{coll_stats['avgObjSize'] / 1024:.2f} KB" if coll_stats['count'] > 0 else "0 KB",
                    'num_indexes': len(coll_stats['indexSizes']),
                    'index_size': f"{coll_stats['totalIndexSize'] / (1024 * 1024):.2f} MB"
                }
            
            stats['collections'] = collection_stats
            
            # Get index information
            index_info = {}
            for collection_name in self.db.list_collection_names():
                indexes = self.db[collection_name].index_information()
                index_info[collection_name] = indexes
            
            stats['indexes'] = index_info
            
            logger.info("Successfully retrieved database statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return {'error': str(e)}