"""
Telehealth documentation generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic telehealth-related documentation
such as virtual visit notes, remote monitoring data, and telehealth summaries.
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


class TelehealthDocumentationGenerator(BaseGenerator):
    """Generator for synthetic telehealth documentation."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the telehealth documentation generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract configuration
        self.telehealth_config = config.get('telehealth_config', {})
        
    def generate(self, count: int, member_ids: List[str] = None, provider_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic telehealth documentation.
        
        Args:
            count: Number of documents to generate.
            member_ids: Optional list of member IDs to associate with the documents.
                If not provided, random IDs will be generated.
            provider_ids: Optional list of provider IDs to use as authors.
                If not provided, random IDs will be generated.
                
        Returns:
            List of generated telehealth documentation entries.
        """
        self.logger.info(f"Generating {count} telehealth documents")
        
        if member_ids is None:
            # Generate random member IDs if not provided
            member_ids = [f"MEM{i:08d}" for i in range(count)]
        
        if provider_ids is None:
            # Generate random provider IDs if not provided
            provider_ids = [f"PRV{i:08d}" for i in range(20)]  # Generate 20 providers
        
        # If fewer member IDs than count, repeat member IDs
        if len(member_ids) < count:
            member_ids = (member_ids * (count // len(member_ids) + 1))[:count]
        
        documents = []
        
        # Generate different types of telehealth documents
        document_types = [
            'virtual_visit_note', 
            'remote_monitoring_summary', 
            'telehealth_consultation',
            'virtual_follow_up',
            'telehealth_triage'
        ]
        
        for i in range(count):
            document_type = random.choice(document_types)
            
            if document_type == 'virtual_visit_note':
                document = self._generate_virtual_visit_note(member_ids[i], provider_ids)
            elif document_type == 'remote_monitoring_summary':
                document = self._generate_remote_monitoring_summary(member_ids[i], provider_ids)
            elif document_type == 'telehealth_consultation':
                document = self._generate_telehealth_consultation(member_ids[i], provider_ids)
            elif document_type == 'virtual_follow_up':
                document = self._generate_virtual_follow_up(member_ids[i], provider_ids)
            elif document_type == 'telehealth_triage':
                document = self._generate_telehealth_triage(member_ids[i], provider_ids)
            
            documents.append(document)
            
        self.logger.info(f"Generated {len(documents)} telehealth documents")
        return documents
    
    def _generate_virtual_visit_note(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a virtual visit note."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        visit_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"TVN{random.randint(10000, 99999)}",
            "type": "virtual_visit_note",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": visit_date.strftime("%Y-%m-%d"),
            "time": visit_date.strftime("%H:%M"),
            "duration_minutes": random.choice([15, 20, 30, 45, 60]),
            "visit_reason": "Follow-up for chronic condition",
            "chief_complaint": "Hypertension management",
            "assessment": [
                {
                    "diagnosis": "Essential Hypertension",
                    "status": "Well-controlled",
                    "plan": "Continue current management"
                }
            ],
            "plan": {
                "medications": [
                    {
                        "action": "Continue",
                        "medication": "lisinopril",
                        "details": "10 mg daily"
                    }
                ],
                "testing": [],
                "referrals": [],
                "patient_education": ["Medication adherence importance"],
                "follow_up": "3 months"
            },
            "technical_details": {
                "platform": "Zoom for Healthcare",
                "connection_quality": "Good",
                "patient_location": "Home",
                "privacy_confirmed": True
            }
        }
    
    def _generate_remote_monitoring_summary(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a remote monitoring summary."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        summary_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"RMS{random.randint(10000, 99999)}",
            "type": "remote_monitoring_summary",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": summary_date.strftime("%Y-%m-%d"),
            "monitoring_type": "Blood Pressure",
            "monitoring_period": {
                "start_date": (summary_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end_date": summary_date.strftime("%Y-%m-%d"),
                "duration_days": 30
            },
            "monitoring_data": {
                "readings": [
                    {
                        "date": (summary_date - timedelta(days=25)).strftime("%Y-%m-%d"),
                        "time": "08:00",
                        "value": "135/85",
                        "heart_rate": 72
                    },
                    {
                        "date": (summary_date - timedelta(days=18)).strftime("%Y-%m-%d"),
                        "time": "08:15",
                        "value": "130/82",
                        "heart_rate": 70
                    },
                    {
                        "date": (summary_date - timedelta(days=10)).strftime("%Y-%m-%d"),
                        "time": "08:30",
                        "value": "128/80",
                        "heart_rate": 68
                    }
                ],
                "average": "131/82",
                "min": "128/80",
                "max": "135/85"
            },
            "assessment": "Blood pressure readings show good control with current medication regimen.",
            "recommendations": [
                "Continue current medication regimen",
                "Maintain home blood pressure monitoring",
                "Follow up in 3 months"
            ]
        }
    
    def _generate_telehealth_consultation(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a telehealth consultation note."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        consult_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"THC{random.randint(10000, 99999)}",
            "type": "telehealth_consultation",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": consult_date.strftime("%Y-%m-%d"),
            "time": consult_date.strftime("%H:%M"),
            "duration_minutes": 30,
            "consultation_reason": "Cardiology consultation",
            "clinical_question": "Evaluation of heart murmur and palpitations",
            "assessment": "Patient presents with new onset palpitations and a grade 2/6 systolic murmur. ECG shows sinus rhythm with occasional PACs.",
            "recommendations": [
                "Echocardiogram to evaluate murmur",
                "24-hour Holter monitor",
                "Avoid caffeine and stimulants",
                "Follow up after testing completed"
            ],
            "technical_details": {
                "platform": "Zoom for Healthcare",
                "connection_quality": "Good"
            }
        }
    
    def _generate_virtual_follow_up(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a virtual follow-up note."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        followup_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"VFU{random.randint(10000, 99999)}",
            "type": "virtual_follow_up",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": followup_date.strftime("%Y-%m-%d"),
            "time": followup_date.strftime("%H:%M"),
            "duration_minutes": 15,
            "previous_visit_date": (followup_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            "followup_reason": "Diabetes management",
            "current_status": "Patient reports improved blood glucose readings with dietary changes.",
            "assessment": "Type 2 Diabetes, improving control with current management",
            "plan": {
                "medications": [
                    {
                        "action": "Continue",
                        "medication": "metformin",
                        "details": "1000 mg twice daily"
                    }
                ],
                "testing": [
                    {
                        "test": "Hemoglobin A1c",
                        "timeframe": "Within 3 months"
                    }
                ],
                "follow_up": "3 months"
            }
        }
    
    def _generate_telehealth_triage(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a telehealth triage note."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        triage_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"TTN{random.randint(10000, 99999)}",
            "type": "telehealth_triage",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": triage_date.strftime("%Y-%m-%d"),
            "time": triage_date.strftime("%H:%M"),
            "duration_minutes": 10,
            "presenting_concern": "Fever and cough for 3 days",
            "symptom_assessment": "Patient reports fever up to 101°F, dry cough, mild shortness of breath, and fatigue. No known COVID-19 exposure.",
            "triage_assessment": "Possible upper respiratory infection or COVID-19",
            "disposition": "Virtual Visit Scheduled",
            "recommendations": [
                "Schedule telehealth visit within 24 hours",
                "COVID-19 testing recommended",
                "Rest, fluids, and acetaminophen for fever",
                "Call back or seek emergency care if symptoms worsen"
            ]
        }
