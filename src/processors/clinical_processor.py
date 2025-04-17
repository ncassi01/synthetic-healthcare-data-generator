"""
Clinical Domain Processor

This module provides a processor for clinical encounter data, including validation,
transformation, and output formatting.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from src.processors.base_processor import BaseProcessor
from src.models.clinical import (
    ClinicalEncounter, EncounterParticipant, EncounterLocation,
    EncounterDiagnosis, EncounterProcedure, ClinicalNote,
    EncounterService, EncounterAssessment, EncounterMedication,
    EncounterTransition
)
from src.utils.clinical_validator import ClinicalValidator


class ClinicalProcessor(BaseProcessor):
    """
    Processor for clinical encounter data.
    
    This class processes clinical encounters and related entities, including validation,
    transformation, and output formatting.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the clinical processor.
        
        Args:
            config: Configuration dictionary for the processor.
        """
        super().__init__(config)
        self.validator = ClinicalValidator(config.get('validation_config', {}))
        
        # Output paths
        self.output_dir = config.get('output_dir', 'output')
        self.encounters_path = os.path.join(self.output_dir, 'encounters.json')
        self.clinical_notes_path = os.path.join(self.output_dir, 'clinical_notes.json')
        self.statistics_path = os.path.join(self.output_dir, 'encounter_statistics.json')
        
        # Statistics
        self.statistics = {
            'encounter_count': 0,
            'encounter_types': {},
            'encounter_statuses': {},
            'participant_count': 0,
            'location_count': 0,
            'diagnosis_count': 0,
            'procedure_count': 0,
            'note_count': 0,
            'service_count': 0,
            'assessment_count': 0,
            'medication_count': 0,
            'transition_count': 0,
            'validation_errors': 0,
            'validation_warnings': 0
        }
    
    def process(self, encounters: List[ClinicalEncounter]) -> List[ClinicalEncounter]:
        """
        Process clinical encounters.
        
        Args:
            encounters: List of clinical encounters to process.
            
        Returns:
            List of processed clinical encounters.
        """
        self.logger.info(f"Processing {len(encounters)} clinical encounters")
        
        # Validate encounters
        validation_results = self.validator.validate_encounters(encounters)
        
        # Update statistics
        self.statistics['encounter_count'] = len(encounters)
        self.statistics['validation_errors'] = len(self.validator.errors)
        self.statistics['validation_warnings'] = len(self.validator.warnings)
        
        # Process each encounter
        processed_encounters = []
        for encounter in encounters:
            # Skip encounters with validation errors if configured to do so
            if (encounter.id in validation_results and 
                self.config.get('skip_invalid_encounters', False) and
                any(r.severity == 'Error' for r in validation_results[encounter.id])):
                self.logger.warning(f"Skipping invalid encounter: {encounter.id}")
                continue
            
            # Process the encounter
            processed_encounter = self._process_encounter(encounter)
            processed_encounters.append(processed_encounter)
            
            # Update statistics
            self._update_statistics(processed_encounter)
        
        # Save outputs
        self._save_outputs(processed_encounters)
        
        return processed_encounters
    
    def _process_encounter(self, encounter: ClinicalEncounter) -> ClinicalEncounter:
        """
        Process a single clinical encounter.
        
        Args:
            encounter: The clinical encounter to process.
            
        Returns:
            The processed clinical encounter.
        """
        # In a real implementation, this would apply transformations, enrichments, etc.
        # For now, we'll just return the encounter as-is
        return encounter
    
    def _update_statistics(self, encounter: ClinicalEncounter) -> None:
        """
        Update statistics based on an encounter.
        
        Args:
            encounter: The clinical encounter to analyze.
        """
        # Update encounter type statistics
        encounter_type = encounter.type.value
        self.statistics['encounter_types'][encounter_type] = (
            self.statistics['encounter_types'].get(encounter_type, 0) + 1
        )
        
        # Update encounter status statistics
        encounter_status = encounter.status.value
        self.statistics['encounter_statuses'][encounter_status] = (
            self.statistics['encounter_statuses'].get(encounter_status, 0) + 1
        )
        
        # Update entity counts
        self.statistics['participant_count'] += len(encounter.participants)
        self.statistics['location_count'] += len(encounter.locations)
        self.statistics['diagnosis_count'] += len(encounter.diagnoses)
        self.statistics['procedure_count'] += len(encounter.procedures)
        self.statistics['note_count'] += len(encounter.notes)
        self.statistics['service_count'] += len(encounter.services)
        self.statistics['assessment_count'] += len(encounter.assessments)
        self.statistics['medication_count'] += len(encounter.medications)
    
    def _save_outputs(self, encounters: List[ClinicalEncounter]) -> None:
        """
        Save processed data to output files.
        
        Args:
            encounters: List of processed clinical encounters.
        """
        # Save encounters
        self.save_to_json(encounters, self.encounters_path)
        
        # Extract and save clinical notes
        clinical_notes = []
        for encounter in encounters:
            for note in encounter.notes:
                clinical_notes.append(note)
        
        self.save_to_json(clinical_notes, self.clinical_notes_path)
        
        # Save statistics
        with open(self.statistics_path, 'w') as f:
            json.dump(self.statistics, f, indent=2)
        
        self.logger.info(f"Saved statistics to {self.statistics_path}")
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a processing report.
        
        Args:
            output_path: Optional path to save the report.
            
        Returns:
            The report as a string.
        """
        # Generate validation report
        validation_report = self.validator.generate_validation_report()
        
        # Generate processing report
        report = [
            "Clinical Domain Processing Report",
            "===============================",
            "",
            f"Processed {self.statistics['encounter_count']} encounters",
            "",
            "Encounter Types:",
            "--------------"
        ]
        
        for encounter_type, count in self.statistics['encounter_types'].items():
            report.append(f"{encounter_type}: {count}")
        
        report.extend([
            "",
            "Encounter Statuses:",
            "-----------------"
        ])
        
        for encounter_status, count in self.statistics['encounter_statuses'].items():
            report.append(f"{encounter_status}: {count}")
        
        report.extend([
            "",
            "Entity Counts:",
            "-------------",
            f"Participants: {self.statistics['participant_count']}",
            f"Locations: {self.statistics['location_count']}",
            f"Diagnoses: {self.statistics['diagnosis_count']}",
            f"Procedures: {self.statistics['procedure_count']}",
            f"Notes: {self.statistics['note_count']}",
            f"Services: {self.statistics['service_count']}",
            f"Assessments: {self.statistics['assessment_count']}",
            f"Medications: {self.statistics['medication_count']}",
            "",
            "Validation Results:",
            "------------------",
            f"Errors: {self.statistics['validation_errors']}",
            f"Warnings: {self.statistics['validation_warnings']}",
            "",
            "Validation Details:",
            "------------------"
        ])
        
        report.append(validation_report)
        
        report_text = "\n".join(report)
        
        # Save report if output path is provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
            self.logger.info(f"Saved processing report to {output_path}")
        
        return report_text