"""
Database Configuration Update Script

This script helps update the database_config.json file with your database connection details.
It will prompt you for the necessary information and update the configuration file.
"""

import os
import json
import getpass
import argparse


def load_config(config_path):
    """Load the existing configuration file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing configuration file at {config_path}")
        return None


def save_config(config, config_path):
    """Save the updated configuration to the file."""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def update_postgresql_config(config):
    """Update PostgreSQL configuration."""
    print("\n=== PostgreSQL Configuration ===")
    
    postgresql = config.get('postgresql', {})
    
    postgresql['host'] = input(f"Host [default: {postgresql.get('host', 'localhost')}]: ") or postgresql.get('host', 'localhost')
    
    port_str = input(f"Port [default: {postgresql.get('port', 5432)}]: ") or str(postgresql.get('port', 5432))
    postgresql['port'] = int(port_str)
    
    postgresql['user'] = input(f"Username [default: {postgresql.get('user', 'postgres')}]: ") or postgresql.get('user', 'postgres')
    
    # Securely prompt for password
    default_password = postgresql.get('password', '')
    password_prompt = "Password"
    if default_password:
        password_prompt += " [press Enter to keep current password]"
    password_prompt += ": "
    
    password = getpass.getpass(password_prompt)
    if password:
        postgresql['password'] = password
    elif 'password' not in postgresql:
        postgresql['password'] = ''
    
    postgresql['database'] = input(f"Database name [default: {postgresql.get('database', 'healthcare')}]: ") or postgresql.get('database', 'healthcare')
    postgresql['schema'] = input(f"Schema [default: {postgresql.get('schema', 'public')}]: ") or postgresql.get('schema', 'public')
    
    # Add default values for other parameters if they don't exist
    if 'connection_timeout' not in postgresql:
        postgresql['connection_timeout'] = 30
    if 'connection_retries' not in postgresql:
        postgresql['connection_retries'] = 3
    if 'retry_delay' not in postgresql:
        postgresql['retry_delay'] = 5
    
    config['postgresql'] = postgresql
    return config


def update_mongodb_config(config):
    """Update MongoDB configuration."""
    print("\n=== MongoDB Configuration ===")
    
    mongodb = config.get('mongodb', {})
    
    mongodb['host'] = input(f"Host [default: {mongodb.get('host', 'localhost')}]: ") or mongodb.get('host', 'localhost')
    
    port_str = input(f"Port [default: {mongodb.get('port', 27017)}]: ") or str(mongodb.get('port', 27017))
    mongodb['port'] = int(port_str)
    
    mongodb['database'] = input(f"Database name [default: {mongodb.get('database', 'healthcare')}]: ") or mongodb.get('database', 'healthcare')
    
    use_auth = input("Use authentication? (y/n) [default: n]: ").lower() == 'y'
    
    if use_auth:
        mongodb['username'] = input(f"Username [default: {mongodb.get('username', '')}]: ") or mongodb.get('username', '')
        
        # Securely prompt for password
        default_password = mongodb.get('password', '')
        password_prompt = "Password"
        if default_password:
            password_prompt += " [press Enter to keep current password]"
        password_prompt += ": "
        
        password = getpass.getpass(password_prompt)
        if password:
            mongodb['password'] = password
        elif 'password' not in mongodb:
            mongodb['password'] = ''
        
        mongodb['auth_source'] = input(f"Auth source [default: {mongodb.get('auth_source', 'admin')}]: ") or mongodb.get('auth_source', 'admin')
    else:
        mongodb['username'] = ''
        mongodb['password'] = ''
        mongodb['auth_source'] = 'admin'
    
    # Add default values for other parameters if they don't exist
    if 'connection_timeout' not in mongodb:
        mongodb['connection_timeout'] = 30000
    if 'connection_retries' not in mongodb:
        mongodb['connection_retries'] = 3
    if 'retry_delay' not in mongodb:
        mongodb['retry_delay'] = 5
    
    config['mongodb'] = mongodb
    return config


def update_neo4j_config(config):
    """Update Neo4j configuration."""
    print("\n=== Neo4j Configuration ===")
    
    neo4j = config.get('neo4j', {})
    
    uri = neo4j.get('uri', 'bolt://localhost:7687')
    neo4j['uri'] = input(f"URI [default: {uri}]: ") or uri
    
    neo4j['username'] = input(f"Username [default: {neo4j.get('username', 'neo4j')}]: ") or neo4j.get('username', 'neo4j')
    
    # Securely prompt for password
    default_password = neo4j.get('password', '')
    password_prompt = "Password"
    if default_password:
        password_prompt += " [press Enter to keep current password]"
    password_prompt += ": "
    
    password = getpass.getpass(password_prompt)
    if password:
        neo4j['password'] = password
    elif 'password' not in neo4j:
        neo4j['password'] = ''
    
    neo4j['database'] = input(f"Database name [default: {neo4j.get('database', 'healthcare')}]: ") or neo4j.get('database', 'healthcare')
    
    # Add default values for other parameters if they don't exist
    if 'connection_timeout' not in neo4j:
        neo4j['connection_timeout'] = 30
    if 'connection_retries' not in neo4j:
        neo4j['connection_retries'] = 3
    if 'retry_delay' not in neo4j:
        neo4j['retry_delay'] = 5
    
    config['neo4j'] = neo4j
    return config


def update_pinecone_config(config):
    """Update Pinecone configuration."""
    print("\n=== Pinecone Configuration ===")
    
    pinecone = config.get('pinecone', {})
    
    # Securely prompt for API key
    default_api_key = pinecone.get('api_key', '')
    api_key_prompt = "API Key"
    if default_api_key:
        api_key_prompt += " [press Enter to keep current API key]"
    api_key_prompt += ": "
    
    api_key = getpass.getpass(api_key_prompt)
    if api_key:
        pinecone['api_key'] = api_key
    elif 'api_key' not in pinecone:
        pinecone['api_key'] = ''
    
    pinecone['environment'] = input(f"Environment [default: {pinecone.get('environment', 'us-west1-gcp')}]: ") or pinecone.get('environment', 'us-west1-gcp')
    pinecone['project_name'] = input(f"Project name [default: {pinecone.get('project_name', 'healthcare')}]: ") or pinecone.get('project_name', 'healthcare')
    
    dimension_str = input(f"Vector dimension [default: {pinecone.get('dimension', 768)}]: ") or str(pinecone.get('dimension', 768))
    pinecone['dimension'] = int(dimension_str)
    
    pinecone['metric'] = input(f"Metric [default: {pinecone.get('metric', 'cosine')}]: ") or pinecone.get('metric', 'cosine')
    pinecone['pod_type'] = input(f"Pod type [default: {pinecone.get('pod_type', 'p1.x1')}]: ") or pinecone.get('pod_type', 'p1.x1')
    pinecone['index_name'] = input(f"Index name [default: {pinecone.get('index_name', 'healthcare-embeddings')}]: ") or pinecone.get('index_name', 'healthcare-embeddings')
    
    # Add default values for other parameters if they don't exist
    if 'connection_retries' not in pinecone:
        pinecone['connection_retries'] = 3
    if 'retry_delay' not in pinecone:
        pinecone['retry_delay'] = 5
    
    config['pinecone'] = pinecone
    return config


def update_database_names(config):
    """Update database names."""
    print("\n=== Database Names ===")
    
    config['relational_database'] = input(f"Relational database name [default: {config.get('relational_database', 'healthcare')}]: ") or config.get('relational_database', 'healthcare')
    config['document_database'] = input(f"Document database name [default: {config.get('document_database', 'healthcare')}]: ") or config.get('document_database', 'healthcare')
    config['graph_database'] = input(f"Graph database name [default: {config.get('graph_database', 'healthcare')}]: ") or config.get('graph_database', 'healthcare')
    config['vector_database'] = input(f"Vector database name [default: {config.get('vector_database', 'healthcare-embeddings')}]: ") or config.get('vector_database', 'healthcare-embeddings')
    
    return config


def update_synchronization_config(config):
    """Update synchronization configuration."""
    print("\n=== Synchronization Configuration ===")
    
    sync = config.get('synchronization', {})
    
    batch_size_str = input(f"Batch size [default: {sync.get('batch_size', 100)}]: ") or str(sync.get('batch_size', 100))
    sync['batch_size'] = int(batch_size_str)
    
    sync_interval_str = input(f"Sync interval (seconds) [default: {sync.get('sync_interval', 60)}]: ") or str(sync.get('sync_interval', 60))
    sync['sync_interval'] = int(sync_interval_str)
    
    sync['change_log_table'] = input(f"Change log table [default: {sync.get('change_log_table', 'sync_change_log')}]: ") or sync.get('change_log_table', 'sync_change_log')
    
    config['synchronization'] = sync
    return config


def update_query_orchestration_config(config):
    """Update query orchestration configuration."""
    print("\n=== Query Orchestration Configuration ===")
    
    query = config.get('query_orchestration', {})
    
    cache_enabled = input(f"Enable cache? (y/n) [default: {'y' if query.get('cache_enabled', True) else 'n'}]: ").lower()
    if cache_enabled:
        query['cache_enabled'] = cache_enabled == 'y' or (not cache_enabled and query.get('cache_enabled', True))
    
    if query['cache_enabled']:
        cache_ttl_str = input(f"Cache TTL (seconds) [default: {query.get('cache_ttl', 300)}]: ") or str(query.get('cache_ttl', 300))
        query['cache_ttl'] = int(cache_ttl_str)
        
        cache_size_str = input(f"Cache size [default: {query.get('cache_size', 1000)}]: ") or str(query.get('cache_size', 1000))
        query['cache_size'] = int(cache_size_str)
    
    query_timeout_str = input(f"Query timeout (seconds) [default: {query.get('query_timeout', 30)}]: ") or str(query.get('query_timeout', 30))
    query['query_timeout'] = int(query_timeout_str)
    
    config['query_orchestration'] = query
    return config


def main():
    """Main function to update database configuration."""
    parser = argparse.ArgumentParser(description='Update database configuration')
    parser.add_argument('--config', default='config/database_config.json', help='Path to configuration file')
    parser.add_argument('--postgresql', action='store_true', help='Update PostgreSQL configuration')
    parser.add_argument('--mongodb', action='store_true', help='Update MongoDB configuration')
    parser.add_argument('--neo4j', action='store_true', help='Update Neo4j configuration')
    parser.add_argument('--pinecone', action='store_true', help='Update Pinecone configuration')
    parser.add_argument('--all', action='store_true', help='Update all configurations')
    args = parser.parse_args()
    
    # Load existing configuration
    config = load_config(args.config)
    if config is None:
        print("Creating new configuration file...")
        config = {}
    
    # Determine which configurations to update
    update_all = args.all or not (args.postgresql or args.mongodb or args.neo4j or args.pinecone)
    
    # Update configurations
    if update_all or args.postgresql:
        config = update_postgresql_config(config)
    
    if update_all or args.mongodb:
        config = update_mongodb_config(config)
    
    if update_all or args.neo4j:
        config = update_neo4j_config(config)
    
    if update_all or args.pinecone:
        config = update_pinecone_config(config)
    
    if update_all:
        config = update_database_names(config)
        config = update_synchronization_config(config)
        config = update_query_orchestration_config(config)
    
    # Save updated configuration
    if save_config(config, args.config):
        print("\nConfiguration updated successfully!")
        print(f"You can now run: python run_databases.py --config {args.config} --skip-load --skip-sync --skip-queries")
        print("to test the database connections.")


if __name__ == "__main__":
    main()