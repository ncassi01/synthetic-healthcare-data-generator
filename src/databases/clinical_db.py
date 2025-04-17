"""
Clinical Database Module

This module provides functionality for interacting with the clinical domain database tables.
It includes methods for creating, reading, updating, and deleting clinical encounter data.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from src.databases.base_db import BaseDatabase
from src.utils.id_generator import generate_id

logger = logging.getLogger(__name__)

class ClinicalDatabase(BaseDatabase):
    """Database connector for clinical domain data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the clinical database connector.
        
        Args:
            config: Database configuration dictionary
        """
        super().__init__(config)
        self.schema_file = os.path.join(os.path.dirname(__file__), 'clinical_db_schema.sql')
        
    def initialize(self) -> bool:
        """Initialize the clinical database tables.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Read and execute the schema file
            with open(self.schema_file, 'r') as f:
                schema_sql = f.read()
                
            # Execute the schema SQL
            self.execute_query(schema_sql)
            logger.info("Clinical database tables initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing clinical database tables: {e}")
            return False
    
    def create_encounter(self, encounter_data: Dict[str, Any]) -> str:
        """Create a new clinical encounter.
        
        Args:
            encounter_data: Dictionary containing encounter data
            
        Returns:
            str: ID of the created encounter
        """
        try:
            # Generate ID if not provided
            if 'id' not in encounter_data:
                encounter_data['id'] = generate_id('ENC')
                
            # Prepare data for insertion
            columns = ', '.join(encounter_data.keys())
            placeholders = ', '.join(['%s'] * len(encounter_data))
            values = list(encounter_data.values())
            
            # Insert the encounter
            query = f"INSERT INTO clinical_encounters ({columns}) VALUES ({placeholders})"
            self.execute_query(query, values)
            
            logger.info(f"Created clinical encounter with ID: {encounter_data['id']}")
            return encounter_data['id']
        except Exception as e:
            logger.error(f"Error creating clinical encounter: {e}")
            raise
    
    def get_encounter(self, encounter_id: str) -> Optional[Dict[str, Any]]:
        """Get a clinical encounter by ID.
        
        Args:
            encounter_id: ID of the encounter to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Encounter data or None if not found
        """
        try:
            # Get the encounter
            query = "SELECT * FROM clinical_encounters WHERE id = %s"
            result = self.execute_query(query, [encounter_id], fetch=True)
            
            if not result:
                logger.warning(f"Clinical encounter not found: {encounter_id}")
                return None
                
            encounter = result[0]
            
            # Get related data
            encounter['participants'] = self.get_encounter_participants(encounter_id)
            encounter['locations'] = self.get_encounter_locations(encounter_id)
            encounter['diagnoses'] = self.get_encounter_diagnoses(encounter_id)
            encounter['procedures'] = self.get_encounter_procedures(encounter_id)
            encounter['services'] = self.get_encounter_services(encounter_id)
            encounter['assessments'] = self.get_encounter_assessments(encounter_id)
            encounter['medications'] = self.get_encounter_medications(encounter_id)
            
            # Get clinical notes for this encounter
            query = "SELECT * FROM clinical_notes WHERE encounter_id = %s"
            notes = self.execute_query(query, [encounter_id], fetch=True)
            encounter['clinical_notes'] = notes if notes else []
            
            return encounter
        except Exception as e:
            logger.error(f"Error getting clinical encounter: {e}")
            return None
    
    def get_member_encounters(self, member_id: str) -> List[Dict[str, Any]]:
        """Get all clinical encounters for a member.
        
        Args:
            member_id: ID of the member
            
        Returns:
            List[Dict[str, Any]]: List of encounter data
        """
        try:
            # Get the encounters
            query = "SELECT * FROM clinical_encounters WHERE member_id = %s ORDER BY start_datetime DESC"
            results = self.execute_query(query, [member_id], fetch=True)
            
            if not results:
                logger.info(f"No clinical encounters found for member: {member_id}")
                return []
                
            encounters = []
            for encounter in results:
                # Get related data
                encounter['participants'] = self.get_encounter_participants(encounter['id'])
                encounter['locations'] = self.get_encounter_locations(encounter['id'])
                encounter['diagnoses'] = self.get_encounter_diagnoses(encounter['id'])
                encounter['procedures'] = self.get_encounter_procedures(encounter['id'])
                encounters.append(encounter)
                
            return encounters
        except Exception as e:
            logger.error(f"Error getting member clinical encounters: {e}")
            return []
    
    def update_encounter(self, encounter_id: str, encounter_data: Dict[str, Any]) -> bool:
        """Update a clinical encounter.
        
        Args:
            encounter_id: ID of the encounter to update
            encounter_data: Dictionary containing updated encounter data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Remove ID from update data if present
            if 'id' in encounter_data:
                del encounter_data['id']
                
            if not encounter_data:
                logger.warning("No data provided for encounter update")
                return False
                
            # Prepare data for update
            set_clause = ', '.join([f"{key} = %s" for key in encounter_data.keys()])
            values = list(encounter_data.values()) + [encounter_id]
            
            # Update the encounter
            query = f"UPDATE clinical_encounters SET {set_clause} WHERE id = %s"
            self.execute_query(query, values)
            
            logger.info(f"Updated clinical encounter: {encounter_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating clinical encounter: {e}")
            return False
    
    def delete_encounter(self, encounter_id: str) -> bool:
        """Delete a clinical encounter and all related data.
        
        Args:
            encounter_id: ID of the encounter to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Delete related data first
            self.execute_query("DELETE FROM encounter_participants WHERE encounter_id = %s", [encounter_id])
            self.execute_query("DELETE FROM encounter_locations WHERE encounter_id = %s", [encounter_id])
            self.execute_query("DELETE FROM encounter_diagnoses WHERE encounter_id = %s", [encounter_id])
            self.execute_query("DELETE FROM encounter_procedures WHERE encounter_id = %s", [encounter_id])
            self.execute_query("DELETE FROM encounter_services WHERE encounter_id = %s", [encounter_id])
            self.execute_query("DELETE FROM encounter_assessments WHERE encounter_id = %s", [encounter_id])
            self.execute_query("DELETE FROM encounter_medications WHERE encounter_id = %s", [encounter_id])
            
            # Update clinical notes to remove encounter reference
            self.execute_query("UPDATE clinical_notes SET encounter_id = NULL WHERE encounter_id = %s", [encounter_id])
            
            # Delete transitions
            self.execute_query("DELETE FROM encounter_transitions WHERE from_encounter_id = %s OR to_encounter_id = %s", 
                              [encounter_id, encounter_id])
            
            # Delete the encounter
            self.execute_query("DELETE FROM clinical_encounters WHERE id = %s", [encounter_id])
            
            logger.info(f"Deleted clinical encounter: {encounter_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting clinical encounter: {e}")
            return False
    
    # Helper methods for related entities
    
    def get_encounter_participants(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get participants for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of participant data
        """
        query = "SELECT * FROM encounter_participants WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    def get_encounter_locations(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get locations for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of location data
        """
        query = "SELECT * FROM encounter_locations WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    def get_encounter_diagnoses(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get diagnoses for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of diagnosis data
        """
        query = "SELECT * FROM encounter_diagnoses WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    def get_encounter_procedures(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get procedures for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of procedure data
        """
        query = "SELECT * FROM encounter_procedures WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    def get_encounter_services(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get services for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of service data
        """
        query = "SELECT * FROM encounter_services WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    def get_encounter_assessments(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get assessments for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of assessment data
        """
        query = "SELECT * FROM encounter_assessments WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    def get_encounter_medications(self, encounter_id: str) -> List[Dict[str, Any]]:
        """Get medications for an encounter.
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List[Dict[str, Any]]: List of medication data
        """
        query = "SELECT * FROM encounter_medications WHERE encounter_id = %s"
        results = self.execute_query(query, [encounter_id], fetch=True)
        return results if results else []
    
    # Methods for adding related entities
    
    def add_encounter_participant(self, participant_data: Dict[str, Any]) -> str:
        """Add a participant to an encounter.
        
        Args:
            participant_data: Dictionary containing participant data
            
        Returns:
            str: ID of the created participant
        """
        try:
            # Generate ID if not provided
            if 'id' not in participant_data:
                participant_data['id'] = generate_id('PART')
                
            # Prepare data for insertion
            columns = ', '.join(participant_data.keys())
            placeholders = ', '.join(['%s'] * len(participant_data))
            values = list(participant_data.values())
            
            # Insert the participant
            query = f"INSERT INTO encounter_participants ({columns}) VALUES ({placeholders})"
            self.execute_query(query, values)
            
            logger.info(f"Added participant to encounter: {participant_data['encounter_id']}")
            return participant_data['id']
        except Exception as e:
            logger.error(f"Error adding encounter participant: {e}")
            raise
    
    def add_encounter_location(self, location_data: Dict[str, Any]) -> str:
        """Add a location to an encounter.
        
        Args:
            location_data: Dictionary containing location data
            
        Returns:
            str: ID of the created location
        """
        try:
            # Generate ID if not provided
            if 'id' not in location_data:
                location_data['id'] = generate_id('LOC')
                
            # Prepare data for insertion
            columns = ', '.join(location_data.keys())
            placeholders = ', '.join(['%s'] * len(location_data))
            values = list(location_data.values())
            
            # Insert the location
            query = f"INSERT INTO encounter_locations ({columns}) VALUES ({placeholders})"
            self.execute_query(query, values)
            
            logger.info(f"Added location to encounter: {location_data['encounter_id']}")
            return location_data['id']
        except Exception as e:
            logger.error(f"Error adding encounter location: {e}")
            raise
    
    def add_encounter_diagnosis(self, diagnosis_data: Dict[str, Any]) -> str:
        """Add a diagnosis to an encounter.
        
        Args:
            diagnosis_data: Dictionary containing diagnosis data
            
        Returns:
            str: ID of the created diagnosis
        """
        try:
            # Generate ID if not provided
            if 'id' not in diagnosis_data:
                diagnosis_data['id'] = generate_id('DIAG')
                
            # Prepare data for insertion
            columns = ', '.join(diagnosis_data.keys())
            placeholders = ', '.join(['%s'] * len(diagnosis_data))
            values = list(diagnosis_data.values())
            
            # Insert the diagnosis
            query = f"INSERT INTO encounter_diagnoses ({columns}) VALUES ({placeholders})"
            self.execute_query(query, values)
            
            logger.info(f"Added diagnosis to encounter: {diagnosis_data['encounter_id']}")
            return diagnosis_data['id']
        except Exception as e:
            logger.error(f"Error adding encounter diagnosis: {e}")
            raise
    
    def add_encounter_procedure(self, procedure_data: Dict[str, Any]) -> str:
        """Add a procedure to an encounter.
        
        Args:
            procedure_data: Dictionary containing procedure data
            
        Returns:
            str: ID of the created procedure
        """
        try:
            # Generate ID if not provided
            if 'id' not in procedure_data:
                procedure_data['id'] = generate_id('PROC')
                
            # Prepare data for insertion
            columns = ', '.join(procedure_data.keys())
            placeholders = ', '.join(['%s'] * len(procedure_data))
            values = list(procedure_data.values())
            
            # Insert the procedure
            query = f"INSERT INTO encounter_procedures ({columns}) VALUES ({placeholders})"
            self.execute_query(query, values)
            
            logger.info(f"Added procedure to encounter: {procedure_data['encounter_id']}")
            return procedure_data['id']
        except Exception as e:
            logger.error(f"Error adding encounter procedure: {e}")
            raise