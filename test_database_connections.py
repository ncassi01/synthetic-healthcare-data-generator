"""
Database Connection Test Script

This script tests the connections to all configured databases to verify
that they are properly installed and configured.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def test_postgresql_connection(config: Dict[str, Any]) -> bool:
    """
    Test connection to PostgreSQL.
    
    Args:
        config: PostgreSQL configuration dictionary.
        
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        import psycopg2
        
        logger.info("Testing PostgreSQL connection...")
        
        # Extract connection parameters
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        user = config.get('user', 'postgres')
        password = config.get('password', '')
        database = config.get('database', 'healthcare')
        
        # Create connection string
        conn_string = f"host={host} port={port} user={user} password={password} dbname={database}"
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(conn_string)
        
        # Test connection with a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info(f"PostgreSQL connection successful. Version: {version}")
        return True
    except ImportError:
        logger.error("PostgreSQL driver (psycopg2) not installed. Please install it with: pip install psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return False


def test_mongodb_connection(config: Dict[str, Any]) -> bool:
    """
    Test connection to MongoDB.
    
    Args:
        config: MongoDB configuration dictionary.
        
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        import pymongo
        
        logger.info("Testing MongoDB connection...")
        
        # Extract connection parameters
        host = config.get('host', 'localhost')
        port = config.get('port', 27017)
        username = config.get('username', '')
        password = config.get('password', '')
        database = config.get('database', 'healthcare')
        auth_source = config.get('auth_source', 'admin')
        
        # Create connection URI
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        # Connect to MongoDB
        client = pymongo.MongoClient(uri)
        
        # Test connection
        server_info = client.server_info()
        
        # Close connection
        client.close()
        
        logger.info(f"MongoDB connection successful. Version: {server_info.get('version', 'unknown')}")
        return True
    except ImportError:
        logger.error("MongoDB driver (pymongo) not installed. Please install it with: pip install pymongo")
        return False
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return False


def test_neo4j_connection(config: Dict[str, Any]) -> bool:
    """
    Test connection to Neo4j.
    
    Args:
        config: Neo4j configuration dictionary.
        
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        from neo4j import GraphDatabase
        
        logger.info("Testing Neo4j connection...")
        
        # Extract connection parameters
        uri = config.get('uri', 'bolt://localhost:7687')
        username = config.get('username', 'neo4j')
        password = config.get('password', '')
        database = config.get('database', 'healthcare')
        
        # Connect to Neo4j
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Test connection with a simple query
        with driver.session(database=database) as session:
            result = session.run("RETURN 'Connection successful' AS message")
            message = result.single()[0]
        
        # Close connection
        driver.close()
        
        logger.info(f"Neo4j connection successful. Message: {message}")
        return True
    except ImportError:
        logger.error("Neo4j driver not installed. Please install it with: pip install neo4j")
        return False
    except Exception as e:
        logger.error(f"Error connecting to Neo4j: {e}")
        return False


def test_pinecone_connection(config: Dict[str, Any]) -> bool:
    """
    Test connection to Pinecone.
    
    Args:
        config: Pinecone configuration dictionary.
        
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        import pinecone
        
        logger.info("Testing Pinecone connection...")
        
        # Extract connection parameters
        api_key = config.get('api_key', '')
        environment = config.get('environment', 'us-west1-gcp')
        index_name = config.get('index_name', 'healthcare-embeddings')
        
        if not api_key:
            logger.error("Pinecone API key not provided")
            return False
        
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        
        # Check if index exists
        indexes = pinecone.list_indexes()
        
        if index_name in indexes:
            logger.info(f"Pinecone connection successful. Index '{index_name}' exists.")
            return True
        else:
            logger.warning(f"Pinecone connection successful, but index '{index_name}' does not exist.")
            logger.warning(f"Available indexes: {indexes}")
            return False
    except ImportError:
        logger.error("Pinecone client not installed. Please install it with: pip install pinecone-client")
        return False
    except Exception as e:
        logger.error(f"Error connecting to Pinecone: {e}")
        return False


def main():
    """Main function to test database connections."""
    parser = argparse.ArgumentParser(description='Test database connections')
    parser.add_argument('--config', default='config/database_config.json', help='Path to configuration file')
    parser.add_argument('--postgresql', action='store_true', help='Test PostgreSQL connection only')
    parser.add_argument('--mongodb', action='store_true', help='Test MongoDB connection only')
    parser.add_argument('--neo4j', action='store_true', help='Test Neo4j connection only')
    parser.add_argument('--pinecone', action='store_true', help='Test Pinecone connection only')
    parser.add_argument('--all', action='store_true', help='Test all database connections')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    # Determine which connections to test
    test_all = args.all or not (args.postgresql or args.mongodb or args.neo4j or args.pinecone)
    
    results = {}
    
    # Test PostgreSQL connection
    if test_all or args.postgresql:
        if 'postgresql' in config:
            results['PostgreSQL'] = test_postgresql_connection(config['postgresql'])
        else:
            logger.error("PostgreSQL configuration not found in config file")
            results['PostgreSQL'] = False
    
    # Test MongoDB connection
    if test_all or args.mongodb:
        if 'mongodb' in config:
            results['MongoDB'] = test_mongodb_connection(config['mongodb'])
        else:
            logger.error("MongoDB configuration not found in config file")
            results['MongoDB'] = False
    
    # Test Neo4j connection
    if test_all or args.neo4j:
        if 'neo4j' in config:
            results['Neo4j'] = test_neo4j_connection(config['neo4j'])
        else:
            logger.error("Neo4j configuration not found in config file")
            results['Neo4j'] = False
    
    # Test Pinecone connection
    if test_all or args.pinecone:
        if 'pinecone' in config:
            results['Pinecone'] = test_pinecone_connection(config['pinecone'])
        else:
            logger.error("Pinecone configuration not found in config file")
            results['Pinecone'] = False
    
    # Print summary
    print("\n=== Database Connection Test Results ===")
    for db, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"{db}: {status}")
    
    # Check if all tests passed
    all_passed = all(results.values())
    if all_passed:
        print("\nAll database connections are working correctly!")
        print("You can now run the full database setup:")
        print(f"python run_databases.py --config {args.config} --data-dir output/processed")
    else:
        print("\nSome database connections failed. Please check the error messages above.")
        print("For troubleshooting, refer to the database_installation_guide.md file.")


if __name__ == "__main__":
    main()