"""
Database Integration Runner

This script demonstrates the database integration functionality by setting up
the databases, loading sample data, and running sample queries.
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.databases.base import BaseDBConnector
from src.databases.relational import PostgreSQLConnector
from src.databases.document import MongoDBConnector
from src.databases.graph import Neo4jConnector
from src.databases.vector import PineconeConnector
from src.databases.sync import DatabaseSynchronizer
from src.databases.query import QueryOrchestrator
from src.databases.setup_databases import (
    load_config,
    setup_database_connectors,
    connect_databases,
    create_database_schemas,
    load_sample_data,
    setup_synchronization,
    setup_query_orchestration,
    run_sample_queries
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the database integration demonstration."""
    parser = argparse.ArgumentParser(description='Demonstrate database integration functionality')
    parser.add_argument('--config', default='config/database_config.json', help='Path to configuration file')
    parser.add_argument('--data-dir', default='output/processed', help='Directory containing sample data files')
    parser.add_argument('--skip-load', action='store_true', help='Skip loading sample data')
    parser.add_argument('--skip-sync', action='store_true', help='Skip database synchronization')
    parser.add_argument('--skip-queries', action='store_true', help='Skip running sample queries')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    args = parser.parse_args()
    
    logger.info("Starting database integration demonstration")
    
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
        logger.info(f"Loading sample data from {args.data_dir}")
        data_results = load_sample_data(connectors, args.data_dir)
        logger.info(f"Data loading results: {data_results}")
    
    # Set up synchronization
    synchronizer = None
    if not args.skip_sync:
        logger.info("Setting up database synchronization")
        synchronizer = setup_synchronization(connectors, config)
        if synchronizer:
            # Synchronize all data
            logger.info("Performing full synchronization")
            sync_result = synchronizer.synchronize_all()
            logger.info(f"Full synchronization result: {sync_result}")
    
    # Set up query orchestration
    logger.info("Setting up query orchestration")
    orchestrator = setup_query_orchestration(connectors, config)
    
    # Run sample queries
    if not args.skip_queries and orchestrator:
        logger.info("Running sample queries")
        query_results = run_sample_queries(orchestrator)
        logger.info(f"Sample queries completed: {len(query_results)} queries executed")
    
    # Show database statistics
    if args.stats:
        logger.info("Retrieving database statistics")
        stats = {}
        
        for db_type, connector in connectors.items():
            try:
                db_stats = connector.get_stats()
                stats[db_type] = db_stats
                logger.info(f"{db_type.capitalize()} database statistics: {db_stats}")
            except Exception as e:
                logger.error(f"Error getting statistics for {db_type} database: {e}")
        
        if synchronizer:
            try:
                sync_stats = synchronizer.get_stats()
                stats['synchronization'] = sync_stats
                logger.info(f"Synchronization statistics: {sync_stats}")
            except Exception as e:
                logger.error(f"Error getting synchronization statistics: {e}")
        
        if orchestrator:
            try:
                query_stats = orchestrator.get_cache_stats()
                stats['query_orchestration'] = query_stats
                logger.info(f"Query orchestration statistics: {query_stats}")
            except Exception as e:
                logger.error(f"Error getting query orchestration statistics: {e}")
    
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
    
    logger.info("Database integration demonstration completed")


if __name__ == "__main__":
    main()