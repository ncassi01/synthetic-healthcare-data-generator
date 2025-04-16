# Synthetic Healthcare Data Generator

A Python-based synthetic healthcare data generator for RAG testing and development purposes.

## Project Overview

This project aims to generate realistic, interconnected healthcare data for testing and development purposes. The initial focus is on the member domain, with plans to expand to other healthcare domains in the future.

## Key Features

* Generate synthetic member data with realistic attributes
* Generate insurance-related data (claims, prior authorizations, EOBs, plan coverage)
* Generate realistic healthcare data using custom Python libraries
* Generate narrative content (clinical notes, communications, care plans) for RAG testing
* Generate diverse unstructured data types (patient-generated content, provider communications, etc.)
* Support both structured and unstructured data for comprehensive RAG testing
* Support multi-database storage for different data types and query patterns
* Include enhanced healthcare entities (care episodes, SDOH, risk assessments, etc.)
* Model realistic clinical decision pathways and authorization flows
* Output data in JSON format (initially)
* Support for future integration with various database types
* Configurable data generation parameters
* Realistic data distributions and relationships
* Web-based frontend for data visualization and exploration

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Navigate to the project directory
cd synthetic-healthcare-data

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
# Generate 100 members (default)
python src/main.py

# Generate a specific number of members
python src/main.py --count 500

# Generate members with a specific random seed
python src/main.py --seed 12345

# Generate members and validate the data
python src/main.py --validate

# Generate members and produce statistics
python src/main.py --stats
```

### Data Processing

```bash
# Generate and process members (adds risk scores, care gaps, etc.)
python src/main.py --process

# Generate, process, and skip saving raw data
python src/main.py --process --skip-raw

# Generate, process, and produce statistics on the processed data
python src/main.py --process --stats
```

### Database Integration

The project includes a multi-database architecture that leverages the strengths of different database types:

- **PostgreSQL** for structured relational data (members, providers, claims, etc.)
- **MongoDB** for semi-structured document data (clinical notes, communications, etc.)
- **Neo4j** for graph data and relationships (provider networks, care episodes, etc.)
- **Pinecone** for vector embeddings and semantic search

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

Before running the database integration, make sure you have the required database systems installed and configured:

1. **PostgreSQL**: Install PostgreSQL and create a database
2. **MongoDB**: Install MongoDB and start the MongoDB service
3. **Neo4j**: Install Neo4j and create a database
4. **Pinecone**: Sign up for a Pinecone account and get an API key

Update the `config/database_config.json` file with your database connection details.

### Web Frontend

The project includes a web-based frontend for visualizing and exploring the generated data.

```bash
# First, generate data with the data generation pipeline
python src/main.py --process --stats

# Then, run the web application
python web/app.py

# Open your browser and navigate to http://localhost:5000
```

The web frontend provides:
- Dashboard with summary statistics and visualizations
- Member data explorer with detailed views
- Claims, authorizations, and other insurance data views
- Clinical notes and care plans viewer
- Communication records explorer
- Interactive data tables and charts

For more details, see the [Web Frontend README](web/README.md).

### Python API

```python
from src.generators.member_generator import MemberGenerator
from src.processors.member_processor import MemberProcessor
from src.utils.validation_utils import validate_dataset, check_data_distribution

# Load configuration
config = {...}  # Your configuration dictionary

# Generate members
generator = MemberGenerator(config)
members = generator.generate(100)

# Process and enrich members
processor = MemberProcessor(config)
processed_members = processor.process(members)

# Validate members
validation_results = validate_dataset(processed_members)

# Check data distribution
distributions = check_data_distribution(processed_members)
```

### Database API

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

## Project Structure

```
synthetic-healthcare-data/
├── README.md
├── setup.py
├── requirements.txt
├── src/
│   ├── processors/           # Data processors
│   ├── generators/           # Supplemental data generators
│   ├── models/               # Data models
│   ├── utils/                # Utility functions
│   ├── databases/            # Database connectors and utilities
│   │   ├── base.py           # Base database connector
│   │   ├── relational.py     # PostgreSQL connector
│   │   ├── document.py       # MongoDB connector
│   │   ├── graph.py          # Neo4j connector
│   │   ├── vector.py         # Pinecone connector
│   │   ├── sync.py           # Database synchronization
│   │   ├── query.py          # Query orchestration
│   │   └── setup_databases.py # Database setup utilities
│   └── main.py               # Main entry point
├── web/                      # Web frontend
│   ├── app.py                # Flask application
│   ├── templates/            # HTML templates
│   ├── static/               # Static assets (CSS, JS, images)
│   └── README.md             # Web frontend documentation
├── config/                   # Configuration files
│   ├── config.json           # Main configuration
│   └── database_config.json  # Database configuration
├── tests/                    # Test files
└── output/                   # Generated data output
    ├── raw/                  # Raw generated data
    └── processed/            # Processed data for RAG
```

## Development

### Phase 1: Setup and Initial Data Generation ✓
- Set up Python environment and dependencies
- Develop initial data generation modules
- Generate a small test dataset (100 patients)
- Design Python processing pipeline architecture

### Phase 2: Core Data Processing ✓
- Develop member data processing modules
- Transform and enrich member data
- Add risk scores and care gaps
- Implement enhanced JSON output for member data
- Validate member data quality and completeness

### Phase 3: Insurance Data Generation ✓
- Create comprehensive insurance data models
- Implement generators for insurance-related data
- Ensure proper relationships between clinical and insurance data
- Implement insurance data processor for enrichment and validation

### Phase 4: Narrative Content Generation ✓
- Create narrative content data models
- Implement generators for narrative content
- Ensure proper relationships between narrative and structured data
- Implement narrative content processor for enrichment and validation

### Phase 5: Web Frontend ✓
- Create web-based frontend for data visualization
- Implement interactive data tables and charts
- Provide detailed views for all data types
- Enable exploration of relationships between data entities

### Phase 6: Expanded Unstructured Data ✓
- Implement patient-generated health data generator
- Develop provider-to-provider communications generator
- Create insurance communications generator
- Build mental health narratives generator
- Implement telehealth documentation generator
- Add remaining unstructured data generators as needed

### Phase 7: Enhanced Data Model ✓
- Implement care episodes generator
- Develop SDOH assessment generator
- Create risk assessment generator
- Build provider network and relationship generator
- Implement pharmacy benefit and claims generator
- Develop authorization rules engine
- Create comprehensive data consistency validators

### Phase 8: Database Integration ✓
- Set up and configure multiple database systems
- Implement data loading pipelines for each database
- Create cross-database references and synchronization
- Develop query orchestration layer
- Implement caching and performance optimizations

### Future Phases
- RAG Testing Support
- Scaling and Optimization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.