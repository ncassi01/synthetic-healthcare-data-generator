"""
Relational Database Connector Module

This module provides a connector for PostgreSQL relational database.
It implements the BaseDBConnector interface and provides PostgreSQL-specific
functionality.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor, execute_values

from .base import BaseDBConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLConnector(BaseDBConnector):
    """
    PostgreSQL database connector.
    
    This class provides methods to interact with a PostgreSQL database.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the PostgreSQL connector with configuration parameters.
        
        Args:
            config: Dictionary containing configuration parameters for the PostgreSQL connection.
                   Required keys: host, port, user, password, database
        """
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5432)
        self.user = config.get('user', 'postgres')
        self.password = config.get('password', '')
        self.database = config.get('database', 'postgres')
        self.schema = config.get('schema', 'public')
        self.connection_timeout = config.get('connection_timeout', 30)
        self.connection_retries = config.get('connection_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
    
    def connect(self) -> bool:
        """
        Establish a connection to the PostgreSQL database.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        for attempt in range(self.connection_retries):
            try:
                logger.info(f"Connecting to PostgreSQL database {self.database} on {self.host}:{self.port}")
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    connect_timeout=self.connection_timeout
                )
                self.connection.autocommit = False
                self.is_connected = True
                logger.info("Successfully connected to PostgreSQL database")
                return True
            except psycopg2.Error as e:
                logger.error(f"Failed to connect to PostgreSQL database (attempt {attempt+1}/{self.connection_retries}): {e}")
                if attempt < self.connection_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Maximum connection attempts reached. Could not connect to PostgreSQL database.")
        return False
    
    def disconnect(self) -> bool:
        """
        Close the connection to the PostgreSQL database.
        
        Returns:
            bool: True if disconnection was successful, False otherwise.
        """
        if self.connection and self.is_connected:
            try:
                self.connection.close()
                self.is_connected = False
                logger.info("Disconnected from PostgreSQL database")
                return True
            except psycopg2.Error as e:
                logger.error(f"Error disconnecting from PostgreSQL database: {e}")
                return False
        return True  # Already disconnected
    
    def create_database(self, database_name: str) -> bool:
        """
        Create a new PostgreSQL database.
        
        Args:
            database_name: Name of the database to create.
            
        Returns:
            bool: True if database creation was successful, False otherwise.
        """
        # Connect to the default postgres database to create a new database
        temp_config = self.config.copy()
        temp_config['database'] = 'postgres'
        
        try:
            temp_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database='postgres',
                connect_timeout=self.connection_timeout
            )
            temp_conn.autocommit = True
            
            with temp_conn.cursor() as cursor:
                # Check if database already exists
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
                if cursor.fetchone():
                    logger.info(f"Database {database_name} already exists")
                    temp_conn.close()
                    return True
                
                # Create the database
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
                logger.info(f"Created database {database_name}")
                
            temp_conn.close()
            return True
        except psycopg2.Error as e:
            logger.error(f"Error creating database {database_name}: {e}")
            return False
    
    def create_schema(self) -> bool:
        """
        Create the database schema (tables, indexes, etc.).
        
        Returns:
            bool: True if schema creation was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Create schema if it doesn't exist
                cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(self.schema)))
                
                # Create tables
                self._create_members_table(cursor)
                self._create_providers_table(cursor)
                self._create_encounters_table(cursor)
                self._create_conditions_table(cursor)
                self._create_medications_table(cursor)
                self._create_procedures_table(cursor)
                self._create_claims_table(cursor)
                self._create_authorizations_table(cursor)
                self._create_eobs_table(cursor)
                self._create_plans_table(cursor)
                
                self.connection.commit()
                logger.info("Successfully created database schema")
                return True
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error creating schema: {e}")
            return False
    
    def _create_members_table(self, cursor):
        """Create the members table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.members (
                id VARCHAR(20) PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                date_of_birth DATE NOT NULL,
                gender VARCHAR(20) NOT NULL,
                address JSONB NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                insurance JSONB NOT NULL,
                primary_care_provider JSONB,
                risk_score FLOAT,
                conditions JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(sql.Identifier(self.schema)))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_members_last_name ON {}.members (last_name)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_members_dob ON {}.members (date_of_birth)
        """).format(sql.Identifier(self.schema)))
    
    def _create_providers_table(self, cursor):
        """Create the providers table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.providers (
                id VARCHAR(20) PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                credentials VARCHAR(50),
                specialty VARCHAR(100),
                address JSONB,
                phone VARCHAR(20),
                email VARCHAR(100),
                npi VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(sql.Identifier(self.schema)))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_providers_specialty ON {}.providers (specialty)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounters_table(self, cursor):
        """Create the encounters table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounters (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                provider_id VARCHAR(20) NOT NULL REFERENCES {}.providers(id),
                date DATE NOT NULL,
                type VARCHAR(50) NOT NULL,
                location VARCHAR(100),
                reason VARCHAR(200),
                diagnoses JSONB,
                procedures JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounters_member_id ON {}.encounters (member_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounters_date ON {}.encounters (date)
        """).format(sql.Identifier(self.schema)))
    
    def _create_conditions_table(self, cursor):
        """Create the conditions table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.conditions (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                code VARCHAR(20) NOT NULL,
                description VARCHAR(200) NOT NULL,
                onset_date DATE,
                end_date DATE,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_conditions_member_id ON {}.conditions (member_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_conditions_code ON {}.conditions (code)
        """).format(sql.Identifier(self.schema)))
    
    def _create_medications_table(self, cursor):
        """Create the medications table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.medications (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                name VARCHAR(100) NOT NULL,
                code VARCHAR(20),
                dosage VARCHAR(50),
                frequency VARCHAR(50),
                start_date DATE,
                end_date DATE,
                prescriber_id VARCHAR(20) REFERENCES {}.providers(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_medications_member_id ON {}.medications (member_id)
        """).format(sql.Identifier(self.schema)))
    
    def _create_procedures_table(self, cursor):
        """Create the procedures table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.procedures (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                provider_id VARCHAR(20) NOT NULL REFERENCES {}.providers(id),
                encounter_id VARCHAR(20) REFERENCES {}.encounters(id),
                code VARCHAR(20) NOT NULL,
                description VARCHAR(200) NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_procedures_member_id ON {}.procedures (member_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_procedures_code ON {}.procedures (code)
        """).format(sql.Identifier(self.schema)))
    
    def _create_claims_table(self, cursor):
        """Create the claims table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.claims (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                provider_id VARCHAR(20) NOT NULL REFERENCES {}.providers(id),
                date_of_service DATE NOT NULL,
                date_received DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                claim_type VARCHAR(50) NOT NULL,
                diagnosis_codes JSONB,
                service_lines JSONB NOT NULL,
                total_charge DECIMAL(10, 2) NOT NULL,
                total_allowed DECIMAL(10, 2) NOT NULL,
                total_paid DECIMAL(10, 2) NOT NULL,
                total_member_responsibility DECIMAL(10, 2) NOT NULL,
                payment_date DATE,
                related_authorization_id VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_claims_member_id ON {}.claims (member_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_claims_date_of_service ON {}.claims (date_of_service)
        """).format(sql.Identifier(self.schema)))
    
    def _create_authorizations_table(self, cursor):
        """Create the authorizations table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.authorizations (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                provider_id VARCHAR(20) NOT NULL REFERENCES {}.providers(id),
                date_requested DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                service_lines JSONB NOT NULL,
                diagnosis_codes JSONB,
                clinical_justification TEXT,
                authorization_type VARCHAR(50) NOT NULL,
                date_decision DATE,
                decision_rationale TEXT,
                expiration_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_authorizations_member_id ON {}.authorizations (member_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_authorizations_status ON {}.authorizations (status)
        """).format(sql.Identifier(self.schema)))
    
    def _create_eobs_table(self, cursor):
        """Create the EOBs (Explanation of Benefits) table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.eobs (
                id VARCHAR(20) PRIMARY KEY,
                member_id VARCHAR(20) NOT NULL REFERENCES {}.members(id),
                claim_id VARCHAR(20) NOT NULL REFERENCES {}.claims(id),
                date_issued DATE NOT NULL,
                service_date_start DATE NOT NULL,
                service_date_end DATE NOT NULL,
                provider_name VARCHAR(100) NOT NULL,
                provider_id VARCHAR(20) NOT NULL REFERENCES {}.providers(id),
                service_lines JSONB NOT NULL,
                total_billed DECIMAL(10, 2) NOT NULL,
                total_allowed DECIMAL(10, 2) NOT NULL,
                total_not_covered DECIMAL(10, 2) NOT NULL,
                total_discount DECIMAL(10, 2) NOT NULL,
                total_deductible DECIMAL(10, 2) NOT NULL,
                total_copay DECIMAL(10, 2) NOT NULL,
                total_coinsurance DECIMAL(10, 2) NOT NULL,
                total_plan_paid DECIMAL(10, 2) NOT NULL,
                total_member_responsibility DECIMAL(10, 2) NOT NULL,
                year_to_date_deductible DECIMAL(10, 2),
                year_to_date_out_of_pocket DECIMAL(10, 2),
                appeal_rights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_eobs_member_id ON {}.eobs (member_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_eobs_claim_id ON {}.eobs (claim_id)
        """).format(sql.Identifier(self.schema)))
    
    def _create_plans_table(self, cursor):
        """Create the plans table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.plans (
                id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                year INTEGER NOT NULL,
                deductible JSONB NOT NULL,
                out_of_pocket_max JSONB NOT NULL,
                copays JSONB NOT NULL,
                coinsurance DECIMAL(5, 2) NOT NULL,
                requires_referrals BOOLEAN NOT NULL,
                formulary_id VARCHAR(20),
                network_id VARCHAR(20),
                benefits JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(sql.Identifier(self.schema)))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_plans_type ON {}.plans (type)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_plans_year ON {}.plans (year)
        """).format(sql.Identifier(self.schema)))
    
    def insert_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   collection_name: str) -> bool:
        """
        Insert data into the PostgreSQL database.
        
        Args:
            data: Data to insert, either a single document or a list of documents.
            collection_name: Name of the table to insert data into.
            
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
            logger.warning(f"No data to insert into {collection_name}")
            return True
        
        try:
            with self.connection.cursor() as cursor:
                # Get column names from the first document
                columns = list(data[0].keys())
                
                # Prepare the SQL statement
                insert_stmt = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
                    sql.Identifier(self.schema),
                    sql.Identifier(collection_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                )
                
                # Prepare the values
                values = [[doc.get(col) for col in columns] for doc in data]
                
                # Execute the insert
                execute_values(cursor, insert_stmt, values)
                
                self.connection.commit()
                logger.info(f"Successfully inserted {len(data)} records into {collection_name}")
                return True
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error inserting data into {collection_name}: {e}")
            return False
    
    def query(self, query: str, collection_name: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query against the PostgreSQL database.
        
        Args:
            query: SQL query to execute.
            collection_name: Name of the table to query (used for logging).
            
        Returns:
            List of dictionaries containing the query results.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info(f"Query executed successfully on {collection_name}, returned {len(results)} results")
                return list(results)
        except psycopg2.Error as e:
            logger.error(f"Error executing query on {collection_name}: {e}")
            return []
    
    def update_data(self, query: str, update: Dict[str, Any], 
                   collection_name: str) -> bool:
        """
        Update data in the PostgreSQL database.
        
        Args:
            query: SQL WHERE clause to identify the records to update.
            update: Dictionary of column-value pairs to update.
            collection_name: Name of the table to update.
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Prepare the SET clause
                set_clause = sql.SQL(', ').join(
                    sql.SQL("{} = {}").format(
                        sql.Identifier(k),
                        sql.Literal(v)
                    ) for k, v in update.items()
                )
                
                # Prepare the full update statement
                update_stmt = sql.SQL("UPDATE {}.{} SET {} WHERE {}").format(
                    sql.Identifier(self.schema),
                    sql.Identifier(collection_name),
                    set_clause,
                    sql.SQL(query)
                )
                
                # Execute the update
                cursor.execute(update_stmt)
                affected_rows = cursor.rowcount
                
                self.connection.commit()
                logger.info(f"Successfully updated {affected_rows} records in {collection_name}")
                return True
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error updating data in {collection_name}: {e}")
            return False
    
    def delete_data(self, query: str, collection_name: str) -> bool:
        """
        Delete data from the PostgreSQL database.
        
        Args:
            query: SQL WHERE clause to identify the records to delete.
            collection_name: Name of the table to delete from.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Prepare the delete statement
                delete_stmt = sql.SQL("DELETE FROM {}.{} WHERE {}").format(
                    sql.Identifier(self.schema),
                    sql.Identifier(collection_name),
                    sql.SQL(query)
                )
                
                # Execute the delete
                cursor.execute(delete_stmt)
                affected_rows = cursor.rowcount
                
                self.connection.commit()
                logger.info(f"Successfully deleted {affected_rows} records from {collection_name}")
                return True
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error deleting data from {collection_name}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the PostgreSQL database.
        
        Returns:
            Dictionary containing database statistics.
        """
        if not self.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return {}
        
        stats = {}
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get database size
                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database())) as db_size")
                stats['database_size'] = cursor.fetchone()['db_size']
                
                # Get table counts
                cursor.execute(sql.SQL("""
                    SELECT 
                        table_name, 
                        (SELECT count(*) FROM {}.{}) as row_count
                    FROM 
                        information_schema.tables
                    WHERE 
                        table_schema = %s
                        AND table_type = 'BASE TABLE'
                """).format(
                    sql.Identifier(self.schema),
                    sql.Placeholder()
                ), (self.schema,))
                
                table_counts = {}
                for row in cursor.fetchall():
                    table_name = row['table_name']
                    cursor.execute(sql.SQL("SELECT COUNT(*) as count FROM {}.{}").format(
                        sql.Identifier(self.schema),
                        sql.Identifier(table_name)
                    ))
                    count_result = cursor.fetchone()
                    table_counts[table_name] = count_result['count'] if count_result else 0
                
                stats['table_counts'] = table_counts
                
                # Get index information
                cursor.execute(sql.SQL("""
                    SELECT
                        tablename,
                        indexname,
                        indexdef
                    FROM
                        pg_indexes
                    WHERE
                        schemaname = %s
                    ORDER BY
                        tablename,
                        indexname
                """), (self.schema,))
                
                indexes = {}
                for row in cursor.fetchall():
                    table_name = row['tablename']
                    if table_name not in indexes:
                        indexes[table_name] = []
                    indexes[table_name].append({
                        'name': row['indexname'],
                        'definition': row['indexdef']
                    })
                
                stats['indexes'] = indexes
                
                logger.info("Successfully retrieved database statistics")
                return stats
        except psycopg2.Error as e:
            logger.error(f"Error getting database statistics: {e}")
            return {'error': str(e)}