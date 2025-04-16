@echo off
echo ===================================================
echo Synthetic Healthcare Data Generator - Database Setup
echo ===================================================
echo.
echo This script will help you install and configure the required databases:
echo 1. PostgreSQL
echo 2. MongoDB
echo 3. Neo4j
echo 4. Pinecone (cloud service, requires signup)
echo.
echo Prerequisites:
echo - Administrative privileges on your Windows system
echo - Internet connection
echo.
pause

REM Create a temporary directory for downloads
mkdir temp_downloads 2>nul
cd temp_downloads

REM Install PostgreSQL
echo.
echo ===================================================
echo Installing PostgreSQL
echo ===================================================
echo.
echo Downloading PostgreSQL installer...
curl -L -o postgresql.exe https://get.enterprisedb.com/postgresql/postgresql-15.5-1-windows-x64.exe

echo.
echo Running PostgreSQL installer...
echo Please follow the installation wizard:
echo - Set a password for the 'postgres' user
echo - Keep the default port (5432)
echo - Complete the installation
echo.
postgresql.exe
echo.
echo PostgreSQL installation completed.
echo.
pause

REM Install MongoDB
echo.
echo ===================================================
echo Installing MongoDB
echo ===================================================
echo.
echo Downloading MongoDB installer...
curl -L -o mongodb.msi https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-6.0.12-signed.msi

echo.
echo Running MongoDB installer...
echo Please follow the installation wizard:
echo - Choose "Complete" installation
echo - Select "Install MongoDB as a Service" with the default settings
echo - Complete the installation
echo.
msiexec /i mongodb.msi
echo.
echo MongoDB installation completed.
echo.
pause

REM Install Neo4j
echo.
echo ===================================================
echo Installing Neo4j
echo ===================================================
echo.
echo Downloading Neo4j Desktop installer...
curl -L -o neo4j-desktop.exe https://neo4j.com/artifact.php?name=neo4j-desktop-1.5.9-setup.exe

echo.
echo Running Neo4j Desktop installer...
echo Please follow the installation wizard:
echo - Complete the installation
echo - After installation, create a new database named 'healthcare'
echo - Set a password for the database
echo.
neo4j-desktop.exe
echo.
echo Neo4j installation completed.
echo.
pause

REM Pinecone setup instructions
echo.
echo ===================================================
echo Pinecone Setup Instructions
echo ===================================================
echo.
echo Pinecone is a cloud-based vector database service.
echo Please follow these steps to set up Pinecone:
echo.
echo 1. Go to https://www.pinecone.io/ and sign up for a free account
echo 2. Verify your email address
echo 3. Create an API key in your Pinecone dashboard
echo 4. Create an index named 'healthcare-embeddings' with:
echo    - Dimension: 768
echo    - Metric: cosine
echo    - Region: us-west1-gcp (or your preferred region)
echo.
echo After completing these steps, you'll need to update your configuration.
echo.
pause

REM Clean up
cd ..
echo.
echo Cleaning up temporary files...
rmdir /s /q temp_downloads
echo.

REM Update configuration
echo.
echo ===================================================
echo Updating Database Configuration
echo ===================================================
echo.
echo Now let's update your database configuration.
echo.
python update_database_config.py
echo.

echo ===================================================
echo Installation Complete
echo ===================================================
echo.
echo All database systems have been installed.
echo.
echo To test your database connections, run:
echo python run_databases.py --config config/database_config.json --skip-load --skip-sync --skip-queries
echo.
echo For more detailed instructions, please refer to the database_installation_guide.md file.
echo.
pause