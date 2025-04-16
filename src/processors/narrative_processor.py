"""
Narrative content processor for the synthetic healthcare data generator.

This module processes and enriches narrative content data.
"""

import json
import logging
import os
import random
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np

from src.models.narrative import (
    AuthorizationRationale, CarePlan, ClinicalNote, CommunicationRecord
)
from src.processors.base_processor import BaseProcessor


class NarrativeProcessor(BaseProcessor):
    """Processor for narrative content data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the narrative processor.
        
        Args:
            config: Configuration dictionary for the processor.
        """
        super().__init__(config)
        
        # Load processing rules
        self.processing_rules = self._load_processing_rules()
        
        # Initialize statistics
        self.stats = {
            "clinical_notes": {
                "total": 0,
                "by_type": {},
                "avg_length": 0
            },
            "communications": {
                "total": 0,
                "by_type": {},
                "avg_length": 0
            },
            "care_plans": {
                "total": 0,
                "by_type": {},
                "avg_goals": 0,
                "avg_interventions": 0
            },
            "authorization_rationales": {
                "total": 0,
                "avg_evidence_count": 0,
                "avg_alternatives_count": 0
            }
        }
    
    def _load_processing_rules(self) -> Dict[str, Any]:
        """
        Load processing rules from the configuration.
        
        Returns:
            Dictionary of processing rules.
        """
        # Default processing rules if not provided in config
        default_rules = {
            "clinical_notes": {
                "min_length": {
                    "chief_complaint": 10,
                    "subjective": 50,
                    "objective": 100,
                    "assessment": 30,
                    "plan": 50
                },
                "required_sections": [
                    "chief_complaint", "subjective", "objective", "assessment", "plan"
                ],
                "consistency_checks": [
                    "diagnosis_codes_match_conditions",
                    "procedure_codes_match_procedures",
                    "medication_references_match_medications"
                ]
            },
            "communications": {
                "min_length": {
                    "subject": 5,
                    "content": 30
                },
                "required_fields": [
                    "subject", "content", "sender_id", "recipient_id"
                ]
            },
            "care_plans": {
                "min_length": {
                    "title": 5,
                    "description": 30
                },
                "min_goals": 1,
                "min_interventions": 1,
                "required_fields": [
                    "title", "description", "goals", "interventions"
                ]
            },
            "authorization_rationales": {
                "min_length": {
                    "clinical_summary": 50,
                    "medical_necessity": 50
                },
                "min_evidence_references": 1,
                "min_guidelines_referenced": 1,
                "min_alternatives_considered": 1,
                "required_fields": [
                    "clinical_summary", "medical_necessity", 
                    "evidence_references", "guidelines_referenced", "alternatives_considered"
                ]
            }
        }
        
        # Use processing rules from config if available, otherwise use defaults
        return self.config.get("narrative_processing_rules", default_rules)
    
    def process(self, data: List[Union[ClinicalNote, CommunicationRecord, CarePlan, AuthorizationRationale]]) -> List[Union[ClinicalNote, CommunicationRecord, CarePlan, AuthorizationRationale]]:
        """
        Process narrative content data.
        
        Args:
            data: List of narrative content items to process.
            
        Returns:
            List of processed narrative content items.
        """
        if not data:
            self.logger.warning("No narrative content data to process")
            return []
        
        processed_data = []
        
        # Reset statistics
        self._reset_statistics()
        
        # Process each item based on its type
        for item in data:
            if isinstance(item, ClinicalNote):
                processed_item = self._process_clinical_note(item)
                self._update_clinical_note_stats(processed_item)
            elif isinstance(item, CommunicationRecord):
                processed_item = self._process_communication(item)
                self._update_communication_stats(processed_item)
            elif isinstance(item, CarePlan):
                processed_item = self._process_care_plan(item)
                self._update_care_plan_stats(processed_item)
            elif isinstance(item, AuthorizationRationale):
                processed_item = self._process_authorization_rationale(item)
                self._update_authorization_rationale_stats(processed_item)
            else:
                self.logger.warning(f"Unknown narrative content type: {type(item)}")
                processed_item = item
            
            processed_data.append(processed_item)
        
        # Calculate averages
        self._calculate_statistics()
        
        self.logger.info(f"Processed {len(processed_data)} narrative content items")
        return processed_data
    
    def _reset_statistics(self) -> None:
        """Reset statistics for a new processing run."""
        self.stats = {
            "clinical_notes": {
                "total": 0,
                "by_type": {},
                "avg_length": 0,
                "total_length": 0
            },
            "communications": {
                "total": 0,
                "by_type": {},
                "avg_length": 0,
                "total_length": 0
            },
            "care_plans": {
                "total": 0,
                "by_type": {},
                "avg_goals": 0,
                "total_goals": 0,
                "avg_interventions": 0,
                "total_interventions": 0
            },
            "authorization_rationales": {
                "total": 0,
                "avg_evidence_count": 0,
                "total_evidence_count": 0,
                "avg_alternatives_count": 0,
                "total_alternatives_count": 0
            }
        }
    
    def _process_clinical_note(self, note: ClinicalNote) -> ClinicalNote:
        """
        Process a clinical note.
        
        Args:
            note: Clinical note to process.
            
        Returns:
            Processed clinical note.
        """
        # Get processing rules for clinical notes
        rules = self.processing_rules.get("clinical_notes", {})
        
        # Check and enforce minimum lengths
        min_lengths = rules.get("min_length", {})
        
        # Chief complaint
        if len(note.chief_complaint) < min_lengths.get("chief_complaint", 10):
            note.chief_complaint = self._expand_text(note.chief_complaint, min_lengths.get("chief_complaint", 10))
        
        # Subjective
        if len(note.subjective) < min_lengths.get("subjective", 50):
            note.subjective = self._expand_text(note.subjective, min_lengths.get("subjective", 50))
        
        # Objective
        if len(note.objective) < min_lengths.get("objective", 100):
            note.objective = self._expand_text(note.objective, min_lengths.get("objective", 100))
        
        # Assessment
        if len(note.assessment) < min_lengths.get("assessment", 30):
            note.assessment = self._expand_text(note.assessment, min_lengths.get("assessment", 30))
        
        # Plan
        if len(note.plan) < min_lengths.get("plan", 50):
            note.plan = self._expand_text(note.plan, min_lengths.get("plan", 50))
        
        # Ensure consistency between diagnosis codes and conditions
        # In a real implementation, this would map conditions to actual ICD-10 codes
        # For this example, we'll just ensure there are diagnosis codes if there are conditions
        if "diagnosis_codes_match_conditions" in rules.get("consistency_checks", []):
            if not note.diagnosis_codes and hasattr(note, 'conditions') and note.conditions:
                # Generate mock diagnosis codes
                note.diagnosis_codes = self._generate_mock_diagnosis_codes(len(note.conditions))
        
        return note
    
    def _process_communication(self, comm: CommunicationRecord) -> CommunicationRecord:
        """
        Process a communication record.
        
        Args:
            comm: Communication record to process.
            
        Returns:
            Processed communication record.
        """
        # Get processing rules for communications
        rules = self.processing_rules.get("communications", {})
        
        # Check and enforce minimum lengths
        min_lengths = rules.get("min_length", {})
        
        # Subject
        if len(comm.subject) < min_lengths.get("subject", 5):
            comm.subject = self._expand_text(comm.subject, min_lengths.get("subject", 5))
        
        # Content
        if len(comm.content) < min_lengths.get("content", 30):
            comm.content = self._expand_text(comm.content, min_lengths.get("content", 30))
        
        return comm
    
    def _process_care_plan(self, plan: CarePlan) -> CarePlan:
        """
        Process a care plan.
        
        Args:
            plan: Care plan to process.
            
        Returns:
            Processed care plan.
        """
        # Get processing rules for care plans
        rules = self.processing_rules.get("care_plans", {})
        
        # Check and enforce minimum lengths
        min_lengths = rules.get("min_length", {})
        
        # Title
        if len(plan.title) < min_lengths.get("title", 5):
            plan.title = self._expand_text(plan.title, min_lengths.get("title", 5))
        
        # Description
        if len(plan.description) < min_lengths.get("description", 30):
            plan.description = self._expand_text(plan.description, min_lengths.get("description", 30))
        
        # Ensure minimum number of goals
        min_goals = rules.get("min_goals", 1)
        if len(plan.goals) < min_goals:
            # Add generic goals to meet the minimum
            for _ in range(min_goals - len(plan.goals)):
                from src.models.narrative import CarePlanGoal
                from datetime import datetime, timedelta
                
                target_date = datetime.now() + timedelta(days=random.randint(30, 180))
                goal = CarePlanGoal(
                    description="Improve overall health status and function",
                    target_date=target_date,
                    status="active",
                    priority="medium"
                )
                plan.goals.append(goal)
        
        # Ensure minimum number of interventions
        min_interventions = rules.get("min_interventions", 1)
        if len(plan.interventions) < min_interventions:
            # Add generic interventions to meet the minimum
            for _ in range(min_interventions - len(plan.interventions)):
                from src.models.narrative import CarePlanIntervention
                
                intervention = CarePlanIntervention(
                    description="Follow recommended treatment plan",
                    type="education",
                    frequency="ongoing",
                    instructions="Adhere to all prescribed treatments and follow-up appointments"
                )
                plan.interventions.append(intervention)
        
        return plan
    
    def _process_authorization_rationale(self, rationale: AuthorizationRationale) -> AuthorizationRationale:
        """
        Process an authorization rationale.
        
        Args:
            rationale: Authorization rationale to process.
            
        Returns:
            Processed authorization rationale.
        """
        # Get processing rules for authorization rationales
        rules = self.processing_rules.get("authorization_rationales", {})
        
        # Check and enforce minimum lengths
        min_lengths = rules.get("min_length", {})
        
        # Clinical summary
        if len(rationale.clinical_summary) < min_lengths.get("clinical_summary", 50):
            rationale.clinical_summary = self._expand_text(rationale.clinical_summary, min_lengths.get("clinical_summary", 50))
        
        # Medical necessity
        if len(rationale.medical_necessity) < min_lengths.get("medical_necessity", 50):
            rationale.medical_necessity = self._expand_text(rationale.medical_necessity, min_lengths.get("medical_necessity", 50))
        
        # Ensure minimum number of evidence references
        min_evidence = rules.get("min_evidence_references", 1)
        if len(rationale.evidence_references) < min_evidence:
            # Add generic evidence references to meet the minimum
            for _ in range(min_evidence - len(rationale.evidence_references)):
                year = random.randint(datetime.now().year - 10, datetime.now().year - 1)
                rationale.evidence_references.append(
                    f"Smith et al. ({year}). Clinical Outcomes Study. Journal of Medical Research."
                )
        
        # Ensure minimum number of guidelines referenced
        min_guidelines = rules.get("min_guidelines_referenced", 1)
        if len(rationale.guidelines_referenced) < min_guidelines:
            # Add generic guidelines to meet the minimum
            for _ in range(min_guidelines - len(rationale.guidelines_referenced)):
                rationale.guidelines_referenced.append(
                    "Clinical Practice Guidelines for Evidence-Based Care"
                )
        
        # Ensure minimum number of alternatives considered
        min_alternatives = rules.get("min_alternatives_considered", 1)
        if len(rationale.alternatives_considered) < min_alternatives:
            # Add generic alternatives to meet the minimum
            for _ in range(min_alternatives - len(rationale.alternatives_considered)):
                rationale.alternatives_considered.append(
                    "Conservative management with monitoring"
                )
        
        return rationale
    
    def _expand_text(self, text: str, min_length: int) -> str:
        """
        Expand text to meet minimum length requirements.
        
        Args:
            text: Original text.
            min_length: Minimum required length.
            
        Returns:
            Expanded text.
        """
        if len(text) >= min_length:
            return text
        
        # Generic expansions to add to text
        expansions = [
            "Further evaluation is recommended.",
            "Continued monitoring is advised.",
            "Patient education was provided.",
            "Will reassess at next visit.",
            "Treatment plan was discussed with patient.",
            "Patient expressed understanding of the plan.",
            "Follow-up appointment scheduled.",
            "Risks and benefits were discussed.",
            "Patient tolerated the procedure well.",
            "No complications were noted."
        ]
        
        expanded_text = text
        while len(expanded_text) < min_length:
            expansion = random.choice(expansions)
            if not expanded_text.endswith("."):
                expanded_text += ". "
            expanded_text += expansion + " "
        
        return expanded_text.strip()
    
    def _generate_mock_diagnosis_codes(self, count: int) -> List[str]:
        """
        Generate mock diagnosis codes.
        
        Args:
            count: Number of codes to generate.
            
        Returns:
            List of mock diagnosis codes.
        """
        codes = []
        for _ in range(count):
            letter = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"])
            number = random.randint(0, 99)
            decimal = random.randint(0, 9)
            codes.append(f"{letter}{number}.{decimal}")
        
        return codes
    
    def _update_clinical_note_stats(self, note: ClinicalNote) -> None:
        """
        Update statistics for clinical notes.
        
        Args:
            note: Processed clinical note.
        """
        self.stats["clinical_notes"]["total"] += 1
        
        # Update by type
        note_type = note.note_type.value if hasattr(note.note_type, 'value') else str(note.note_type)
        if note_type not in self.stats["clinical_notes"]["by_type"]:
            self.stats["clinical_notes"]["by_type"][note_type] = 0
        self.stats["clinical_notes"]["by_type"][note_type] += 1
        
        # Update length stats
        total_length = (
            len(note.chief_complaint) +
            len(note.subjective) +
            len(note.objective) +
            len(note.assessment) +
            len(note.plan)
        )
        self.stats["clinical_notes"]["total_length"] += total_length
    
    def _update_communication_stats(self, comm: CommunicationRecord) -> None:
        """
        Update statistics for communication records.
        
        Args:
            comm: Processed communication record.
        """
        self.stats["communications"]["total"] += 1
        
        # Update by type
        comm_type = comm.communication_type.value if hasattr(comm.communication_type, 'value') else str(comm.communication_type)
        if comm_type not in self.stats["communications"]["by_type"]:
            self.stats["communications"]["by_type"][comm_type] = 0
        self.stats["communications"]["by_type"][comm_type] += 1
        
        # Update length stats
        total_length = len(comm.subject) + len(comm.content)
        self.stats["communications"]["total_length"] += total_length
    
    def _update_care_plan_stats(self, plan: CarePlan) -> None:
        """
        Update statistics for care plans.
        
        Args:
            plan: Processed care plan.
        """
        self.stats["care_plans"]["total"] += 1
        
        # Update by type
        plan_type = plan.care_plan_type.value if hasattr(plan.care_plan_type, 'value') else str(plan.care_plan_type)
        if plan_type not in self.stats["care_plans"]["by_type"]:
            self.stats["care_plans"]["by_type"][plan_type] = 0
        self.stats["care_plans"]["by_type"][plan_type] += 1
        
        # Update goals and interventions stats
        self.stats["care_plans"]["total_goals"] += len(plan.goals)
        self.stats["care_plans"]["total_interventions"] += len(plan.interventions)
    
    def _update_authorization_rationale_stats(self, rationale: AuthorizationRationale) -> None:
        """
        Update statistics for authorization rationales.
        
        Args:
            rationale: Processed authorization rationale.
        """
        self.stats["authorization_rationales"]["total"] += 1
        
        # Update evidence and alternatives stats
        self.stats["authorization_rationales"]["total_evidence_count"] += len(rationale.evidence_references)
        self.stats["authorization_rationales"]["total_alternatives_count"] += len(rationale.alternatives_considered)
    
    def _calculate_statistics(self) -> None:
        """Calculate average statistics after processing all items."""
        # Clinical notes
        if self.stats["clinical_notes"]["total"] > 0:
            self.stats["clinical_notes"]["avg_length"] = (
                self.stats["clinical_notes"]["total_length"] / self.stats["clinical_notes"]["total"]
            )
        
        # Communications
        if self.stats["communications"]["total"] > 0:
            self.stats["communications"]["avg_length"] = (
                self.stats["communications"]["total_length"] / self.stats["communications"]["total"]
            )
        
        # Care plans
        if self.stats["care_plans"]["total"] > 0:
            self.stats["care_plans"]["avg_goals"] = (
                self.stats["care_plans"]["total_goals"] / self.stats["care_plans"]["total"]
            )
            self.stats["care_plans"]["avg_interventions"] = (
                self.stats["care_plans"]["total_interventions"] / self.stats["care_plans"]["total"]
            )
        
        # Authorization rationales
        if self.stats["authorization_rationales"]["total"] > 0:
            self.stats["authorization_rationales"]["avg_evidence_count"] = (
                self.stats["authorization_rationales"]["total_evidence_count"] / 
                self.stats["authorization_rationales"]["total"]
            )
            self.stats["authorization_rationales"]["avg_alternatives_count"] = (
                self.stats["authorization_rationales"]["total_alternatives_count"] / 
                self.stats["authorization_rationales"]["total"]
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the processed narrative content.
        
        Returns:
            Dictionary of statistics.
        """
        return self.stats