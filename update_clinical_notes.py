"""
Script to update clinical notes data to include the provider_name field.

This script loads the existing clinical notes from the processed directory,
converts them to ClinicalNote objects, and then uses the updated to_dict() method
to regenerate the JSON data with the provider_name field.
"""

import json
import os
import logging
from datetime import datetime
from src.models.narrative import ClinicalNote, NoteType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_clinical_notes():
    """Update clinical notes to include the provider_name field."""
    # Define paths
    processed_dir = os.path.join('output', 'processed')
    raw_dir = os.path.join('output', 'raw')
    
    # Check if the processed directory exists
    if not os.path.exists(processed_dir):
        logger.error(f"Processed directory not found: {processed_dir}")
        return
    
    # Load clinical notes data
    notes_path = os.path.join(processed_dir, 'clinical_notes.json')
    if not os.path.exists(notes_path):
        logger.error(f"Clinical notes file not found: {notes_path}")
        return
    
    try:
        with open(notes_path, 'r') as f:
            notes_data = json.load(f)
        
        logger.info(f"Loaded {len(notes_data)} clinical notes")
        
        # Convert JSON data to ClinicalNote objects and then back to updated JSON
        updated_notes = []
        for note in notes_data:
            # Create a ClinicalNote object from the JSON data
            clinical_note = ClinicalNote(
                id=note.get("id", ""),
                member_id=note.get("member_id", ""),
                provider_id=note.get("provider_id", ""),
                note_type=note.get("note_type", ""),
                date_of_service=datetime.fromisoformat(note.get("date_of_service", "").replace("Z", "+00:00")),
                chief_complaint=note.get("chief_complaint", ""),
                subjective=note.get("subjective", ""),
                objective=note.get("objective", ""),
                assessment=note.get("assessment", ""),
                plan=note.get("plan", ""),
                diagnosis_codes=note.get("diagnosis_codes", []),
                procedure_codes=note.get("procedure_codes", []),
                medication_references=note.get("medication_references", [])
            )
            
            # Convert back to dictionary using the updated to_dict() method
            updated_note = clinical_note.to_dict()
            updated_notes.append(updated_note)
        
        logger.info(f"Updated {len(updated_notes)} clinical notes")
        
        # Save updated data
        with open(notes_path, 'w') as f:
            json.dump(updated_notes, f, indent=2)
        
        logger.info(f"Saved updated clinical notes to {notes_path}")
        
        # Also update the raw data if it exists
        raw_notes_path = os.path.join(raw_dir, 'clinical_notes.json')
        if os.path.exists(raw_notes_path):
            with open(raw_notes_path, 'w') as f:
                json.dump(updated_notes, f, indent=2)
            logger.info(f"Saved updated clinical notes to {raw_notes_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating clinical notes: {e}")
        return False

if __name__ == "__main__":
    update_clinical_notes()