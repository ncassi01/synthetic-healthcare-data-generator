"""
Test script for the Clinical Domain Validation Framework.

This script demonstrates the use of the ClinicalValidator class to validate
clinical encounters and related entities.
"""

import os
import sys
import json
from datetime import datetime, timedelta
import logging

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.clinical_validator import ClinicalValidator
from src.models.clinical import (
    ClinicalEncounter, EncounterParticipant, EncounterLocation,
    EncounterDiagnosis, EncounterProcedure, ClinicalNote,
    EncounterType, EncounterStatus, EncounterClass, EncounterPriority,
    ParticipantType, ProviderRole, LocationType, LocationStatus,
    DiagnosisType, ProcedureStatus, NoteType, NoteStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_encounter(valid: bool = True) -> ClinicalEncounter:
    """
    Create a sample clinical encounter for testing.
    
    Args:
        valid: Whether to create a valid encounter (True) or one with validation issues (False).
        
    Returns:
        A sample clinical encounter.
    """
    # Create base encounter
    now = datetime.now()
    encounter = ClinicalEncounter(
        id="ENC123456",
        type=EncounterType.INPATIENT,
        status=EncounterStatus.FINISHED,
        class_type=EncounterClass.INPATIENT,
        priority=EncounterPriority.ROUTINE,
        start_datetime=now - timedelta(days=3),
        end_datetime=now if valid else None,  # Missing end date for invalid case
        length_of_stay=3 if valid else 0,  # Invalid length of stay for invalid case
        admission_type="Elective",
        discharge_disposition="Home" if valid else None,  # Missing discharge disposition for invalid case
        readmission=False,
        chief_complaint="Chest pain and shortness of breath",
        reason_code="R07.9",
        service_type="Medical",
        account_number="ACC987654",
        visit_number="VN123456",
        episode_of_care_id="EP1A2B3C4D"
    )
    
    # Add participants
    patient = EncounterParticipant(
        id="PART123",
        encounter_id=encounter.id,
        participant_type=ParticipantType.PATIENT,
        participant_id="MEM00000042",
        role=None,
        start_datetime=encounter.start_datetime,
        end_datetime=encounter.end_datetime,
        primary=True
    )
    
    provider = EncounterParticipant(
        id="PART124",
        encounter_id=encounter.id,
        participant_type=ParticipantType.PROVIDER,
        participant_id="PRV00000078",
        role=ProviderRole.ATTENDING,
        start_datetime=encounter.start_datetime,
        end_datetime=encounter.end_datetime,
        primary=True
    )
    
    encounter.participants = [patient, provider]
    
    # Add location
    location = EncounterLocation(
        id="LOC123",
        encounter_id=encounter.id,
        facility_id="FAC001",
        department_id="DEP005",
        location_type=LocationType.WARD,
        bed_id="BED123" if valid else None,  # Missing bed ID for invalid case
        start_datetime=encounter.start_datetime,
        end_datetime=encounter.end_datetime,
        status=LocationStatus.COMPLETED
    )
    
    encounter.locations = [location]
    
    # Add diagnosis
    diagnosis = EncounterDiagnosis(
        id="DIAG123",
        encounter_id=encounter.id,
        condition_id="COND456",
        diagnosis_code="J18.9" if valid else "INVALID",  # Invalid code for invalid case
        diagnosis_description="Pneumonia, unspecified",
        diagnosis_type=DiagnosisType.PRINCIPAL,
        present_on_admission=True if valid else None,  # Missing POA flag for invalid case
        rank=1,
        provider_id="PRV00000078"
    )
    
    encounter.diagnoses = [diagnosis]
    
    # Add procedure
    procedure = EncounterProcedure(
        id="PROC123",
        encounter_id=encounter.id,
        procedure_id="PROC456",
        procedure_code="71045" if valid else "INVALID",  # Invalid code for invalid case
        procedure_description="X-ray, chest, single view",
        datetime=encounter.start_datetime + timedelta(hours=4),
        duration_minutes=15,
        provider_id="PRV00000079",
        location_id="LOC123",
        status=ProcedureStatus.COMPLETED,
        primary=False
    )
    
    encounter.procedures = [procedure]
    
    # Add note
    note = ClinicalNote(
        id="NOTE123",
        encounter_id=encounter.id,
        note_type=NoteType.H_AND_P,
        author_id="PRV00000078",
        datetime=encounter.start_datetime + timedelta(hours=1),
        content="Patient is a 65-year-old male presenting with chest pain and shortness of breath..." if valid else "",  # Empty content for invalid case
        status=NoteStatus.FINAL,
        signed=True,
        signed_datetime=encounter.start_datetime + timedelta(hours=2)
    )
    
    # Add discharge summary for valid case
    if valid:
        discharge_summary = ClinicalNote(
            id="NOTE124",
            encounter_id=encounter.id,
            note_type=NoteType.DISCHARGE_SUMMARY,
            author_id="PRV00000078",
            datetime=encounter.end_datetime - timedelta(hours=1),
            content="Patient was admitted for pneumonia and has completed a course of antibiotics...",
            status=NoteStatus.FINAL,
            signed=True,
            signed_datetime=encounter.end_datetime - timedelta(minutes=30)
        )
        encounter.notes = [note, discharge_summary]
    else:
        encounter.notes = [note]  # Missing discharge summary for invalid case
    
    return encounter


def test_validator():
    """Test the clinical validator with sample encounters."""
    # Create validator
    validator = ClinicalValidator()
    
    # Test with valid encounter
    logger.info("Testing with valid encounter...")
    valid_encounter = create_sample_encounter(valid=True)
    valid_results = validator.validate_encounter(valid_encounter)
    
    if valid_results:
        logger.warning(f"Found {len(valid_results)} validation issues in valid encounter:")
        for result in valid_results:
            logger.warning(f"  {result.code}: {result.message} ({result.severity.value})")
    else:
        logger.info("No validation issues found in valid encounter.")
    
    # Reset validator
    validator = ClinicalValidator()
    
    # Test with invalid encounter
    logger.info("\nTesting with invalid encounter...")
    invalid_encounter = create_sample_encounter(valid=False)
    invalid_results = validator.validate_encounter(invalid_encounter)
    
    if invalid_results:
        logger.warning(f"Found {len(invalid_results)} validation issues in invalid encounter:")
        for result in invalid_results:
            logger.warning(f"  {result.code}: {result.message} ({result.severity.value})")
    else:
        logger.error("No validation issues found in invalid encounter, but issues were expected.")
    
    # Generate validation report
    logger.info("\nValidation Report:")
    report = validator.generate_validation_report()
    print(report)


if __name__ == "__main__":
    test_validator()