"""
Graph Database Connector Module

This module provides a connector for Neo4j graph database.
It implements the BaseDBConnector interface and provides Neo4j-specific
functionality.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from .base import BaseDBConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jConnector(BaseDBConnector):
    """
    Neo4j graph database connector.
    
    This class provides methods to interact with a Neo4j graph database.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Neo4j connector with configuration parameters.
        
        Args:
            config: Dictionary containing configuration parameters for the Neo4j connection.
                   Required keys: uri, username, password
                   Optional keys: database, connection_timeout, connection_retries, retry_delay
        """
        super().__init__(config)
        self.uri = config.get('uri', 'bolt://localhost:7687')
        self.username = config.get('username', 'neo4j')
        self.password = config.get('password', 'neo4j')
        self.database = config.get('database', 'neo4j')
        self.connection_timeout = config.get('connection_timeout', 30)  # in seconds
        self.connection_retries = config.get('connection_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.driver = None
    
    def connect(self) -> bool:
        """
        Establish a connection to the Neo4j database.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        for attempt in range(self.connection_retries):
            try:
                logger.info(f"Connecting to Neo4j database at {self.uri}")
                
                # Connect to Neo4j
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password),
                    max_connection_lifetime=self.connection_timeout
                )
                
                # Test the connection
                with self.driver.session(database=self.database) as session:
                    session.run("RETURN 1")
                
                self.is_connected = True
                logger.info("Successfully connected to Neo4j database")
                return True
            except (ServiceUnavailable, AuthError) as e:
                logger.error(f"Failed to connect to Neo4j database (attempt {attempt+1}/{self.connection_retries}): {e}")
                if attempt < self.connection_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Maximum connection attempts reached. Could not connect to Neo4j database.")
        return False
    
    def disconnect(self) -> bool:
        """
        Close the connection to the Neo4j database.
        
        Returns:
            bool: True if disconnection was successful, False otherwise.
        """
        if self.driver and self.is_connected:
            try:
                self.driver.close()
                self.is_connected = False
                logger.info("Disconnected from Neo4j database")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from Neo4j database: {e}")
                return False
        return True  # Already disconnected
    
    def create_database(self, database_name: str) -> bool:
        """
        Create a new Neo4j database.
        
        Note: This requires Neo4j Enterprise Edition and admin privileges.
        
        Args:
            database_name: Name of the database to create.
            
        Returns:
            bool: True if database creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            # Connect to the system database to create a new database
            with self.driver.session(database="system") as session:
                # Check if database already exists
                result = session.run(
                    "SHOW DATABASES WHERE name = $name",
                    name=database_name
                )
                
                if result.single():
                    logger.info(f"Database {database_name} already exists")
                    return True
                
                # Create the database
                session.run(
                    "CREATE DATABASE $name",
                    name=database_name
                )
                
                logger.info(f"Created database {database_name}")
                
                # Set the current database
                self.database = database_name
                
                return True
        except Exception as e:
            logger.error(f"Error creating database {database_name}: {e}")
            logger.warning("Note: Creating databases requires Neo4j Enterprise Edition and admin privileges")
            return False
    
    def create_schema(self) -> bool:
        """
        Create the database schema (nodes, relationships, constraints, indexes).
        
        Returns:
            bool: True if schema creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.driver.session(database=self.database) as session:
                # Create constraints
                self._create_constraints(session)
                
                # Create indexes
                self._create_indexes(session)
                
                logger.info("Successfully created database schema")
                return True
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            return False
    
    def _create_constraints(self, session):
        """Create constraints for the graph database."""
        # Create node key constraints (unique identifiers)
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Member) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Provider) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Encounter) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Condition) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Medication) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Procedure) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Authorization) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:EOB) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Plan) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ce:CareEpisode) REQUIRE ce.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (sa:SDOHAssessment) REQUIRE sa.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ra:RiskAssessment) REQUIRE ra.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (pn:ProviderNetwork) REQUIRE pn.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (pr:ProviderRelationship) REQUIRE pr.id IS UNIQUE"
        ]
        
        for constraint in constraints:
            session.run(constraint)
            logger.info(f"Created constraint: {constraint}")
    
    def _create_indexes(self, session):
        """Create indexes for the graph database."""
        # Create indexes for common query patterns
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (m:Member) ON (m.last_name)",
            "CREATE INDEX IF NOT EXISTS FOR (m:Member) ON (m.date_of_birth)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Provider) ON (p.specialty)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Encounter) ON (e.date)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Condition) ON (c.code)",
            "CREATE INDEX IF NOT EXISTS FOR (m:Medication) ON (m.name)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Procedure) ON (p.code)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Claim) ON (c.date_of_service)",
            "CREATE INDEX IF NOT EXISTS FOR (a:Authorization) ON (a.status)",
            "CREATE INDEX IF NOT EXISTS FOR (ce:CareEpisode) ON (ce.episode_type)",
            "CREATE INDEX IF NOT EXISTS FOR (sa:SDOHAssessment) ON (sa.assessment_date)",
            "CREATE INDEX IF NOT EXISTS FOR (ra:RiskAssessment) ON (ra.assessment_date)",
            "CREATE INDEX IF NOT EXISTS FOR (pr:ProviderRelationship) ON (pr.relationship_type)"
        ]
        
        for index in indexes:
            session.run(index)
            logger.info(f"Created index: {index}")
    
    def insert_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   collection_name: str) -> bool:
        """
        Insert data into the Neo4j database.
        
        In Neo4j, 'collection_name' represents the node label or relationship type.
        
        Args:
            data: Data to insert, either a single document or a list of documents.
            collection_name: Node label or relationship type.
            
        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        # Convert single document to list
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            logger.warning(f"No data to insert with label/type {collection_name}")
            return True
        
        try:
            with self.driver.session(database=self.database) as session:
                # Determine if this is a node or relationship based on collection_name
                if collection_name.endswith('_RELATIONSHIP'):
                    # Handle relationship insertion
                    relationship_type = collection_name.replace('_RELATIONSHIP', '')
                    for item in data:
                        self._create_relationship(session, relationship_type, item)
                else:
                    # Handle node insertion
                    for item in data:
                        self._create_node(session, collection_name, item)
                
                logger.info(f"Successfully inserted {len(data)} items with label/type {collection_name}")
                return True
        except Exception as e:
            logger.error(f"Error inserting data with label/type {collection_name}: {e}")
            return False
    
    def _create_node(self, session, label, properties):
        """Create a node with the given label and properties."""
        # Extract the ID for logging
        node_id = properties.get('id', 'unknown')
        
        # Create Cypher query
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n
        """
        
        # Execute query
        session.run(query, properties=properties)
        logger.debug(f"Created {label} node with ID {node_id}")
    
    def _create_relationship(self, session, relationship_type, properties):
        """Create a relationship between two nodes."""
        # Extract source and target node information
        source_label = properties.get('source_label')
        source_id = properties.get('source_id')
        target_label = properties.get('target_label')
        target_id = properties.get('target_id')
        
        # Remove source and target info from properties
        relationship_properties = {k: v for k, v in properties.items() 
                                 if k not in ('source_label', 'source_id', 'target_label', 'target_id')}
        
        # Create Cypher query
        query = f"""
        MATCH (source:{source_label} {{id: $source_id}}), (target:{target_label} {{id: $target_id}})
        CREATE (source)-[r:{relationship_type} $properties]->(target)
        RETURN r
        """
        
        # Execute query
        session.run(
            query, 
            source_id=source_id,
            target_id=target_id,
            properties=relationship_properties
        )
        
        logger.debug(f"Created {relationship_type} relationship from {source_label}:{source_id} to {target_label}:{target_id}")
    
    def query(self, query: str, collection_name: str = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query against the Neo4j database.
        
        Args:
            query: Cypher query to execute.
            collection_name: Optional node label or relationship type (for logging only).
            
        Returns:
            List of dictionaries containing the query results.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return []
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query)
                records = [record.data() for record in result]
                
                log_msg = f"Query executed successfully"
                if collection_name:
                    log_msg += f" on {collection_name}"
                log_msg += f", returned {len(records)} results"
                logger.info(log_msg)
                
                return records
        except Exception as e:
            log_msg = f"Error executing query"
            if collection_name:
                log_msg += f" on {collection_name}"
            logger.error(f"{log_msg}: {e}")
            return []
    
    def update_data(self, query: str, update: Dict[str, Any] = None, 
                   collection_name: str = None) -> bool:
        """
        Update data in the Neo4j database using a Cypher query.
        
        Args:
            query: Cypher query to execute the update.
            update: Optional parameters for the query.
            collection_name: Optional node label or relationship type (for logging only).
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.driver.session(database=self.database) as session:
                if update:
                    result = session.run(query, update)
                else:
                    result = session.run(query)
                
                summary = result.consume()
                affected_nodes = summary.counters.nodes_created + summary.counters.nodes_deleted + summary.counters.properties_set
                affected_relationships = summary.counters.relationships_created + summary.counters.relationships_deleted
                
                log_msg = f"Successfully updated {affected_nodes} nodes and {affected_relationships} relationships"
                if collection_name:
                    log_msg += f" for {collection_name}"
                logger.info(log_msg)
                
                return True
        except Exception as e:
            log_msg = f"Error updating data"
            if collection_name:
                log_msg += f" for {collection_name}"
            logger.error(f"{log_msg}: {e}")
            return False
    
    def delete_data(self, query: str, collection_name: str = None) -> bool:
        """
        Delete data from the Neo4j database using a Cypher query.
        
        Args:
            query: Cypher query to execute the deletion.
            collection_name: Optional node label or relationship type (for logging only).
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query)
                
                summary = result.consume()
                deleted_nodes = summary.counters.nodes_deleted
                deleted_relationships = summary.counters.relationships_deleted
                
                log_msg = f"Successfully deleted {deleted_nodes} nodes and {deleted_relationships} relationships"
                if collection_name:
                    log_msg += f" for {collection_name}"
                logger.info(log_msg)
                
                return True
        except Exception as e:
            log_msg = f"Error deleting data"
            if collection_name:
                log_msg += f" for {collection_name}"
            logger.error(f"{log_msg}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Neo4j database.
        
        Returns:
            Dictionary containing database statistics.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return {}
        
        stats = {}
        
        try:
            with self.driver.session(database=self.database) as session:
                # Get database size
                result = session.run("CALL dbms.database.size($database)", database=self.database)
                size_info = result.single()
                if size_info:
                    stats['database_size'] = {
                        'total_size': size_info['totalSize'],
                        'log_size': size_info['logSize']
                    }
                
                # Get node counts by label
                result = session.run("""
                MATCH (n)
                RETURN labels(n) AS labels, count(*) AS count
                ORDER BY count DESC
                """)
                
                node_counts = {}
                for record in result:
                    label = record['labels'][0] if record['labels'] else 'unlabeled'
                    node_counts[label] = record['count']
                
                stats['node_counts'] = node_counts
                
                # Get relationship counts by type
                result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS type, count(*) AS count
                ORDER BY count DESC
                """)
                
                relationship_counts = {}
                for record in result:
                    relationship_counts[record['type']] = record['count']
                
                stats['relationship_counts'] = relationship_counts
                
                # Get constraint and index information
                result = session.run("SHOW CONSTRAINTS")
                constraints = [dict(record) for record in result]
                stats['constraints'] = constraints
                
                result = session.run("SHOW INDEXES")
                indexes = [dict(record) for record in result]
                stats['indexes'] = indexes
                
                logger.info("Successfully retrieved database statistics")
                return stats
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return {'error': str(e)}