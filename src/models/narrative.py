"""
Narrative content data models for the synthetic healthcare data generator.

This module defines the data models for representing narrative content such as
clinical notes, communication records, care plans, and authorization rationales.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class NoteType(Enum):
    """Type of clinical note."""
    
    PROGRESS_NOTE = "progress_note"
    CONSULTATION = "consultation"
    DISCHARGE_SUMMARY = "discharge_summary"
    HISTORY_AND_PHYSICAL = "history_and_physical"
    PROCEDURE_NOTE = "procedure_note"
    EMERGENCY_DEPARTMENT = "emergency_department"
    NURSING_NOTE = "nursing_note"
    MEDICATION_RECONCILIATION = "medication_reconciliation"
    TELEHEALTH_NOTE = "telehealth_note"


class CommunicationType(Enum):
    """Type of communication record."""
    
    PROVIDER_TO_PROVIDER = "provider_to_provider"
    PROVIDER_TO_PATIENT = "provider_to_patient"
    PATIENT_TO_PROVIDER = "patient_to_provider"
    CARE_TEAM_DISCUSSION = "care_team_discussion"
    INSURANCE_COMMUNICATION = "insurance_communication"
    PHARMACY_COMMUNICATION = "pharmacy_communication"


class CarePlanType(Enum):
    """Type of care plan."""
    
    TREATMENT_PLAN = "treatment_plan"
    CARE_MANAGEMENT = "care_management"
    DISCHARGE_PLAN = "discharge_plan"
    CHRONIC_CONDITION = "chronic_condition"
    PREVENTIVE_CARE = "preventive_care"
    BEHAVIORAL_HEALTH = "behavioral_health"
    REHABILITATION = "rehabilitation"


@dataclass
class ClinicalNote:
    """Clinical note data model."""
    
    id: str
    member_id: str
    provider_id: str
    note_type: NoteType
    date_of_service: datetime
    chief_complaint: str
    subjective: str
    objective: str
    assessment: str
    plan: str
    diagnosis_codes: List[str] = field(default_factory=list)
    procedure_codes: List[str] = field(default_factory=list)
    medication_references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert the clinical note to a dictionary for serialization."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "note_type": self.note_type.value if isinstance(self.note_type, Enum) else self.note_type,
            "date_of_service": self.date_of_service.isoformat(),
            "chief_complaint": self.chief_complaint,
            "subjective": self.subjective,
            "objective": self.objective,
            "assessment": self.assessment,
            "plan": self.plan,
            "diagnosis_codes": self.diagnosis_codes,
            "procedure_codes": self.procedure_codes,
            "medication_references": self.medication_references,
            # Add flattened fields for compatibility with web frontend
            "note_date": self.date_of_service.isoformat(),
            "note_category": self.note_type.value if isinstance(self.note_type, Enum) else self.note_type,
            "complaint": self.chief_complaint,
            "diagnoses": self.diagnosis_codes,
            "procedures": self.procedure_codes,
            "provider_name": self.provider_id,  # Add provider_name as a flattened field
            "date": self.date_of_service.isoformat()  # Add date field for compatibility
        }


@dataclass
class CommunicationRecord:
    """Communication record data model."""
    
    id: str
    communication_type: CommunicationType
    date_time: datetime
    subject: str
    content: str
    sender_id: str
    sender_type: str  # provider, patient, insurance, pharmacy
    recipient_id: str
    recipient_type: str  # provider, patient, insurance, pharmacy
    related_to: Optional[str] = None  # e.g., claim_id, authorization_id
    attachments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert the communication record to a dictionary for serialization."""
        return {
            "id": self.id,
            "communication_type": self.communication_type.value if isinstance(self.communication_type, Enum) else self.communication_type,
            "date_time": self.date_time.isoformat(),
            "subject": self.subject,
            "content": self.content,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type,
            "recipient_id": self.recipient_id,
            "recipient_type": self.recipient_type,
            "related_to": self.related_to,
            "attachments": self.attachments,
            # Add flattened fields for compatibility with web frontend
            "comm_date": self.date_time.isoformat(),
            "comm_type": self.communication_type.value if isinstance(self.communication_type, Enum) else self.communication_type,
            "message_subject": self.subject,
            "message_content": self.content,
            "from_id": self.sender_id,
            "from_type": self.sender_type,
            "to_id": self.recipient_id,
            "to_type": self.recipient_type,
            "sender": f"{self.sender_type}: {self.sender_id}",  # Use sender as the field name
            "recipient": f"{self.recipient_type}: {self.recipient_id}",  # Use recipient as the field name
            "member_id": self.sender_id if self.sender_type == "patient" else (self.recipient_id if self.recipient_type == "patient" else None),  # Extract member_id
            "attachments": self.attachments,  # Use attachments as the field name
            "has_attachments": len(self.attachments) > 0,  # Boolean flag for attachments
            "date": self.date_time.isoformat()  # Add date field for compatibility
        }


@dataclass
class CarePlanGoal:
    """Goal within a care plan."""
    
    description: str
    target_date: datetime
    status: str  # active, completed, cancelled
    priority: str  # high, medium, low
    
    def to_dict(self) -> Dict:
        """Convert the care plan goal to a dictionary for serialization."""
        return {
            "description": self.description,
            "target_date": self.target_date.isoformat(),
            "status": self.status,
            "priority": self.priority
        }


@dataclass
class CarePlanIntervention:
    """Intervention within a care plan."""
    
    description: str
    type: str  # medication, procedure, referral, education, monitoring
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert the care plan intervention to a dictionary for serialization."""
        return {
            "description": self.description,
            "type": self.type,
            "frequency": self.frequency,
            "duration": self.duration,
            "instructions": self.instructions
        }


@dataclass
class CarePlan:
    """Care plan data model."""
    
    id: str
    member_id: str
    provider_id: str
    care_plan_type: CarePlanType
    title: str
    description: str
    created_date: datetime
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, completed, cancelled
    goals: List[CarePlanGoal] = field(default_factory=list)
    interventions: List[CarePlanIntervention] = field(default_factory=list)
    conditions_addressed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert the care plan to a dictionary for serialization."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "care_plan_type": self.care_plan_type.value if isinstance(self.care_plan_type, Enum) else self.care_plan_type,
            "title": self.title,
            "description": self.description,
            "created_date": self.created_date.isoformat(),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "goals": [goal.to_dict() for goal in self.goals],
            "interventions": [intervention.to_dict() for intervention in self.interventions],
            "conditions_addressed": self.conditions_addressed,
            # Add flattened fields for compatibility with web frontend
            "plan_type": self.care_plan_type.value if isinstance(self.care_plan_type, Enum) else self.care_plan_type,
            "plan_title": self.title,
            "plan_description": self.description,
            "date_created": self.created_date.isoformat(),
            "date_start": self.start_date.isoformat(),
            "date_end": self.end_date.isoformat() if self.end_date else None,
            "plan_status": self.status,
            "conditions": self.conditions_addressed,
            "condition": self.conditions_addressed[0] if self.conditions_addressed else None,  # Primary condition
            "provider_name": self.provider_id,  # Use provider_name as the flattened field name
            "review_date": self.start_date.isoformat()  # Using start_date as review date
        }


@dataclass
class AuthorizationRationale:
    """Authorization rationale data model."""
    
    id: str
    authorization_id: str
    member_id: str
    provider_id: str
    date_created: datetime
    clinical_summary: str
    medical_necessity: str
    evidence_references: List[str] = field(default_factory=list)
    guidelines_referenced: List[str] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert the authorization rationale to a dictionary for serialization."""
        return {
            "id": self.id,
            "authorization_id": self.authorization_id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "date_created": self.date_created.isoformat(),
            "clinical_summary": self.clinical_summary,
            "medical_necessity": self.medical_necessity,
            "evidence_references": self.evidence_references,
            "guidelines_referenced": self.guidelines_referenced,
            "alternatives_considered": self.alternatives_considered,
            # Add flattened fields for compatibility with web frontend
            "auth_id": self.authorization_id,
            "creation_date": self.date_created.isoformat(),
            "summary": self.clinical_summary,
            "necessity": self.medical_necessity,
            "evidence": self.evidence_references,
            "guidelines": self.guidelines_referenced,
            "alternatives": self.alternatives_considered
        }