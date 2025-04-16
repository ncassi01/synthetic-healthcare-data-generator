"""
Mental health narratives generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic mental health-related narratives
such as therapy notes, assessments, treatment plans, and progress notes.
"""

import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
import os
import sys

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from faker import Faker

from src.generators.base_generator import BaseGenerator


class MentalHealthNarrativesGenerator(BaseGenerator):
    """Generator for synthetic mental health narratives."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the mental health narratives generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract configuration
        self.mental_health_config = config.get('mental_health_config', {})
        
    def generate(self, count: int, member_ids: List[str] = None, provider_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic mental health narratives.
        
        Args:
            count: Number of narratives to generate.
            member_ids: Optional list of member IDs to associate with the narratives.
                If not provided, random IDs will be generated.
            provider_ids: Optional list of provider IDs to use as authors.
                If not provided, random IDs will be generated.
                
        Returns:
            List of generated mental health narrative entries.
        """
        self.logger.info(f"Generating {count} mental health narratives")
        
        if member_ids is None:
            # Generate random member IDs if not provided
            member_ids = [f"MEM{i:08d}" for i in range(count)]
        
        if provider_ids is None:
            # Generate random provider IDs if not provided
            provider_ids = [f"PRV{i:08d}" for i in range(20)]  # Generate 20 providers
        
        # If fewer member IDs than count, repeat member IDs
        if len(member_ids) < count:
            member_ids = (member_ids * (count // len(member_ids) + 1))[:count]
        
        narratives = []
        
        # Generate different types of mental health narratives
        narrative_types = [
            'initial_assessment', 
            'therapy_session_note', 
            'treatment_plan', 
            'progress_note',
            'psychiatric_evaluation'
        ]
        
        for i in range(count):
            narrative_type = random.choice(narrative_types)
            
            if narrative_type == 'initial_assessment':
                narrative = self._generate_initial_assessment(member_ids[i], provider_ids)
            elif narrative_type == 'therapy_session_note':
                narrative = self._generate_therapy_session_note(member_ids[i], provider_ids)
            elif narrative_type == 'treatment_plan':
                narrative = self._generate_treatment_plan(member_ids[i], provider_ids)
            elif narrative_type == 'progress_note':
                narrative = self._generate_progress_note(member_ids[i], provider_ids)
            elif narrative_type == 'psychiatric_evaluation':
                narrative = self._generate_psychiatric_evaluation(member_ids[i], provider_ids)
            
            narratives.append(narrative)
            
        self.logger.info(f"Generated {len(narratives)} mental health narratives")
        return narratives
    
    def _generate_initial_assessment(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate an initial mental health assessment."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 180 days
        assessment_date = datetime.now() - timedelta(days=random.randint(0, 180))
        
        return {
            "id": f"MHA{random.randint(10000, 99999)}",
            "type": "initial_assessment",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": assessment_date.strftime("%Y-%m-%d"),
            "presenting_problems": [
                {
                    "problem": "Depression",
                    "description": "Patient reports persistent low mood, anhedonia, and fatigue.",
                    "duration": "3 months",
                    "severity": "Moderate"
                }
            ],
            "diagnoses": [
                {"code": "F32.1", "name": "Major Depressive Disorder, moderate"}
            ],
            "recommendations": [
                "Individual therapy, weekly sessions",
                "Psychiatric evaluation for medication management",
                "Sleep hygiene education"
            ]
        }
    
    def _generate_therapy_session_note(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a therapy session note."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        session_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"MHT{random.randint(10000, 99999)}",
            "type": "therapy_session_note",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": session_date.strftime("%Y-%m-%d"),
            "session_number": random.randint(1, 20),
            "therapy_type": "Cognitive Behavioral Therapy (CBT)",
            "session_content": "Session focused on identifying and challenging negative thought patterns related to work stress.",
            "plan": [
                "Continue individual therapy sessions",
                "Practice thought records between sessions",
                "Implement stress reduction techniques daily"
            ]
        }
    
    def _generate_treatment_plan(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a mental health treatment plan."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 180 days
        plan_date = datetime.now() - timedelta(days=random.randint(0, 180))
        
        return {
            "id": f"MHTP{random.randint(10000, 99999)}",
            "type": "treatment_plan",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": plan_date.strftime("%Y-%m-%d"),
            "diagnoses": [
                {"code": "F32.1", "name": "Major Depressive Disorder, moderate"}
            ],
            "goals": [
                {
                    "goal": "Reduce depressive symptoms and improve mood",
                    "target_date": "3 months"
                }
            ],
            "interventions": [
                "Cognitive Behavioral Therapy (CBT) focusing on negative thought patterns",
                "Behavioral Activation to increase engagement in pleasurable activities",
                "Psychoeducation about depression and treatment"
            ],
            "frequency": "Weekly",
            "estimated_duration": "6 months"
        }
    
    def _generate_progress_note(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a mental health progress note."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        note_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"MHPN{random.randint(10000, 99999)}",
            "type": "progress_note",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": note_date.strftime("%Y-%m-%d"),
            "time_period": "30 days",
            "diagnoses": [
                {"code": "F32.1", "name": "Major Depressive Disorder, moderate"}
            ],
            "progress_on_goals": [
                {
                    "goal": "Reduce depressive symptoms",
                    "status": "Moderate progress",
                    "details": "Patient reports improved mood and energy levels."
                }
            ],
            "recommendations": [
                "Continue current treatment plan",
                "Maintain current therapy frequency",
                "Continue practicing mindfulness skills"
            ]
        }
    
    def _generate_psychiatric_evaluation(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a psychiatric evaluation."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 180 days
        eval_date = datetime.now() - timedelta(days=random.randint(0, 180))
        
        return {
            "id": f"MHPE{random.randint(10000, 99999)}",
            "type": "psychiatric_evaluation",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": eval_date.strftime("%Y-%m-%d"),
            "chief_complaint": "Depression with insomnia",
            "diagnoses": [
                {"code": "F32.1", "name": "Major Depressive Disorder, moderate"}
            ],
            "treatment_recommendations": [
                "Start sertraline 50 mg daily",
                "Consider trazodone 50 mg at bedtime for insomnia",
                "Continue psychotherapy",
                "Follow up in 4 weeks"
            ]
        }
