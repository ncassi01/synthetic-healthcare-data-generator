"""
Care Episodes Generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic care episodes,
which represent a sequence of related healthcare events for a member.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from src.utils.file_utils import load_config


class CareEpisode:
    """
    Represents a care episode, which is a sequence of related healthcare events.
    
    A care episode typically includes:
    - A primary condition or reason for the episode
    - A start and end date
    - A sequence of related healthcare events (encounters, procedures, etc.)
    - Outcomes and status
    - Associated providers and care team members
    """
    
    def __init__(self, member_id: str, episode_type: str, start_date: datetime,
                 end_date: Optional[datetime] = None, status: str = "active"):
        """
        Initialize a care episode.
        
        Args:
            member_id: ID of the member associated with this episode
            episode_type: Type of care episode (e.g., "acute", "chronic", "preventive")
            start_date: Start date of the episode
            end_date: End date of the episode (None if ongoing)
            status: Status of the episode (active, completed, cancelled)
        """
        self.id = f"EP{uuid.uuid4().hex[:8].upper()}"
        self.member_id = member_id
        self.episode_type = episode_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.primary_condition = None
        self.events = []
        self.providers = []
        self.care_team = []
        self.goals = []
        self.outcomes = []
        
    def add_condition(self, condition: Dict[str, Any]) -> None:
        """
        Add a primary condition to the episode.
        
        Args:
            condition: Dictionary containing condition details
        """
        self.primary_condition = condition
        
    def add_event(self, event: Dict[str, Any]) -> None:
        """
        Add a healthcare event to the episode.
        
        Args:
            event: Dictionary containing event details
        """
        self.events.append(event)
        
    def add_provider(self, provider: Dict[str, Any]) -> None:
        """
        Add a provider to the episode.
        
        Args:
            provider: Dictionary containing provider details
        """
        self.providers.append(provider)
        
    def add_care_team_member(self, member: Dict[str, Any]) -> None:
        """
        Add a care team member to the episode.
        
        Args:
            member: Dictionary containing care team member details
        """
        self.care_team.append(member)
        
    def add_goal(self, goal: Dict[str, Any]) -> None:
        """
        Add a goal to the episode.
        
        Args:
            goal: Dictionary containing goal details
        """
        self.goals.append(goal)
        
    def add_outcome(self, outcome: Dict[str, Any]) -> None:
        """
        Add an outcome to the episode.
        
        Args:
            outcome: Dictionary containing outcome details
        """
        self.outcomes.append(outcome)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the care episode to a dictionary.
        
        Returns:
            Dictionary representation of the care episode
        """
        return {
            "id": self.id,
            "member_id": self.member_id,
            "episode_type": self.episode_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "primary_condition": self.primary_condition,
            "events": self.events,
            "providers": self.providers,
            "care_team": self.care_team,
            "goals": self.goals,
            "outcomes": self.outcomes
        }


class CareEpisodesGenerator:
    """
    Generator for synthetic care episodes.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the care episodes generator.
        
        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config
        self.episode_config = config.get("care_episode_config", {})
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load reference data
        self.condition_categories = self.episode_config.get("condition_categories", [
            "Cardiovascular",
            "Respiratory",
            "Gastrointestinal",
            "Musculoskeletal",
            "Neurological",
            "Endocrine",
            "Mental Health",
            "Oncology",
            "Infectious Disease",
            "Preventive Care"
        ])
        
        self.episode_types = self.episode_config.get("episode_types", [
            "acute",
            "chronic",
            "preventive",
            "surgical",
            "maternity",
            "behavioral_health",
            "rehabilitation"
        ])
        
        self.event_types = self.episode_config.get("event_types", [
            "office_visit",
            "emergency",
            "inpatient",
            "procedure",
            "lab_test",
            "imaging",
            "medication",
            "referral",
            "follow_up"
        ])
        
        self.provider_specialties = self.episode_config.get("provider_specialties", [
            "Primary Care",
            "Cardiology",
            "Pulmonology",
            "Gastroenterology",
            "Orthopedics",
            "Neurology",
            "Endocrinology",
            "Psychiatry",
            "Oncology",
            "Infectious Disease"
        ])
        
        self.care_team_roles = self.episode_config.get("care_team_roles", [
            "Primary Care Physician",
            "Specialist",
            "Nurse",
            "Care Manager",
            "Social Worker",
            "Pharmacist",
            "Physical Therapist",
            "Nutritionist",
            "Behavioral Health Provider"
        ])
        
        self.goal_types = self.episode_config.get("goal_types", [
            "symptom_management",
            "functional_improvement",
            "disease_management",
            "preventive",
            "lifestyle",
            "medication_adherence"
        ])
        
        self.outcome_types = self.episode_config.get("outcome_types", [
            "improved",
            "stable",
            "worsened",
            "resolved",
            "complication",
            "readmission",
            "ongoing"
        ])
        
    def generate(self, count: int, members: List[Dict[str, Any]]) -> List[CareEpisode]:
        """
        Generate synthetic care episodes.
        
        Args:
            count: Number of care episodes to generate
            members: List of member dictionaries to associate episodes with
            
        Returns:
            List of generated CareEpisode objects
        """
        episodes = []
        
        # Ensure we have members to work with
        if not members:
            return episodes
        
        # Generate care episodes
        for _ in range(count):
            # Select a random member
            member = random.choice(members)
            member_id = member.get("id")
            
            # Determine episode type
            episode_type = random.choice(self.episode_types)
            
            # Determine start and end dates
            now = datetime.now()
            start_date = now - timedelta(days=random.randint(1, 365))
            
            # For completed episodes, set an end date
            status = random.choices(["active", "completed", "cancelled"], weights=[0.4, 0.5, 0.1])[0]
            end_date = None
            if status in ["completed", "cancelled"]:
                duration_days = random.randint(1, 90)
                end_date = start_date + timedelta(days=duration_days)
            
            # Create the care episode
            episode = CareEpisode(member_id, episode_type, start_date, end_date, status)
            
            # Add a primary condition
            condition_category = random.choice(self.condition_categories)
            condition = self._generate_condition(condition_category)
            episode.add_condition(condition)
            
            # Add events
            event_count = random.randint(1, 10)
            for _ in range(event_count):
                event = self._generate_event(episode.start_date, episode.end_date)
                episode.add_event(event)
            
            # Add providers
            provider_count = random.randint(1, 3)
            for _ in range(provider_count):
                provider = self._generate_provider()
                episode.add_provider(provider)
            
            # Add care team members
            care_team_count = random.randint(1, 5)
            for _ in range(care_team_count):
                care_team_member = self._generate_care_team_member()
                episode.add_care_team_member(care_team_member)
            
            # Add goals
            goal_count = random.randint(1, 3)
            for _ in range(goal_count):
                goal = self._generate_goal()
                episode.add_goal(goal)
            
            # Add outcomes if the episode is completed
            if status == "completed":
                outcome_count = random.randint(1, 3)
                for _ in range(outcome_count):
                    outcome = self._generate_outcome()
                    episode.add_outcome(outcome)
            
            episodes.append(episode)
        
        return episodes
    
    def _generate_condition(self, category: str) -> Dict[str, Any]:
        """
        Generate a synthetic condition.
        
        Args:
            category: Condition category
            
        Returns:
            Dictionary containing condition details
        """
        condition_codes = {
            "Cardiovascular": ["I10", "I25.10", "I50.9"],
            "Respiratory": ["J44.9", "J45.909", "J18.9"],
            "Gastrointestinal": ["K21.9", "K29.70", "K57.30"],
            "Musculoskeletal": ["M54.5", "M17.9", "M19.90"],
            "Neurological": ["G43.909", "G40.909", "G20"],
            "Endocrine": ["E11.9", "E03.9", "E78.5"],
            "Mental Health": ["F32.9", "F41.9", "F43.10"],
            "Oncology": ["C50.919", "C61", "C34.90"],
            "Infectious Disease": ["A41.9", "B34.9", "J09.X2"],
            "Preventive Care": ["Z00.00", "Z13.1", "Z23"]
        }
        
        condition_names = {
            "Cardiovascular": ["Hypertension", "Coronary Artery Disease", "Heart Failure"],
            "Respiratory": ["COPD", "Asthma", "Pneumonia"],
            "Gastrointestinal": ["GERD", "Gastritis", "Diverticulitis"],
            "Musculoskeletal": ["Low Back Pain", "Knee Osteoarthritis", "Osteoarthritis"],
            "Neurological": ["Migraine", "Epilepsy", "Parkinson's Disease"],
            "Endocrine": ["Type 2 Diabetes", "Hypothyroidism", "Hyperlipidemia"],
            "Mental Health": ["Depression", "Anxiety Disorder", "PTSD"],
            "Oncology": ["Breast Cancer", "Prostate Cancer", "Lung Cancer"],
            "Infectious Disease": ["Sepsis", "Viral Infection", "Influenza"],
            "Preventive Care": ["Routine Physical", "Health Screening", "Immunization"]
        }
        
        # Select a random condition code and name from the category
        index = random.randint(0, len(condition_codes[category]) - 1)
        code = condition_codes[category][index]
        name = condition_names[category][index]
        
        return {
            "category": category,
            "code": code,
            "name": name,
            "severity": random.choice(["mild", "moderate", "severe"]),
            "is_primary": True
        }
    
    def _generate_event(self, start_date: datetime, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a synthetic healthcare event.
        
        Args:
            start_date: Start date of the episode
            end_date: End date of the episode (None if ongoing)
            
        Returns:
            Dictionary containing event details
        """
        event_type = random.choice(self.event_types)
        
        # Determine event date
        if end_date:
            event_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        else:
            event_date = start_date + timedelta(days=random.randint(0, 90))
        
        return {
            "id": f"EV{uuid.uuid4().hex[:8].upper()}",
            "type": event_type,
            "date": event_date.isoformat(),
            "provider_id": f"PRV{random.randint(10000, 99999)}",
            "location": random.choice(["Clinic", "Hospital", "Emergency Room", "Telehealth"]),
            "notes": f"Patient received {event_type} service."
        }
    
    def _generate_provider(self) -> Dict[str, Any]:
        """
        Generate a synthetic provider.
        
        Returns:
            Dictionary containing provider details
        """
        specialty = random.choice(self.provider_specialties)
        
        return {
            "id": f"PRV{random.randint(10000, 99999)}",
            "name": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'])}",
            "specialty": specialty,
            "role": "attending" if random.random() < 0.7 else "consulting"
        }
    
    def _generate_care_team_member(self) -> Dict[str, Any]:
        """
        Generate a synthetic care team member.
        
        Returns:
            Dictionary containing care team member details
        """
        role = random.choice(self.care_team_roles)
        
        return {
            "id": f"CTM{random.randint(10000, 99999)}",
            "name": f"{random.choice(['John', 'Jane', 'Robert', 'Mary', 'David'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'])}",
            "role": role,
            "start_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
    
    def _generate_goal(self) -> Dict[str, Any]:
        """
        Generate a synthetic goal.
        
        Returns:
            Dictionary containing goal details
        """
        goal_type = random.choice(self.goal_types)
        
        goal_descriptions = {
            "symptom_management": "Reduce pain level to 3/10 or less",
            "functional_improvement": "Increase walking distance to 1 mile without rest",
            "disease_management": "Maintain blood pressure below 140/90",
            "preventive": "Complete all recommended screenings",
            "lifestyle": "Increase physical activity to 150 minutes per week",
            "medication_adherence": "Take all medications as prescribed"
        }
        
        return {
            "id": f"GL{uuid.uuid4().hex[:8].upper()}",
            "type": goal_type,
            "description": goal_descriptions.get(goal_type, "Improve overall health"),
            "status": random.choice(["active", "achieved", "in-progress", "cancelled"]),
            "target_date": (datetime.now() + timedelta(days=random.randint(30, 180))).isoformat()
        }
    
    def _generate_outcome(self) -> Dict[str, Any]:
        """
        Generate a synthetic outcome.
        
        Returns:
            Dictionary containing outcome details
        """
        outcome_type = random.choice(self.outcome_types)
        
        outcome_descriptions = {
            "improved": "Condition has improved with treatment",
            "stable": "Condition remains stable",
            "worsened": "Condition has worsened despite treatment",
            "resolved": "Condition has resolved completely",
            "complication": "Patient experienced a complication",
            "readmission": "Patient required readmission",
            "ongoing": "Treatment is ongoing"
        }
        
        return {
            "id": f"OC{uuid.uuid4().hex[:8].upper()}",
            "type": outcome_type,
            "description": outcome_descriptions.get(outcome_type, "Outcome not specified"),
            "date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }