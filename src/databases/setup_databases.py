"""
Database Setup Script

This script sets up the database systems, creates the necessary schemas,
and loads sample data for testing.
"""

import os
import json
import logging
import argparse
from typing import Dict, Any, List

from .base import BaseDBConnector
from .relational import PostgreSQLConnector
from .document import MongoDBConnector
from .graph import Neo4jConnector
from .vector import PineconeConnector
from .sync import DatabaseSynchronizer
from .query import QueryOrchestrator
from .clinical_db import ClinicalDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Dictionary containing the configuration.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        return {}


def setup_database_connectors(config: Dict[str, Any]) -> Dict[str, BaseDBConnector]:
    """
    Set up database connectors based on configuration.
    
    Args:
        config: Configuration dictionary.
        
    Returns:
        Dictionary of database connectors.
    """
    connectors = {}
    
    # Set up PostgreSQL connector
    if 'postgresql' in config:
        try:
            connectors['relational'] = PostgreSQLConnector(config['postgresql'])
            logger.info("Created PostgreSQL connector")
        except Exception as e:
            logger.error(f"Error creating PostgreSQL connector: {e}")
    
    # Set up MongoDB connector
    if 'mongodb' in config:
        try:
            connectors['document'] = MongoDBConnector(config['mongodb'])
            logger.info("Created MongoDB connector")
        except Exception as e:
            logger.error(f"Error creating MongoDB connector: {e}")
    
    # Set up Neo4j connector
    if 'neo4j' in config:
        try:
            connectors['graph'] = Neo4jConnector(config['neo4j'])
            logger.info("Created Neo4j connector")
        except Exception as e:
            logger.error(f"Error creating Neo4j connector: {e}")
    
    # Set up Pinecone connector
    if 'pinecone' in config:
        try:
            connectors['vector'] = PineconeConnector(config['pinecone'])
            logger.info("Created Pinecone connector")
        except Exception as e:
            logger.error(f"Error creating Pinecone connector: {e}")
    
    return connectors


def connect_databases(connectors: Dict[str, BaseDBConnector]) -> Dict[str, bool]:
    """
    Connect to all databases.
    
    Args:
        connectors: Dictionary of database connectors.
        
    Returns:
        Dictionary of connection results.
    """
    results = {}
    
    for db_type, connector in connectors.items():
        try:
            success = connector.connect()
            results[db_type] = success
            if success:
                logger.info(f"Connected to {db_type} database")
            else:
                logger.error(f"Failed to connect to {db_type} database")
        except Exception as e:
            logger.error(f"Error connecting to {db_type} database: {e}")
            results[db_type] = False
    
    return results


def create_database_schemas(connectors: Dict[str, BaseDBConnector], config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Create database schemas.
    
    Args:
        connectors: Dictionary of database connectors.
        config: Configuration dictionary.
        
    Returns:
        Dictionary of schema creation results.
    """
    results = {}
    
    for db_type, connector in connectors.items():
        try:
            # Create database if specified in config
            if f"{db_type}_database" in config:
                database_name = config[f"{db_type}_database"]
                success = connector.create_database(database_name)
                if success:
                    logger.info(f"Created {db_type} database: {database_name}")
                else:
                    logger.error(f"Failed to create {db_type} database: {database_name}")
            
            # Create schema
            success = connector.create_schema()
            results[db_type] = success
            if success:
                logger.info(f"Created {db_type} database schema")
            else:
                logger.error(f"Failed to create {db_type} database schema")
        except Exception as e:
            logger.error(f"Error creating {db_type} database schema: {e}")
            results[db_type] = False
    
    # Create Clinical domain schema if relational database is available
    if 'relational' in connectors and connectors['relational'].is_connected and results.get('relational', False):
        try:
            clinical_db_manager = ClinicalDBManager(connectors['relational'])
            success = clinical_db_manager.create_clinical_schema()
            results['clinical'] = success
            if success:
                logger.info("Created Clinical domain database schema")
            else:
                logger.error("Failed to create Clinical domain database schema")
        except Exception as e:
            logger.error(f"Error creating Clinical domain database schema: {e}")
            results['clinical'] = False
    
    return results


def load_sample_data(connectors: Dict[str, BaseDBConnector], data_dir: str) -> Dict[str, Dict[str, int]]:
    """
    Load sample data into the databases.
    
    Args:
        connectors: Dictionary of database connectors.
        data_dir: Directory containing sample data files.
        
    Returns:
        Dictionary of data loading results.
    """
    results = {}
    
    # Define mappings between file names and database collections/tables
    file_mappings = {
        'members.json': {'relational': 'members', 'graph': 'Member'},
        'providers.json': {'relational': 'providers', 'graph': 'Provider'},
        'encounters.json': {'relational': 'encounters', 'graph': 'Encounter'},
        'conditions.json': {'relational': 'conditions', 'graph': 'Condition'},
        'medications.json': {'relational': 'medications', 'graph': 'Medication'},
        'procedures.json': {'relational': 'procedures', 'graph': 'Procedure'},
        'claims.json': {'relational': 'claims', 'graph': 'Claim'},
        'authorizations.json': {'relational': 'authorizations', 'graph': 'Authorization'},
        'eobs.json': {'relational': 'eobs', 'graph': 'EOB'},
        'plans.json': {'relational': 'plans', 'graph': 'Plan'},
        'clinical_notes.json': {'document': 'clinical_notes'},
        'communications.json': {'document': 'communications'},
        'care_plans.json': {'document': 'care_plans'},
        'authorization_rationales.json': {'document': 'authorization_rationales'},
        'mental_health_narratives.json': {'document': 'mental_health_narratives'},
        'patient_generated_data.json': {'document': 'patient_generated_data'},
        'provider_communications.json': {'document': 'provider_communications'},
        'telehealth_documentation.json': {'document': 'telehealth_documentation'},
        'insurance_communications.json': {'document': 'insurance_communications'},
        'care_episodes.json': {'graph': 'CareEpisode'},
        'sdoh_assessments.json': {'graph': 'SDOHAssessment'},
        'risk_assessments.json': {'graph': 'RiskAssessment'},
        'provider_network.json': {'graph': 'ProviderNetwork'},
        'provider_relationships.json': {'graph': 'PROVIDER_RELATIONSHIP'},
        # Clinical domain data files
        'clinical_encounters.json': {'relational': 'clinical_encounters', 'graph': 'ClinicalEncounter'},
        'encounter_participants.json': {'relational': 'encounter_participants'},
        'encounter_locations.json': {'relational': 'encounter_locations'},
        'encounter_diagnoses.json': {'relational': 'encounter_diagnoses'},
        'encounter_procedures.json': {'relational': 'encounter_procedures'},
        'clinical_notes_detailed.json': {'relational': 'clinical_notes', 'document': 'clinical_notes_detailed'},
        'encounter_services.json': {'relational': 'encounter_services'},
        'encounter_assessments.json': {'relational': 'encounter_assessments'},
        'encounter_medications.json': {'relational': 'encounter_medications'},
        'encounter_transitions.json': {'relational': 'encounter_transitions'}
    }
    
    # Load each file and insert into appropriate databases
    for filename, db_mappings in file_mappings.items():
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue
        
        try:
            # Load data from file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not data:
                logger.warning(f"No data found in {file_path}")
                continue
            
            # Insert data into each mapped database
            for db_type, collection_name in db_mappings.items():
                if db_type in connectors:
                    connector = connectors[db_type]
                    success = connector.insert_data(data, collection_name)
                    
                    if success:
                        record_count = len(data) if isinstance(data, list) else 1
                        logger.info(f"Inserted {record_count} records from {filename} into {db_type}.{collection_name}")
                        
                        # Update results
                        if db_type not in results:
                            results[db_type] = {}
                        results[db_type][collection_name] = record_count
                    else:
                        logger.error(f"Failed to insert data from {filename} into {db_type}.{collection_name}")
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
    
    return results


def setup_synchronization(connectors: Dict[str, BaseDBConnector], config: Dict[str, Any]) -> DatabaseSynchronizer:
    """
    Set up database synchronization.
    
    Args:
        connectors: Dictionary of database connectors.
        config: Configuration dictionary.
        
    Returns:
        DatabaseSynchronizer instance.
    """
    try:
        sync_config = config.get('synchronization', {})
        synchronizer = DatabaseSynchronizer(connectors, sync_config)
        logger.info("Created database synchronizer")
        
        # Set up change tracking if relational database is available
        if 'relational' in connectors and connectors['relational'].is_connected:
            success = synchronizer.setup_change_tracking()
            if success:
                logger.info("Set up change tracking")
            else:
                logger.error("Failed to set up change tracking")
        
        return synchronizer
    except Exception as e:
        logger.error(f"Error setting up database synchronization: {e}")
        return None


def setup_query_orchestration(connectors: Dict[str, BaseDBConnector], config: Dict[str, Any]) -> QueryOrchestrator:
    """
    Set up query orchestration.
    
    Args:
        connectors: Dictionary of database connectors.
        config: Configuration dictionary.
        
    Returns:
        QueryOrchestrator instance.
    """
    try:
        query_config = config.get('query_orchestration', {})
        orchestrator = QueryOrchestrator(connectors, query_config)
        logger.info("Created query orchestrator")
        return orchestrator
    except Exception as e:
        logger.error(f"Error setting up query orchestration: {e}")
        return None


def run_sample_queries(orchestrator: QueryOrchestrator) -> Dict[str, Any]:
    """
    Run sample queries using the query orchestrator.
    
    Args:
        orchestrator: QueryOrchestrator instance.
        
    Returns:
        Dictionary of query results.
    """
    results = {}
    
    # Sample queries to run
    sample_queries = [
        {
            'name': 'member_details',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'member_conditions',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'member_medications',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'member_encounters',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'member_claims',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'member_authorizations',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'member_clinical_notes',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'semantic_search',
            'parameters': {'query_text': 'diabetes management', 'top_k': 5}
        },
        {
            'name': 'clinical_encounters',
            'parameters': {'member_id': 'MEM00000001'}
        },
        {
            'name': 'clinical_encounter_details',
            'parameters': {'encounter_id': 'ENC123456'}
        }
    ]
    
    # Run each query
    for query in sample_queries:
        try:
            query_name = query['name']
            parameters = query['parameters']
            
            logger.info(f"Running query: {query_name} with parameters: {parameters}")
            result = orchestrator.execute_query(query_name, parameters)
            
            results[query_name] = result
            logger.info(f"Query {query_name} completed successfully")
        except Exception as e:
            logger.error(f"Error running query {query['name']}: {e}")
            results[query['name']] = {'error': str(e)}
    
    return results


def main():
    """Main function to set up databases and run sample queries."""
    parser = argparse.ArgumentParser(description='Set up database systems and load sample data')
    parser.add_argument('--config', default='config/database_config.json', help='Path to configuration file')
    parser.add_argument('--data-dir', default='output/processed', help='Directory containing sample data files')
    parser.add_argument('--skip-load', action='store_true', help='Skip loading sample data')
    parser.add_argument('--skip-sync', action='store_true', help='Skip database synchronization')
    parser.add_argument('--skip-queries', action='store_true', help='Skip running sample queries')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    # Set up database connectors
    connectors = setup_database_connectors(config)
    if not connectors:
        logger.error("Failed to set up any database connectors. Exiting.")
        return
    
    # Connect to databases
    connection_results = connect_databases(connectors)
    if not any(connection_results.values()):
        logger.error("Failed to connect to any databases. Exiting.")
        return
    
    # Create database schemas
    schema_results = create_database_schemas(connectors, config)
    
    # Load sample data
    if not args.skip_load:
        data_results = load_sample_data(connectors, args.data_dir)
        logger.info(f"Data loading results: {data_results}")
    
    # Set up synchronization
    if not args.skip_sync:
        synchronizer = setup_synchronization(connectors, config)
        if synchronizer:
            # Synchronize all data
            sync_result = synchronizer.synchronize_all()
            logger.info(f"Full synchronization result: {sync_result}")
    
    # Set up query orchestration
    orchestrator = setup_query_orchestration(connectors, config)
    
    # Run sample queries
    if not args.skip_queries and orchestrator:
        query_results = run_sample_queries(orchestrator)
        logger.info(f"Sample queries completed: {len(query_results)} queries executed")
    
    # Disconnect from databases
    for db_type, connector in connectors.items():
        try:
            success = connector.disconnect()
            if success:
                logger.info(f"Disconnected from {db_type} database")
            else:
                logger.error(f"Failed to disconnect from {db_type} database")
        except Exception as e:
            logger.error(f"Error disconnecting from {db_type} database: {e}")
    
    logger.info("Database setup completed")


if __name__ == "__main__":
    main()