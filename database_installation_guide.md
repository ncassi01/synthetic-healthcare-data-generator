# Database Installation and Configuration Guide

This guide provides detailed instructions for installing and configuring the database systems required for the Synthetic Healthcare Data Generator project.

## Prerequisites

Before installing the databases, ensure you have:

1. Administrative privileges on your Windows system
2. Python packages already installed (confirmed):
   - psycopg2-binary (for PostgreSQL)
   - pymongo (for MongoDB)
   - neo4j (for Neo4j)
   - pinecone-client (for Pinecone)

## 1. PostgreSQL Installation

PostgreSQL is used for storing structured relational data such as members, providers, claims, etc.

### Installation Steps

1. **Download PostgreSQL**:
   - Go to [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
   - Download the PostgreSQL installer for Windows
   - Recommended version: PostgreSQL 15.x or later

2. **Run the Installer**:
   - Launch the downloaded installer
   - Follow the installation wizard
   - When prompted, set a password for the 'postgres' user (remember this password)
   - Keep the default port (5432)
   - Complete the installation

3. **Verify Installation**:
   - Open Command Prompt or PowerShell
   - Run: `psql -U postgres -c "SELECT version();"`
   - Enter the password you set during installation
   - You should see the PostgreSQL version information

4. **Create a Database**:
   - Open Command Prompt or PowerShell
   - Run: `psql -U postgres`
   - At the PostgreSQL prompt, run: `CREATE DATABASE healthcare;`
   - Verify with: `\l` (this lists all databases)
   - Exit with: `\q`

## 2. MongoDB Installation

MongoDB is used for storing semi-structured document data such as clinical notes, communications, etc.

### Installation Steps

1. **Download MongoDB**:
   - Go to [MongoDB Community Server Downloads](https://www.mongodb.com/try/download/community)
   - Select the Windows x64 MSI package
   - Recommended version: MongoDB 6.x or later

2. **Run the Installer**:
   - Launch the downloaded installer
   - Choose "Complete" installation
   - Select "Install MongoDB as a Service" with the default settings
   - Optionally install MongoDB Compass (a GUI for MongoDB)
   - Complete the installation

3. **Verify Installation**:
   - Open Command Prompt or PowerShell
   - Run: `mongosh`
   - You should see the MongoDB shell
   - Exit with: `exit`

4. **Create a Database**:
   - Open Command Prompt or PowerShell
   - Run: `mongosh`
   - At the MongoDB shell, run: `use healthcare`
   - Exit with: `exit`

## 3. Neo4j Installation

Neo4j is used for storing graph data and relationships such as provider networks, care episodes, etc.

### Installation Steps

1. **Download Neo4j**:
   - Go to [Neo4j Desktop Download](https://neo4j.com/download/)
   - Download Neo4j Desktop for Windows
   - Recommended version: Neo4j 5.x or later

2. **Install Neo4j Desktop**:
   - Launch the downloaded installer
   - Follow the installation wizard
   - Complete the installation

3. **Create a Database**:
   - Launch Neo4j Desktop
   - Create a new project (or use the default project)
   - Click "Add Database" > "Create a Local Database"
   - Name the database "healthcare"
   - Set a password (remember this password)
   - Set the version to the latest available
   - Click "Create"

4. **Start the Database**:
   - In Neo4j Desktop, click the "Start" button for your healthcare database
   - Wait for the database to start
   - Click "Open" to launch Neo4j Browser

5. **Verify Installation**:
   - In Neo4j Browser, run: `RETURN "Neo4j is working!" AS message`
   - You should see the message displayed

## 4. Pinecone Setup

Pinecone is a cloud-based vector database used for semantic search capabilities.

### Setup Steps

1. **Create a Pinecone Account**:
   - Go to [Pinecone](https://www.pinecone.io/)
   - Sign up for a free account
   - Verify your email address

2. **Create an API Key**:
   - Log in to your Pinecone account
   - Navigate to the API Keys section
   - Create a new API key
   - Copy the API key (you'll need it for configuration)

3. **Create an Index**:
   - In the Pinecone dashboard, click "Create Index"
   - Name the index "healthcare-embeddings"
   - Set the dimension to 768 (or the dimension specified in your config)
   - Set the metric to "cosine"
   - Choose the appropriate region (e.g., "us-west1-gcp")
   - Create the index

## Updating Configuration

After installing all the databases, you need to update the `config/database_config.json` file with your connection details.

### PostgreSQL Configuration

```json
"postgresql": {
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "your_postgres_password",
  "database": "healthcare",
  "schema": "public",
  "connection_timeout": 30,
  "connection_retries": 3,
  "retry_delay": 5
}
```

### MongoDB Configuration

```json
"mongodb": {
  "host": "localhost",
  "port": 27017,
  "database": "healthcare",
  "username": "",
  "password": "",
  "auth_source": "admin",
  "connection_timeout": 30000,
  "connection_retries": 3,
  "retry_delay": 5
}
```

If you set up authentication for MongoDB, update the username and password fields.

### Neo4j Configuration

```json
"neo4j": {
  "uri": "bolt://localhost:7687",
  "username": "neo4j",
  "password": "your_neo4j_password",
  "database": "healthcare",
  "connection_timeout": 30,
  "connection_retries": 3,
  "retry_delay": 5
}
```

### Pinecone Configuration

```json
"pinecone": {
  "api_key": "your_pinecone_api_key",
  "environment": "us-west1-gcp",
  "project_name": "healthcare",
  "dimension": 768,
  "metric": "cosine",
  "pod_type": "p1.x1",
  "connection_retries": 3,
  "retry_delay": 5,
  "index_name": "healthcare-embeddings"
}
```

## Testing the Configuration

After installing and configuring all databases, you can test the configuration by running:

```bash
python run_databases.py --config config/database_config.json --skip-load --skip-sync --skip-queries
```

This will attempt to connect to all databases without loading data, synchronizing, or running queries.

If the connections are successful, you can then run the full database setup:

```bash
python run_databases.py --config config/database_config.json --data-dir output/processed
```

## Troubleshooting

### PostgreSQL Issues

- **Connection Refused**: Ensure the PostgreSQL service is running. You can check in Windows Services.
- **Authentication Failed**: Double-check the username and password in the configuration file.
- **Database Not Found**: Make sure you created the 'healthcare' database.

### MongoDB Issues

- **Connection Refused**: Ensure the MongoDB service is running. You can check in Windows Services.
- **Authentication Failed**: If you set up authentication, double-check the username and password.

### Neo4j Issues

- **Connection Refused**: Ensure the Neo4j database is started in Neo4j Desktop.
- **Authentication Failed**: Double-check the username and password in the configuration file.
- **Database Not Found**: Make sure you created the 'healthcare' database in Neo4j Desktop.

### Pinecone Issues

- **Authentication Failed**: Double-check the API key in the configuration file.
- **Index Not Found**: Make sure you created the 'healthcare-embeddings' index in the Pinecone dashboard.
- **Region Mismatch**: Ensure the environment in the configuration matches the region where you created the index.