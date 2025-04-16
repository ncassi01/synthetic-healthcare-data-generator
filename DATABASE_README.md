# Database Integration System

This document provides an overview of the database integration system for the Synthetic Healthcare Data Generator project.

## Overview

The database integration system allows storing and querying the generated healthcare data across multiple specialized database systems:

- **PostgreSQL** (relational): For structured data with well-defined relationships (members, providers, claims, etc.)
- **MongoDB** (document): For semi-structured document data (clinical notes, communications, etc.)
- **Neo4j** (graph): For relationship-rich data (provider networks, care episodes, etc.)
- **Pinecone** (vector): For vector embeddings and semantic search capabilities

The system includes:

1. **Database Connectors**: Interfaces for each database type
2. **Data Synchronization**: Maintains consistency across databases
3. **Query Orchestration**: Routes queries to appropriate databases and combines results
4. **Setup and Configuration**: Scripts for database setup and configuration

## Installation

### Prerequisites

- Python 3.8 or higher
- Required Python packages (already installed):
  - psycopg2-binary (for PostgreSQL)
  - pymongo (for MongoDB)
  - neo4j (for Neo4j)
  - pinecone-client (for Pinecone)

### Database Installation

1. **Automated Installation**:
   ```bash
   # Run the automated installation script (Windows)
   install_databases.bat
   ```

2. **Manual Installation**:
   - Follow the instructions in `database_installation_guide.md`

### Configuration

1. **Automated Configuration**:
   ```bash
   # Run the configuration script
   python update_database_config.py
   ```

2. **Manual Configuration**:
   - Edit `config/database_config.json` with your database connection details

### Testing Connections

```bash
# Test all database connections
python test_database_connections.py

# Test specific database connections
python test_database_connections.py --postgresql
python test_database_connections.py --mongodb
python test_database_connections.py --neo4j
python test_database_connections.py --pinecone
```

## Usage

### Setting Up Databases and Loading Data

```bash
# Set up the database systems and load sample data
python run_databases.py --config config/database_config.json --data-dir output/processed

# Skip loading sample data (if you've already loaded it)
python run_databases.py --config config/database_config.json --skip-load

# Skip database synchronization
python run_databases.py --config config/database_config.json --skip-sync

# Skip running sample queries
python run_databases.py --config config/database_config.json --skip-queries

# Show database statistics
python run_databases.py --config config/database_config.json --stats
```

### Using the Database API in Your Code

```python
from src.databases.relational import PostgreSQLConnector
from src.databases.document import MongoDBConnector
from src.databases.graph import Neo4jConnector
from src.databases.vector import PineconeConnector
from src.databases.sync import DatabaseSynchronizer
from src.databases.query import QueryOrchestrator

# Load configuration
import json
with open('config/database_config.json', 'r') as f:
    config = json.load(f)

# Create database connectors
connectors = {
    'relational': PostgreSQLConnector(config['postgresql']),
    'document': MongoDBConnector(config['mongodb']),
    'graph': Neo4jConnector(config['neo4j']),
    'vector': PineconeConnector(config['pinecone'])
}

# Connect to databases
for db_type, connector in connectors.items():
    connector.connect()

# Create synchronizer
synchronizer = DatabaseSynchronizer(connectors, config['synchronization'])

# Synchronize data across databases
synchronizer.synchronize_all()

# Create query orchestrator
orchestrator = QueryOrchestrator(connectors, config['query_orchestration'])

# Execute a query
result = orchestrator.execute_query('member_details', {'member_id': 'MEM00000001'})

# Disconnect from databases
for db_type, connector in connectors.items():
    connector.disconnect()
```

## Available Queries

The query orchestrator supports the following predefined queries:

1. **member_details**: Get basic member information
   - Parameters: `member_id`

2. **member_conditions**: Get member's health conditions
   - Parameters: `member_id`

3. **member_medications**: Get member's medications
   - Parameters: `member_id`

4. **member_encounters**: Get member's healthcare encounters
   - Parameters: `member_id`

5. **member_claims**: Get member's insurance claims
   - Parameters: `member_id`

6. **member_authorizations**: Get member's prior authorizations
   - Parameters: `member_id`

7. **member_clinical_notes**: Get member's clinical notes
   - Parameters: `member_id`

8. **semantic_search**: Perform semantic search on clinical notes
   - Parameters: `query_text`, `top_k`

## Database Schema

### PostgreSQL (Relational)

The PostgreSQL database contains the following tables:

- **members**: Member demographic and insurance information
- **providers**: Healthcare provider information
- **encounters**: Healthcare encounters (visits, admissions, etc.)
- **conditions**: Health conditions and diagnoses
- **medications**: Medication prescriptions
- **procedures**: Medical procedures
- **claims**: Insurance claims
- **authorizations**: Prior authorization requests
- **eobs**: Explanation of Benefits documents
- **plans**: Insurance plan details

### MongoDB (Document)

The MongoDB database contains the following collections:

- **clinical_notes**: Clinical documentation
- **communications**: Patient-provider communications
- **care_plans**: Care management plans
- **authorization_rationales**: Detailed rationales for authorization decisions
- **mental_health_narratives**: Mental health assessment narratives
- **patient_generated_data**: Data generated by patients
- **provider_communications**: Provider-to-provider communications
- **telehealth_documentation**: Documentation from telehealth visits
- **insurance_communications**: Communications from insurance companies

### Neo4j (Graph)

The Neo4j database contains the following node types:

- **Member**: Member nodes
- **Provider**: Provider nodes
- **Encounter**: Encounter nodes
- **Condition**: Condition nodes
- **Medication**: Medication nodes
- **Procedure**: Procedure nodes
- **Claim**: Claim nodes
- **Authorization**: Authorization nodes
- **EOB**: EOB nodes
- **Plan**: Plan nodes
- **CareEpisode**: Care episode nodes
- **SDOHAssessment**: Social determinants of health assessment nodes
- **RiskAssessment**: Risk assessment nodes

And relationship types:

- **HAS_CONDITION**: Member has condition
- **HAS_MEDICATION**: Member has medication
- **HAS_PROCEDURE**: Member has procedure
- **HAS_ENCOUNTER**: Member has encounter
- **HAS_CLAIM**: Member has claim
- **HAS_AUTHORIZATION**: Member has authorization
- **HAS_EOB**: Member has EOB
- **HAS_PLAN**: Member has plan
- **PROVIDER_RELATIONSHIP**: Relationships between providers

### Pinecone (Vector)

The Pinecone database contains vector embeddings for:

- Clinical notes
- Patient-provider communications
- Care plans
- Mental health narratives
- Patient-generated data
- Provider communications
- Telehealth documentation
- Insurance communications

## Troubleshooting

See the `database_installation_guide.md` file for troubleshooting tips.

## Files

- `src/databases/base.py`: Base database connector interface
- `src/databases/relational.py`: PostgreSQL connector
- `src/databases/document.py`: MongoDB connector
- `src/databases/graph.py`: Neo4j connector
- `src/databases/vector.py`: Pinecone connector
- `src/databases/sync.py`: Database synchronization
- `src/databases/query.py`: Query orchestration
- `src/databases/setup_databases.py`: Database setup utilities
- `config/database_config.json`: Database configuration
- `run_databases.py`: Script to run database setup and queries
- `update_database_config.py`: Script to update database configuration
- `test_database_connections.py`: Script to test database connections
- `install_databases.bat`: Script to install databases (Windows)
- `database_installation_guide.md`: Detailed installation guide