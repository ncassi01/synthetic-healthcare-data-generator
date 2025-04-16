"""
Clinical Domain Validation Framework

This module provides a comprehensive validation framework for the Clinical domain,
including entity-level validation, cross-entity validation, temporal validation,
and clinical realism validation.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from src.models.clinical import (
    ClinicalEncounter, EncounterParticipant, EncounterLocation,
    EncounterDiagnosis, EncounterProcedure, ClinicalNote,
    EncounterService, EncounterAssessment, EncounterMedication,
    EncounterTransition, ValidationResult, ValidationSeverity,
    EncounterType, EncounterStatus, ParticipantType, LocationType,
    DiagnosisType, ProcedureStatus, NoteType, TransitionType
)

logger = logging.getLogger(__name__)


class ClinicalValidator:
    """
    Comprehensive validator for Clinical domain data.
    
    This class provides methods for validating clinical data at different levels:
    - Entity-level validation (single entity)
    - Cross-entity validation (relationships)
    - Temporal validation (time sequences)
    - Clinical realism validation (medical appropriateness)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the clinical validator."""
        self.config = config or {}
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Track entities that have been validated
        self.validated_encounters = set()
        self.validated_participants = set()
        self.validated_locations = set()
        self.validated_diagnoses = set()
        self.validated_procedures = set()
        self.validated_notes = set()
        self.validated_services = set()
        self.validated_assessments = set()
        self.validated_medications = set()
        self.validated_transitions = set()
        
        # Initialize ICD-10 and CPT code validation sets
        self.valid_icd10_codes = self._load_valid_icd10_codes()
        self.valid_cpt_codes = self._load_valid_cpt_codes()
    
    def _load_valid_icd10_codes(self) -> Set[str]:
        """Load valid ICD-10 codes from reference data."""
        # In a real implementation, this would load from a file or database
        return {
            "J18.9", "I10", "E11.9", "F32.9", "M54.5", "R07.9", "N39.0",
            "K21.9", "H40.9", "G47.00", "D64.9", "L40.0", "Z23"
        }
    
    def _load_valid_cpt_codes(self) -> Set[str]:
        """Load valid CPT codes from reference data."""
        # In a real implementation, this would load from a file or database
        return {
            "99213", "99214", "99215", "99223", "99233", "99291",
            "71045", "71046", "93000", "80053", "85025", "82947"
        }
    
    def validate_encounter(self, encounter: ClinicalEncounter) -> List[ValidationResult]:
        """Validate a clinical encounter and its related entities."""
        results = []
        
        # Skip if already validated
        if encounter.id in self.validated_encounters:
            return results
        
        # Entity-level validation
        results.extend(encounter.validate())
        
        # Validate related entities
        for participant in encounter.participants:
            results.extend(self.validate_participant(participant, encounter))
        
        for location in encounter.locations:
            results.extend(self.validate_location(location, encounter))
        
        for diagnosis in encounter.diagnoses:
            results.extend(self.validate_diagnosis(diagnosis, encounter))
        
        for procedure in encounter.procedures:
            results.extend(self.validate_procedure(procedure, encounter))
        
        for note in encounter.notes:
            results.extend(self.validate_note(note, encounter))
        
        for service in encounter.services:
            results.extend(self.validate_service(service, encounter))
        
        for assessment in encounter.assessments:
            results.extend(self.validate_assessment(assessment, encounter))
        
        for medication in encounter.medications:
            results.extend(self.validate_medication(medication, encounter))
        
        # Cross-entity validation
        results.extend(self._validate_encounter_cross_entity(encounter))
        
        # Temporal validation
        results.extend(self._validate_encounter_temporal(encounter))
        
        # Clinical realism validation
        results.extend(self._validate_encounter_clinical_realism(encounter))
        
        # Mark as validated
        self.validated_encounters.add(encounter.id)
        
        # Categorize results
        for result in results:
            if result.severity == ValidationSeverity.ERROR:
                self.errors.append(result)
            elif result.severity == ValidationSeverity.WARNING:
                self.warnings.append(result)
            else:
                self.info.append(result)
        
        return results
    
    def validate_participant(self, participant: EncounterParticipant, 
                            encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter participant."""
        results = []
        
        # Skip if already validated
        if participant.id in self.validated_participants:
            return results
        
        # Entity-level validation
        results.extend(participant.validate())
        
        # PART-001: Each encounter must have exactly one primary patient
        if encounter:
            primary_patients = [p for p in encounter.participants 
                              if p.participant_type == ParticipantType.PATIENT and p.primary]
            if participant.participant_type == ParticipantType.PATIENT and participant.primary:
                if len(primary_patients) > 1:
                    results.append(ValidationResult(
                        code="PART-001",
                        message="Each encounter must have exactly one primary patient",
                        severity=ValidationSeverity.ERROR,
                        entity_id=participant.id
                    ))
        
        # PART-003: Participant dates must be within encounter date range
        if encounter and participant.start_datetime and encounter.start_datetime:
            if participant.start_datetime < encounter.start_datetime:
                results.append(ValidationResult(
                    code="PART-003",
                    message="Participant start date must be within encounter date range",
                    severity=ValidationSeverity.ERROR,
                    entity_id=participant.id
                ))
        
        # Mark as validated
        self.validated_participants.add(participant.id)
        
        return results
    
    def validate_location(self, location: EncounterLocation,
                         encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter location."""
        results = []
        
        # Skip if already validated
        if location.id in self.validated_locations:
            return results
        
        # Entity-level validation
        results.extend(location.validate())
        
        # LOC-001: Location dates must be within encounter date range
        if encounter and location.start_datetime and encounter.start_datetime:
            if location.start_datetime < encounter.start_datetime:
                results.append(ValidationResult(
                    code="LOC-001",
                    message="Location start date must be within encounter date range",
                    severity=ValidationSeverity.ERROR,
                    entity_id=location.id
                ))
        
        # Mark as validated
        self.validated_locations.add(location.id)
        
        return results
    
    def validate_diagnosis(self, diagnosis: EncounterDiagnosis,
                          encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter diagnosis."""
        results = []
        
        # Skip if already validated
        if diagnosis.id in self.validated_diagnoses:
            return results
        
        # Entity-level validation
        results.extend(diagnosis.validate())
        
        # DIAG-001: Diagnosis codes must be valid ICD-10 codes
        if diagnosis.diagnosis_code and diagnosis.diagnosis_code not in self.valid_icd10_codes:
            results.append(ValidationResult(
                code="DIAG-001",
                message=f"Invalid ICD-10 code: {diagnosis.diagnosis_code}",
                severity=ValidationSeverity.ERROR,
                entity_id=diagnosis.id
            ))
        
        # Mark as validated
        self.validated_diagnoses.add(diagnosis.id)
        
        return results
    
    def validate_procedure(self, procedure: EncounterProcedure,
                          encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter procedure."""
        results = []
        
        # Skip if already validated
        if procedure.id in self.validated_procedures:
            return results
        
        # Entity-level validation
        results.extend(procedure.validate())
        
        # PROC-001: Procedure codes must be valid CPT/HCPCS codes
        if procedure.procedure_code and procedure.procedure_code not in self.valid_cpt_codes:
            results.append(ValidationResult(
                code="PROC-001",
                message=f"Invalid CPT/HCPCS code: {procedure.procedure_code}",
                severity=ValidationSeverity.ERROR,
                entity_id=procedure.id
            ))
        
        # Mark as validated
        self.validated_procedures.add(procedure.id)
        
        return results
    
    def validate_note(self, note: ClinicalNote,
                     encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate a clinical note."""
        results = []
        
        # Skip if already validated
        if note.id in self.validated_notes:
            return results
        
        # Entity-level validation
        results.extend(note.validate())
        
        # NOTE-001: Note content required
        if not note.content:
            results.append(ValidationResult(
                code="NOTE-001",
                message="Note content required",
                severity=ValidationSeverity.ERROR,
                entity_id=note.id
            ))
        
        # Mark as validated
        self.validated_notes.add(note.id)
        
        return results
    
    def validate_service(self, service: EncounterService,
                        encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter service."""
        results = []
        
        # Skip if already validated
        if service.id in self.validated_services:
            return results
        
        # Entity-level validation
        results.extend(service.validate())
        
        # Mark as validated
        self.validated_services.add(service.id)
        
        return results
    
    def validate_assessment(self, assessment: EncounterAssessment,
                           encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter assessment."""
        results = []
        
        # Skip if already validated
        if assessment.id in self.validated_assessments:
            return results
        
        # Entity-level validation
        results.extend(assessment.validate())
        
        # Mark as validated
        self.validated_assessments.add(assessment.id)
        
        return results
    
    def validate_medication(self, medication: EncounterMedication,
                           encounter: Optional[ClinicalEncounter] = None) -> List[ValidationResult]:
        """Validate an encounter medication."""
        results = []
        
        # Skip if already validated
        if medication.id in self.validated_medications:
            return results
        
        # Entity-level validation
        results.extend(medication.validate())
        
        # Mark as validated
        self.validated_medications.add(medication.id)
        
        return results
    
    def validate_transition(self, transition: EncounterTransition) -> List[ValidationResult]:
        """Validate an encounter transition."""
        results = []
        
        # Skip if already validated
        if transition.id in self.validated_transitions:
            return results
        
        # Entity-level validation
        results.extend(transition.validate())
        
        # Mark as validated
        self.validated_transitions.add(transition.id)
        
        return results
    
    def _validate_encounter_cross_entity(self, encounter: ClinicalEncounter) -> List[ValidationResult]:
        """Perform cross-entity validation for an encounter."""
        results = []
        
        # Check for at least one location
        if not encounter.locations:
            results.append(ValidationResult(
                code="LOC-007",
                message="At least one location required for each encounter",
                severity=ValidationSeverity.ERROR,
                entity_id=encounter.id
            ))
        
        # Check for emergency location in emergency encounters
        if encounter.type == EncounterType.EMERGENCY:
            er_locations = [l for l in encounter.locations 
                          if l.location_type == LocationType.ER]
            if not er_locations:
                results.append(ValidationResult(
                    code="LOC-009",
                    message="Emergency encounters must have at least one emergency location",
                    severity=ValidationSeverity.ERROR,
                    entity_id=encounter.id
                ))
        
        return results
    
    def _validate_encounter_temporal(self, encounter: ClinicalEncounter) -> List[ValidationResult]:
        """Perform temporal validation for an encounter."""
        results = []
        
        # Check for inpatient location timeline consistency
        if encounter.type == EncounterType.INPATIENT and len(encounter.locations) > 1:
            # Sort locations by start time
            sorted_locations = sorted(encounter.locations, key=lambda l: l.start_datetime or datetime.min)
            
            # Check for gaps or overlaps
            for i in range(len(sorted_locations) - 1):
                current = sorted_locations[i]
                next_loc = sorted_locations[i + 1]
                
                if current.end_datetime and next_loc.start_datetime:
                    # Check for gap
                    if current.end_datetime < next_loc.start_datetime:
                        results.append(ValidationResult(
                            code="LT-002",
                            message="No temporal gaps in location for inpatient stays",
                            severity=ValidationSeverity.ERROR,
                            entity_id=encounter.id
                        ))
        
        return results
    
    def _validate_encounter_clinical_realism(self, encounter: ClinicalEncounter) -> List[ValidationResult]:
        """Perform clinical realism validation for an encounter."""
        results = []
        
        # Check for diagnoses appropriate for encounter type
        if encounter.type == EncounterType.EMERGENCY:
            emergency_appropriate = False
            for diagnosis in encounter.diagnoses:
                # This is a simplified check - in a real implementation, 
                # we would have a more comprehensive list of emergency-appropriate diagnoses
                emergency_codes = {"R07.9", "I21", "S06", "R10.9", "J96.0", "T07"}
                if diagnosis.diagnosis_code and diagnosis.diagnosis_code[:3] in emergency_codes:
                    emergency_appropriate = True
                    break
            
            if not emergency_appropriate and encounter.diagnoses:
                results.append(ValidationResult(
                    code="DP-001",
                    message="Diagnosis combinations must be clinically realistic for emergency encounters",
                    severity=ValidationSeverity.WARNING,
                    entity_id=encounter.id
                ))
        
        return results
    
    def validate_encounters(self, encounters: List[ClinicalEncounter]) -> Dict[str, List[ValidationResult]]:
        """Validate a list of clinical encounters."""
        validation_results = {}
        
        for encounter in encounters:
            results = self.validate_encounter(encounter)
            if results:
                validation_results[encounter.id] = results
        
        if validation_results:
            logger.warning(f"Found validation issues in {len(validation_results)} encounters")
        else:
            logger.info("No validation issues found")
        
        return validation_results
    
    def validate_transitions(self, transitions: List[EncounterTransition], 
                            encounters: Optional[Dict[str, ClinicalEncounter]] = None) -> List[ValidationResult]:
        """Validate transitions between encounters."""
        results = []
        
        for transition in transitions:
            # Entity-level validation
            results.extend(self.validate_transition(transition))
            
            # Cross-entity validation with encounters
            if encounters:
                from_encounter = encounters.get(transition.from_encounter_id)
                to_encounter = encounters.get(transition.to_encounter_id)
                
                if from_encounter and to_encounter:
                    # Check temporal sequence
                    if (from_encounter.end_datetime and to_encounter.start_datetime and
                        from_encounter.end_datetime > to_encounter.start_datetime):
                        results.append(ValidationResult(
                            code="ET-004",
                            message="No temporal overlaps between sequential encounters",
                            severity=ValidationSeverity.ERROR,
                            entity_id=transition.id
                        ))
        
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "info": len(self.info),
            "error_codes": self._count_by_code(self.errors),
            "warning_codes": self._count_by_code(self.warnings),
            "info_codes": self._count_by_code(self.info)
        }
    
    def _count_by_code(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Count validation results by code."""
        counts = {}
        for result in results:
            counts[result.code] = counts.get(result.code, 0) + 1
        return counts
    
    def generate_validation_report(self, output_format: str = "text") -> str:
        """Generate a validation report in the specified format."""
        summary = self.get_validation_summary()
        
        if output_format == "text":
            report = [
                "Clinical Domain Validation Report",
                "================================",
                f"Total Errors: {summary['errors']}",
                f"Total Warnings: {summary['warnings']}",
                f"Total Info: {summary['info']}",
                "",
                "Error Codes:",
                "-----------"
            ]
            
            for code, count in summary['error_codes'].items():
                report.append(f"{code}: {count}")
            
            report.extend([
                "",
                "Warning Codes:",
                "-------------"
            ])
            
            for code, count in summary['warning_codes'].items():
                report.append(f"{code}: {count}")
            
            return "\n".join(report)
        
        elif output_format == "json":
            return str(summary)  # In a real implementation, this would use json.dumps()
        
        else:
            return f"Unsupported output format: {output_format}"
