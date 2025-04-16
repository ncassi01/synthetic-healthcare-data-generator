"""
Clinical Domain Database Module

This module provides functionality for creating and managing the Clinical domain
database schema and operations. It extends the relational database connector
to add Clinical domain-specific tables and operations.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from psycopg2 import sql

from .relational import PostgreSQLConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalDBManager:
    """
    Clinical Domain Database Manager.
    
    This class provides methods to create and manage the Clinical domain database schema
    and perform operations on Clinical domain data.
    """
    
    def __init__(self, db_connector: PostgreSQLConnector):
        """
        Initialize the Clinical Domain Database Manager.
        
        Args:
            db_connector: A PostgreSQL database connector instance.
        """
        self.db = db_connector
        self.schema = db_connector.schema
    
    def create_clinical_schema(self) -> bool:
        """
        Create the Clinical domain database schema (tables, indexes, etc.).
        
        Returns:
            bool: True if schema creation was successful, False otherwise.
        """
        if not self.db.is_connected:
            logger.error("Not connected to database. Call connect() first.")
            return False
        
        try:
            with self.db.connection.cursor() as cursor:
                # Create Clinical domain tables
                self._create_clinical_encounters_table(cursor)
                self._create_encounter_participants_table(cursor)
                self._create_encounter_locations_table(cursor)
                self._create_encounter_diagnoses_table(cursor)
                self._create_encounter_procedures_table(cursor)
                self._create_clinical_notes_table(cursor)
                self._create_encounter_services_table(cursor)
                self._create_encounter_assessments_table(cursor)
                self._create_encounter_medications_table(cursor)
                self._create_encounter_transitions_table(cursor)
                
                self.db.connection.commit()
                logger.info("Successfully created Clinical domain database schema")
                return True
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Error creating Clinical domain schema: {e}")
            return False
    
    def _create_clinical_encounters_table(self, cursor):
        """Create the clinical_encounters table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.clinical_encounters (
                id VARCHAR(50) PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                class_type VARCHAR(50) NOT NULL,
                priority VARCHAR(50),
                start_datetime TIMESTAMP NOT NULL,
                end_datetime TIMESTAMP,
                length_of_stay INTEGER,
                admission_type VARCHAR(50),
                discharge_disposition VARCHAR(50),
                readmission BOOLEAN DEFAULT FALSE,
                chief_complaint TEXT,
                reason_code VARCHAR(50),
                service_type VARCHAR(50),
                account_number VARCHAR(50),
                visit_number VARCHAR(50),
                episode_of_care_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(sql.Identifier(self.schema)))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_encounters_type ON {}.clinical_encounters (type)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_encounters_status ON {}.clinical_encounters (status)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_encounters_start_datetime ON {}.clinical_encounters (start_datetime)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_participants_table(self, cursor):
        """Create the encounter_participants table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_participants (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                participant_type VARCHAR(50) NOT NULL,
                participant_id VARCHAR(50) NOT NULL,
                role VARCHAR(50),
                start_datetime TIMESTAMP,
                end_datetime TIMESTAMP,
                primary_participant BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_participants_encounter_id ON {}.encounter_participants (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_participants_participant_id ON {}.encounter_participants (participant_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_participants_type ON {}.encounter_participants (participant_type)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_locations_table(self, cursor):
        """Create the encounter_locations table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_locations (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                facility_id VARCHAR(50),
                department_id VARCHAR(50),
                location_type VARCHAR(50) NOT NULL,
                start_datetime TIMESTAMP,
                end_datetime TIMESTAMP,
                status VARCHAR(50) NOT NULL,
                bed_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_locations_encounter_id ON {}.encounter_locations (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_locations_facility_id ON {}.encounter_locations (facility_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_locations_type ON {}.encounter_locations (location_type)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_diagnoses_table(self, cursor):
        """Create the encounter_diagnoses table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_diagnoses (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                diagnosis_code VARCHAR(50) NOT NULL,
                diagnosis_description TEXT NOT NULL,
                condition_id VARCHAR(50),
                diagnosis_type VARCHAR(50) NOT NULL,
                present_on_admission BOOLEAN DEFAULT FALSE,
                rank INTEGER,
                provider_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_diagnoses_encounter_id ON {}.encounter_diagnoses (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_diagnoses_code ON {}.encounter_diagnoses (diagnosis_code)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_diagnoses_type ON {}.encounter_diagnoses (diagnosis_type)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_procedures_table(self, cursor):
        """Create the encounter_procedures table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_procedures (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                procedure_code VARCHAR(50) NOT NULL,
                procedure_description TEXT NOT NULL,
                procedure_id VARCHAR(50),
                datetime TIMESTAMP,
                duration_minutes INTEGER,
                provider_id VARCHAR(50),
                location_id VARCHAR(50),
                status VARCHAR(50) NOT NULL,
                primary_procedure BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_procedures_encounter_id ON {}.encounter_procedures (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_procedures_code ON {}.encounter_procedures (procedure_code)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_procedures_datetime ON {}.encounter_procedures (datetime)
        """).format(sql.Identifier(self.schema)))
    
    def _create_clinical_notes_table(self, cursor):
        """Create the clinical_notes table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.clinical_notes (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                note_type VARCHAR(50) NOT NULL,
                author_id VARCHAR(50) NOT NULL,
                datetime TIMESTAMP NOT NULL,
                content TEXT NOT NULL,
                status VARCHAR(50) NOT NULL,
                signed BOOLEAN DEFAULT FALSE,
                signed_datetime TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_notes_encounter_id ON {}.clinical_notes (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_notes_author_id ON {}.clinical_notes (author_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_notes_type ON {}.clinical_notes (note_type)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_clinical_notes_datetime ON {}.clinical_notes (datetime)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_services_table(self, cursor):
        """Create the encounter_services table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_services (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                service_code VARCHAR(50) NOT NULL,
                service_description TEXT NOT NULL,
                service_id VARCHAR(50),
                provider_id VARCHAR(50),
                datetime TIMESTAMP,
                quantity INTEGER DEFAULT 1,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_services_encounter_id ON {}.encounter_services (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_services_code ON {}.encounter_services (service_code)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_services_datetime ON {}.encounter_services (datetime)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_assessments_table(self, cursor):
        """Create the encounter_assessments table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_assessments (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                assessment_type VARCHAR(50) NOT NULL,
                datetime TIMESTAMP NOT NULL,
                provider_id VARCHAR(50),
                result JSONB NOT NULL,
                interpretation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_assessments_encounter_id ON {}.encounter_assessments (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_assessments_type ON {}.encounter_assessments (assessment_type)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_assessments_datetime ON {}.encounter_assessments (datetime)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_medications_table(self, cursor):
        """Create the encounter_medications table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_medications (
                id VARCHAR(50) PRIMARY KEY,
                encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                medication_id VARCHAR(50) NOT NULL,
                order_id VARCHAR(50),
                datetime TIMESTAMP,
                dose VARCHAR(100),
                route VARCHAR(50) NOT NULL,
                provider_id VARCHAR(50),
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """).format(
            sql.Identifier(self.schema),
            sql.Identifier(self.schema)
        ))
        
        # Create indexes
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_medications_encounter_id ON {}.encounter_medications (encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_medications_medication_id ON {}.encounter_medications (medication_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_medications_datetime ON {}.encounter_medications (datetime)
        """).format(sql.Identifier(self.schema)))
    
    def _create_encounter_transitions_table(self, cursor):
        """Create the encounter_transitions table."""
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.encounter_transitions (
                id VARCHAR(50) PRIMARY KEY,
                from_encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                to_encounter_id VARCHAR(50) NOT NULL REFERENCES {}.clinical_encounters(id),
                transition_type VARCHAR(50) NOT NULL,
                datetime TIMESTAMP NOT NULL,
                reason TEXT,
                authorizing_provider_id VARCHAR(50),
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
            CREATE INDEX IF NOT EXISTS idx_encounter_transitions_from_encounter_id ON {}.encounter_transitions (from_encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_transitions_to_encounter_id ON {}.encounter_transitions (to_encounter_id)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_transitions_type ON {}.encounter_transitions (transition_type)
        """).format(sql.Identifier(self.schema)))
        
        cursor.execute(sql.SQL("""
            CREATE INDEX IF NOT EXISTS idx_encounter_transitions_datetime ON {}.encounter_transitions (datetime)
        """).format(sql.Identifier(self.schema)))
    
    def insert_clinical_encounter(self, encounter: Dict[str, Any]) -> bool:
        """
        Insert a clinical encounter into the database.
        
        Args:
            encounter: Dictionary containing the clinical encounter data.
            
        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        try:
            # Insert the main encounter
            self.db.insert_data(encounter, "clinical_encounters")
            
            # Insert related entities if present
            if "participants" in encounter and encounter["participants"]:
                self.db.insert_data(encounter["participants"], "encounter_participants")
            
            if "locations" in encounter and encounter["locations"]:
                self.db.insert_data(encounter["locations"], "encounter_locations")
            
            if "diagnoses" in encounter and encounter["diagnoses"]:
                self.db.insert_data(encounter["diagnoses"], "encounter_diagnoses")
            
            if "procedures" in encounter and encounter["procedures"]:
                self.db.insert_data(encounter["procedures"], "encounter_procedures")
            
            if "notes" in encounter and encounter["notes"]:
                self.db.insert_data(encounter["notes"], "clinical_notes")
            
            if "services" in encounter and encounter["services"]:
                self.db.insert_data(encounter["services"], "encounter_services")
            
            if "assessments" in encounter and encounter["assessments"]:
                self.db.insert_data(encounter["assessments"], "encounter_assessments")
            
            if "medications" in encounter and encounter["medications"]:
                self.db.insert_data(encounter["medications"], "encounter_medications")
            
            return True
        except Exception as e:
            logger.error(f"Error inserting clinical encounter: {e}")
            return False
    
    def get_clinical_encounter(self, encounter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a clinical encounter by ID.
        
        Args:
            encounter_id: ID of the clinical encounter to retrieve.
            
        Returns:
            Dictionary containing the clinical encounter data, or None if not found.
        """
        try:
            # Get the main encounter
            encounters = self.db.query(f"id = '{encounter_id}'", "clinical_encounters")
            if not encounters:
                return None
            
            encounter = encounters[0]
            
            # Get related entities
            encounter["participants"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_participants")
            encounter["locations"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_locations")
            encounter["diagnoses"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_diagnoses")
            encounter["procedures"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_procedures")
            encounter["notes"] = self.db.query(f"encounter_id = '{encounter_id}'", "clinical_notes")
            encounter["services"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_services")
            encounter["assessments"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_assessments")
            encounter["medications"] = self.db.query(f"encounter_id = '{encounter_id}'", "encounter_medications")
            
            return encounter
        except Exception as e:
            logger.error(f"Error retrieving clinical encounter: {e}")
            return None
    
    def get_patient_encounters(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all clinical encounters for a patient.
        
        Args:
            patient_id: ID of the patient.
            
        Returns:
            List of dictionaries containing the clinical encounter data.
        """
        try:
            # Find all encounters where the patient is a participant
            participant_records = self.db.query(
                f"participant_id = '{patient_id}' AND participant_type = 'Patient'", 
                "encounter_participants"
            )
            
            if not participant_records:
                return []
            
            encounter_ids = [p["encounter_id"] for p in participant_records]
            encounters = []
            
            for encounter_id in encounter_ids:
                encounter = self.get_clinical_encounter(encounter_id)
                if encounter:
                    encounters.append(encounter)
            
            return encounters
        except Exception as e:
            logger.error(f"Error retrieving patient encounters: {e}")
            return []