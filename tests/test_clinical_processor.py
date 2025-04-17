"""
Test script for the Clinical Domain Processor.

This script demonstrates the use of the ClinicalProcessor class to process
clinical encounters and generate output files.
"""

import os
import sys
import json
from datetime import datetime, timedelta
import logging

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.processors.clinical_processor import ClinicalProcessor
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


def create_sample_encounters(count: int = 5) -> list:
    """
    Create a list of sample clinical encounters for testing.
    
    Args:
        count: Number of encounters to create.
        
    Returns:
        A list of sample clinical encounters.
    """
    encounters = []
    
    # Create encounters with different types and statuses
    encounter_types = [
        EncounterType.INPATIENT,
        EncounterType.AMBULATORY,
        EncounterType.EMERGENCY,
        EncounterType.OBSERVATION,
        EncounterType.VIRTUAL
    ]
    
    encounter_statuses = [
        EncounterStatus.PLANNED,
        EncounterStatus.ARRIVED,
        EncounterStatus.IN_PROGRESS,
        EncounterStatus.FINISHED,
        EncounterStatus.CANCELLED
    ]
    
    for i in range(count):
        # Create base encounter
        now = datetime.now()
        encounter_type = encounter_types[i % len(encounter_types)]
        encounter_status = encounter_statuses[i % len(encounter_statuses)]
        
        # Set appropriate dates based on status
        if encounter_status == EncounterStatus.PLANNED:
            start_datetime = now + timedelta(days=i+1)
            end_datetime = None
        elif encounter_status == EncounterStatus.ARRIVED:
            start_datetime = now - timedelta(hours=1)
            end_datetime = None
        elif encounter_status == EncounterStatus.IN_PROGRESS:
            start_datetime = now - timedelta(days=1)
            end_datetime = None
        elif encounter_status == EncounterStatus.FINISHED:
            start_datetime = now - timedelta(days=i+3)
            end_datetime = now - timedelta(days=i)
        else:  # CANCELLED
            start_datetime = now - timedelta(days=i+1)
            end_datetime = None
        
        # Set length of stay for inpatient
        length_of_stay = None
        if encounter_type == EncounterType.INPATIENT and end_datetime:
            length_of_stay = (end_datetime - start_datetime).days
        
        # Create encounter
        encounter = ClinicalEncounter(
            id=f"ENC{100000+i}",
            type=encounter_type,
            status=encounter_status,
            class_type=EncounterClass.INPATIENT if encounter_type == EncounterType.INPATIENT else EncounterClass.OUTPATIENT,
            priority=EncounterPriority.ROUTINE,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            length_of_stay=length_of_stay,
            admission_type="Elective" if encounter_type == EncounterType.INPATIENT else None,
            discharge_disposition="Home" if encounter_status == EncounterStatus.FINISHED and encounter_type == EncounterType.INPATIENT else None,
            readmission=False,
            chief_complaint=f"Sample chief complaint {i+1}",
            reason_code="R07.9",
            service_type="Medical",
            account_number=f"ACC{900000+i}",
            visit_number=f"VN{800000+i}",
            episode_of_care_id=f"EP{700000+i}"
        )
        
        # Add participants
        patient = EncounterParticipant(
            id=f"PART{100000+i*2}",
            encounter_id=encounter.id,
            participant_type=ParticipantType.PATIENT,
            participant_id=f"MEM{900000+i}",
            role=None,
            start_datetime=encounter.start_datetime,
            end_datetime=encounter.end_datetime,
            primary=True
        )
        
        provider = EncounterParticipant(
            id=f"PART{100001+i*2}",
            encounter_id=encounter.id,
            participant_type=ParticipantType.PROVIDER,
            participant_id=f"PRV{800000+i}",
            role=ProviderRole.ATTENDING,
            start_datetime=encounter.start_datetime,
            end_datetime=encounter.end_datetime,
            primary=True
        )
        
        encounter.participants = [patient, provider]
        
        # Add location
        location_type = LocationType.WARD if encounter_type == EncounterType.INPATIENT else (
            LocationType.ER if encounter_type == EncounterType.EMERGENCY else LocationType.CLINIC
        )
        
        location = EncounterLocation(
            id=f"LOC{100000+i}",
            encounter_id=encounter.id,
            facility_id=f"FAC{900000+i}",
            department_id=f"DEP{800000+i}",
            location_type=location_type,
            bed_id=f"BED{700000+i}" if encounter_type == EncounterType.INPATIENT else None,
            start_datetime=encounter.start_datetime,
            end_datetime=encounter.end_datetime,
            status=LocationStatus.COMPLETED if encounter_status == EncounterStatus.FINISHED else LocationStatus.ACTIVE
        )
        
        encounter.locations = [location]
        
        # Add diagnosis
        diagnosis = EncounterDiagnosis(
            id=f"DIAG{100000+i}",
            encounter_id=encounter.id,
            condition_id=f"COND{900000+i}",
            diagnosis_code="J18.9",  # Pneumonia
            diagnosis_description="Pneumonia, unspecified",
            diagnosis_type=DiagnosisType.PRINCIPAL,
            present_on_admission=True if encounter_type == EncounterType.INPATIENT else None,
            rank=1,
            provider_id=provider.participant_id
        )
        
        encounter.diagnoses = [diagnosis]
        
        # Add procedure
        procedure = EncounterProcedure(
            id=f"PROC{100000+i}",
            encounter_id=encounter.id,
            procedure_id=f"PROC{900000+i}",
            procedure_code="71045",  # Chest X-ray
            procedure_description="X-ray, chest, single view",
            datetime=encounter.start_datetime + timedelta(hours=4) if encounter.start_datetime <= now else None,
            duration_minutes=15,
            provider_id=provider.participant_id,
            location_id=location.id,
            status=ProcedureStatus.COMPLETED if encounter_status == EncounterStatus.FINISHED else ProcedureStatus.PLANNED,
            primary=False
        )
        
        encounter.procedures = [procedure]
        
        # Add note
        note = ClinicalNote(
            id=f"NOTE{100000+i}",
            encounter_id=encounter.id,
            note_type=NoteType.H_AND_P,
            author_id=provider.participant_id,
            datetime=encounter.start_datetime + timedelta(hours=1) if encounter.start_datetime <= now else None,
            content=f"Sample clinical note content for encounter {encounter.id}...",
            status=NoteStatus.FINAL if encounter_status == EncounterStatus.FINISHED else NoteStatus.DRAFT,
            signed=encounter_status == EncounterStatus.FINISHED,
            signed_datetime=encounter.start_datetime + timedelta(hours=2) if encounter_status == EncounterStatus.FINISHED and encounter.start_datetime <= now else None
        )
        
        # Add discharge summary for finished inpatient encounters
        if encounter_status == EncounterStatus.FINISHED and encounter_type == EncounterType.INPATIENT:
            discharge_summary = ClinicalNote(
                id=f"NOTE{200000+i}",
                encounter_id=encounter.id,
                note_type=NoteType.DISCHARGE_SUMMARY,
                author_id=provider.participant_id,
                datetime=encounter.end_datetime - timedelta(hours=1) if encounter.end_datetime else None,
                content=f"Sample discharge summary content for encounter {encounter.id}...",
                status=NoteStatus.FINAL,
                signed=True,
                signed_datetime=encounter.end_datetime - timedelta(minutes=30) if encounter.end_datetime else None
            )
            encounter.notes = [note, discharge_summary]
        else:
            encounter.notes = [note]
        
        encounters.append(encounter)
    
    return encounters


def test_processor():
    """Test the clinical processor with sample encounters."""
    # Create processor configuration
    config = {
        'output_dir': 'output/clinical',
        'skip_invalid_encounters': False,
        'validation_config': {}
    }
    
    # Create processor
    processor = ClinicalProcessor(config)
    
    # Create sample encounters
    encounters = create_sample_encounters(5)
    
    # Process encounters
    processed_encounters = processor.process(encounters)
    
    # Generate and print report
    report = processor.generate_report('output/clinical/processing_report.txt')
    print(report)
    
    logger.info(f"Processed {len(processed_encounters)} encounters")
    logger.info(f"Output files saved to {config['output_dir']}")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs('output/clinical', exist_ok=True)
    
    test_processor()