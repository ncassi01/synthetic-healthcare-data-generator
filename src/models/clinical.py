"""
Clinical Domain Models

This module contains the data models for the Clinical domain, including encounters,
participants, locations, diagnoses, procedures, notes, services, assessments,
medications, and transitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class EncounterType(str, Enum):
    """Types of clinical encounters"""
    INPATIENT = "Inpatient"
    AMBULATORY = "Ambulatory"
    EMERGENCY = "Emergency"
    OBSERVATION = "Observation"
    VIRTUAL = "Virtual"
    HOME_HEALTH = "Home Health"


class EncounterStatus(str, Enum):
    """Status of clinical encounters"""
    PLANNED = "Planned"
    ARRIVED = "Arrived"
    IN_PROGRESS = "In-Progress"
    ON_LEAVE = "On-Leave"
    FINISHED = "Finished"
    CANCELLED = "Cancelled"


class EncounterClass(str, Enum):
    """Classification of clinical encounters"""
    EMERGENCY = "Emergency"
    INPATIENT = "Inpatient"
    OUTPATIENT = "Outpatient"
    AMBULATORY = "Ambulatory"
    VIRTUAL = "Virtual"
    HOME = "Home"
    FIELD = "Field"
    OTHER = "Other"


class EncounterPriority(str, Enum):
    """Priority of clinical encounters"""
    ROUTINE = "Routine"
    URGENT = "Urgent"
    EMERGENCY = "Emergency"
    ELECTIVE = "Elective"


class AdmissionType(str, Enum):
    """Types of admissions for inpatient encounters"""
    ELECTIVE = "Elective"
    EMERGENCY = "Emergency"
    URGENT = "Urgent"
    NEWBORN = "Newborn"
    TRAUMA = "Trauma"
    OTHER = "Other"


class DischargeDisposition(str, Enum):
    """Disposition at discharge for inpatient encounters"""
    HOME = "Home"
    SNF = "SNF"
    REHAB = "Rehab"
    LTAC = "LTAC"
    EXPIRED = "Expired"
    AMA = "AMA"
    TRANSFER = "Transfer"
    OTHER = "Other"


class ServiceType(str, Enum):
    """Types of services provided during encounters"""
    MEDICAL = "Medical"
    SURGICAL = "Surgical"
    PSYCHIATRIC = "Psychiatric"
    OBSTETRIC = "Obstetric"
    PEDIATRIC = "Pediatric"
    REHABILITATION = "Rehabilitation"
    ONCOLOGY = "Oncology"
    OTHER = "Other"


class ParticipantType(str, Enum):
    """Types of participants in clinical encounters"""
    PATIENT = "Patient"
    PROVIDER = "Provider"
    CAREGIVER = "Caregiver"
    FAMILY = "Family"
    INTERPRETER = "Interpreter"
    OTHER = "Other"


class ProviderRole(str, Enum):
    """Roles of providers in clinical encounters"""
    ATTENDING = "Attending"
    CONSULTING = "Consulting"
    ADMITTING = "Admitting"
    REFERRING = "Referring"
    PCP = "PCP"
    SURGEON = "Surgeon"
    ANESTHESIOLOGIST = "Anesthesiologist"
    RADIOLOGIST = "Radiologist"
    PATHOLOGIST = "Pathologist"
    NURSE = "Nurse"
    THERAPIST = "Therapist"
    OTHER = "Other"


class LocationType(str, Enum):
    """Types of locations for clinical encounters"""
    ER = "ER"
    ICU = "ICU"
    WARD = "Ward"
    CLINIC = "Clinic"
    OPERATING_ROOM = "Operating Room"
    RADIOLOGY = "Radiology"
    LABORATORY = "Laboratory"
    PHARMACY = "Pharmacy"
    OTHER = "Other"


class LocationStatus(str, Enum):
    """Status of locations for clinical encounters"""
    PLANNED = "Planned"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class DiagnosisType(str, Enum):
    """Types of diagnoses for clinical encounters"""
    ADMITTING = "Admitting"
    DISCHARGE = "Discharge"
    PRINCIPAL = "Principal"
    SECONDARY = "Secondary"
    PRE_OP = "Pre-Op"
    POST_OP = "Post-Op"
    OTHER = "Other"


class ProcedureStatus(str, Enum):
    """Status of procedures for clinical encounters"""
    PLANNED = "Planned"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class NoteType(str, Enum):
    """Types of clinical notes"""
    PROGRESS_NOTE = "Progress Note"
    H_AND_P = "H&P"
    DISCHARGE_SUMMARY = "Discharge Summary"
    OPERATIVE_REPORT = "Operative Report"
    CONSULTATION = "Consultation"
    PROCEDURE_NOTE = "Procedure Note"
    NURSING_NOTE = "Nursing Note"
    OTHER = "Other"


class NoteStatus(str, Enum):
    """Status of clinical notes"""
    DRAFT = "Draft"
    FINAL = "Final"
    AMENDED = "Amended"


class ServiceStatus(str, Enum):
    """Status of services for clinical encounters"""
    ORDERED = "Ordered"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class AssessmentType(str, Enum):
    """Types of assessments for clinical encounters"""
    VITAL_SIGNS = "Vital Signs"
    PAIN = "Pain"
    FUNCTIONAL_STATUS = "Functional Status"
    MENTAL_STATUS = "Mental Status"
    RISK_ASSESSMENT = "Risk Assessment"
    OTHER = "Other"


class MedicationRoute(str, Enum):
    """Routes of medication administration"""
    ORAL = "Oral"
    IV = "IV"
    IM = "IM"
    SC = "SC"
    TOPICAL = "Topical"
    INHALED = "Inhaled"
    OTHER = "Other"


class MedicationStatus(str, Enum):
    """Status of medications for clinical encounters"""
    SCHEDULED = "Scheduled"
    ADMINISTERED = "Administered"
    HELD = "Held"
    CANCELLED = "Cancelled"


class TransitionType(str, Enum):
    """Types of transitions between encounters"""
    ADMISSION = "Admission"
    TRANSFER = "Transfer"
    DISCHARGE = "Discharge"
    REFERRAL = "Referral"


class ValidationSeverity(str, Enum):
    """Severity levels for validation errors"""
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    code: str
    message: str
    severity: ValidationSeverity
    entity_id: str


@dataclass
class ClinicalEncounter:
    """
    Core entity representing a healthcare interaction between a patient and provider(s).
    """
    id: str
    type: Union[EncounterType, str]
    status: Union[EncounterStatus, str]
    class_type: Union[EncounterClass, str]
    priority: Optional[Union[EncounterPriority, str]] = None
    start_datetime: datetime = field(default_factory=datetime.now)
    end_datetime: Optional[datetime] = None
    length_of_stay: Optional[int] = None
    admission_type: Optional[Union[AdmissionType, str]] = None
    discharge_disposition: Optional[Union[DischargeDisposition, str]] = None
    readmission: bool = False
    chief_complaint: Optional[str] = None
    reason_code: Optional[str] = None
    service_type: Optional[Union[ServiceType, str]] = None
    account_number: Optional[str] = None
    visit_number: Optional[str] = None
    episode_of_care_id: Optional[str] = None
    
    # Relationships (populated after creation)
    participants: List["EncounterParticipant"] = field(default_factory=list)
    locations: List["EncounterLocation"] = field(default_factory=list)
    diagnoses: List["EncounterDiagnosis"] = field(default_factory=list)
    procedures: List["EncounterProcedure"] = field(default_factory=list)
    notes: List["ClinicalNote"] = field(default_factory=list)
    services: List["EncounterService"] = field(default_factory=list)
    assessments: List["EncounterAssessment"] = field(default_factory=list)
    medications: List["EncounterMedication"] = field(default_factory=list)
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.type, str):
            self.type = EncounterType(self.type)
        if isinstance(self.status, str):
            self.status = EncounterStatus(self.status)
        if isinstance(self.class_type, str):
            self.class_type = EncounterClass(self.class_type)
        if self.priority and isinstance(self.priority, str):
            self.priority = EncounterPriority(self.priority)
        if self.admission_type and isinstance(self.admission_type, str):
            self.admission_type = AdmissionType(self.admission_type)
        if self.discharge_disposition and isinstance(self.discharge_disposition, str):
            self.discharge_disposition = DischargeDisposition(self.discharge_disposition)
        if self.service_type and isinstance(self.service_type, str):
            self.service_type = ServiceType(self.service_type)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the encounter and return any validation errors"""
        results = []
        
        # ENC-001: Start date must be before end date
        if self.end_datetime and self.start_datetime > self.end_datetime:
            results.append(ValidationResult(
                code="ENC-001",
                message="Start date must be before end date",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # ENC-002: Inpatient encounters must have length of stay > 0
        if self.type == EncounterType.INPATIENT and (not self.length_of_stay or self.length_of_stay <= 0):
            results.append(ValidationResult(
                code="ENC-002",
                message="Inpatient encounters must have length of stay > 0",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # ENC-003: Discharge disposition required for completed inpatient encounters
        if (self.type == EncounterType.INPATIENT and
            self.status == EncounterStatus.FINISHED and
            not self.discharge_disposition):
            results.append(ValidationResult(
                code="ENC-003",
                message="Discharge disposition required for completed inpatient encounters",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # ENC-004: At least one patient participant required
        patient_participants = [p for p in self.participants if p.participant_type == ParticipantType.PATIENT]
        if not patient_participants:
            results.append(ValidationResult(
                code="ENC-004",
                message="At least one patient participant required",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # ENC-005: At least one provider participant required for non-cancelled encounters
        if self.status != EncounterStatus.CANCELLED:
            provider_participants = [p for p in self.participants if p.participant_type == ParticipantType.PROVIDER]
            if not provider_participants:
                results.append(ValidationResult(
                    code="ENC-005",
                    message="At least one provider participant required for non-cancelled encounters",
                    severity=ValidationSeverity.ERROR,
                    entity_id=self.id
                ))
        
        # ENC-006: Chief complaint required for emergency encounters
        if self.type == EncounterType.EMERGENCY and not self.chief_complaint:
            results.append(ValidationResult(
                code="ENC-006",
                message="Chief complaint required for emergency encounters",
                severity=ValidationSeverity.WARNING,
                entity_id=self.id
            ))
        
        # Additional validation rules would be implemented here
        
        return results
    
    def get_patient_id(self) -> Optional[str]:
        """Get the ID of the primary patient participant"""
        for participant in self.participants:
            if (participant.participant_type == ParticipantType.PATIENT and
                participant.primary):
                return participant.participant_id
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the encounter to a dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "class_type": self.class_type.value,
            "priority": self.priority.value if self.priority else None,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "length_of_stay": self.length_of_stay,
            "admission_type": self.admission_type.value if self.admission_type else None,
            "discharge_disposition": self.discharge_disposition.value if self.discharge_disposition else None,
            "readmission": self.readmission,
            "chief_complaint": self.chief_complaint,
            "reason_code": self.reason_code,
            "service_type": self.service_type.value if self.service_type else None,
            "account_number": self.account_number,
            "visit_number": self.visit_number,
            "episode_of_care_id": self.episode_of_care_id,
            "participants": [p.to_dict() for p in self.participants],
            "locations": [l.to_dict() for l in self.locations],
            "diagnoses": [d.to_dict() for d in self.diagnoses],
            "procedures": [p.to_dict() for p in self.procedures],
            "notes": [n.to_dict() for n in self.notes],
            "services": [s.to_dict() for s in self.services],
            "assessments": [a.to_dict() for a in self.assessments],
            "medications": [m.to_dict() for m in self.medications]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClinicalEncounter":
        """Create an encounter from a dictionary"""
        # Handle nested objects later
        encounter_data = data.copy()
        for nested_field in ["participants", "locations", "diagnoses", "procedures",
                            "notes", "services", "assessments", "medications"]:
            if nested_field in encounter_data:
                del encounter_data[nested_field]
        
        # Convert ISO datetime strings to datetime objects
        if "start_datetime" in encounter_data and encounter_data["start_datetime"]:
            encounter_data["start_datetime"] = datetime.fromisoformat(encounter_data["start_datetime"].replace("Z", "+00:00"))
        if "end_datetime" in encounter_data and encounter_data["end_datetime"]:
            encounter_data["end_datetime"] = datetime.fromisoformat(encounter_data["end_datetime"].replace("Z", "+00:00"))
        
        encounter = cls(**encounter_data)
        
        # Add nested objects if present
        if "participants" in data:
            encounter.participants = [EncounterParticipant.from_dict(p) for p in data["participants"]]
        if "locations" in data:
            encounter.locations = [EncounterLocation.from_dict(l) for l in data["locations"]]
        if "diagnoses" in data:
            encounter.diagnoses = [EncounterDiagnosis.from_dict(d) for d in data["diagnoses"]]
        if "procedures" in data:
            encounter.procedures = [EncounterProcedure.from_dict(p) for p in data["procedures"]]
        if "notes" in data:
            encounter.notes = [ClinicalNote.from_dict(n) for n in data["notes"]]
        if "services" in data:
            encounter.services = [EncounterService.from_dict(s) for s in data["services"]]
        if "assessments" in data:
            encounter.assessments = [EncounterAssessment.from_dict(a) for a in data["assessments"]]
        if "medications" in data:
            encounter.medications = [EncounterMedication.from_dict(m) for m in data["medications"]]
        
        return encounter


@dataclass
class EncounterParticipant:
    """
    Represents individuals involved in the encounter.
    """
    id: str
    encounter_id: str
    participant_type: Union[ParticipantType, str]
    participant_id: str
    role: Optional[Union[ProviderRole, str]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    primary: bool = False
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.participant_type, str):
            self.participant_type = ParticipantType(self.participant_type)
        if self.role and isinstance(self.role, str):
            self.role = ProviderRole(self.role)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the participant and return any validation errors"""
        results = []
        
        # PART-008: Participant start date must be before end date
        if self.start_datetime and self.end_datetime and self.start_datetime > self.end_datetime:
            results.append(ValidationResult(
                code="PART-008",
                message="Participant start date must be before end date",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # Additional validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the participant to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "participant_type": self.participant_type.value,
            "participant_id": self.participant_id,
            "role": self.role.value if self.role else None,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "primary": self.primary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterParticipant":
        """Create a participant from a dictionary"""
        participant_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "start_datetime" in participant_data and participant_data["start_datetime"]:
            participant_data["start_datetime"] = datetime.fromisoformat(participant_data["start_datetime"].replace("Z", "+00:00"))
        if "end_datetime" in participant_data and participant_data["end_datetime"]:
            participant_data["end_datetime"] = datetime.fromisoformat(participant_data["end_datetime"].replace("Z", "+00:00"))
        
        return cls(**participant_data)


@dataclass
class EncounterLocation:
    """
    Tracks where the encounter took place, including transitions.
    """
    id: str
    encounter_id: str
    facility_id: Optional[str] = None
    department_id: Optional[str] = None
    location_type: Union[LocationType, str] = LocationType.WARD
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: Union[LocationStatus, str] = LocationStatus.ACTIVE
    bed_id: Optional[str] = None
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.location_type, str):
            self.location_type = LocationType(self.location_type)
        if isinstance(self.status, str):
            self.status = LocationStatus(self.status)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the location and return any validation errors"""
        results = []
        
        # LOC-006: Location start date must be before end date
        if self.start_datetime and self.end_datetime and self.start_datetime > self.end_datetime:
            results.append(ValidationResult(
                code="LOC-006",
                message="Location start date must be before end date",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # Additional validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the location to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "facility_id": self.facility_id,
            "department_id": self.department_id,
            "location_type": self.location_type.value,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "status": self.status.value,
            "bed_id": self.bed_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterLocation":
        """Create a location from a dictionary"""
        location_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "start_datetime" in location_data and location_data["start_datetime"]:
            location_data["start_datetime"] = datetime.fromisoformat(location_data["start_datetime"].replace("Z", "+00:00"))
        if "end_datetime" in location_data and location_data["end_datetime"]:
            location_data["end_datetime"] = datetime.fromisoformat(location_data["end_datetime"].replace("Z", "+00:00"))
        
        return cls(**location_data)


@dataclass
class EncounterDiagnosis:
    """
    Diagnoses addressed during the encounter.
    """
    id: str
    encounter_id: str
    diagnosis_code: str
    diagnosis_description: str
    condition_id: Optional[str] = None
    diagnosis_type: Union[DiagnosisType, str] = DiagnosisType.SECONDARY
    present_on_admission: bool = False
    rank: Optional[int] = None
    provider_id: Optional[str] = None
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.diagnosis_type, str):
            self.diagnosis_type = DiagnosisType(self.diagnosis_type)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the diagnosis and return any validation errors"""
        results = []
        
        # Validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the diagnosis to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "diagnosis_code": self.diagnosis_code,
            "diagnosis_description": self.diagnosis_description,
            "condition_id": self.condition_id,
            "diagnosis_type": self.diagnosis_type.value,
            "present_on_admission": self.present_on_admission,
            "rank": self.rank,
            "provider_id": self.provider_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterDiagnosis":
        """Create a diagnosis from a dictionary"""
        return cls(**data)


@dataclass
class EncounterProcedure:
    """
    Procedures performed during the encounter.
    """
    id: str
    encounter_id: str
    procedure_code: str
    procedure_description: str
    procedure_id: Optional[str] = None
    datetime: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    provider_id: Optional[str] = None
    location_id: Optional[str] = None
    status: Union[ProcedureStatus, str] = ProcedureStatus.COMPLETED
    primary: bool = False
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.status, str):
            self.status = ProcedureStatus(self.status)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the procedure and return any validation errors"""
        results = []
        
        # Validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the procedure to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "procedure_code": self.procedure_code,
            "procedure_description": self.procedure_description,
            "procedure_id": self.procedure_id,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "duration_minutes": self.duration_minutes,
            "provider_id": self.provider_id,
            "location_id": self.location_id,
            "status": self.status.value,
            "primary": self.primary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterProcedure":
        """Create a procedure from a dictionary"""
        procedure_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "datetime" in procedure_data and procedure_data["datetime"]:
            procedure_data["datetime"] = datetime.fromisoformat(procedure_data["datetime"].replace("Z", "+00:00"))
        
        return cls(**procedure_data)


@dataclass
class ClinicalNote:
    """
    Documentation created during the encounter.
    """
    id: str
    encounter_id: str
    note_type: Union[NoteType, str]
    author_id: str
    datetime: datetime = field(default_factory=datetime.now)
    content: str = ""
    status: Union[NoteStatus, str] = NoteStatus.DRAFT
    signed: bool = False
    signed_datetime: Optional[datetime] = None
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.note_type, str):
            self.note_type = NoteType(self.note_type)
        if isinstance(self.status, str):
            self.status = NoteStatus(self.status)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the note and return any validation errors"""
        results = []
        
        # NOTE-001: Note content required
        if not self.content:
            results.append(ValidationResult(
                code="NOTE-001",
                message="Note content required",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # NOTE-005: Signed notes must have signed datetime
        if self.signed and not self.signed_datetime:
            results.append(ValidationResult(
                code="NOTE-005",
                message="Signed notes must have signed datetime",
                severity=ValidationSeverity.ERROR,
                entity_id=self.id
            ))
        
        # Additional validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the note to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "note_type": self.note_type.value,
            "author_id": self.author_id,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "content": self.content,
            "status": self.status.value,
            "signed": self.signed,
            "signed_datetime": self.signed_datetime.isoformat() if self.signed_datetime else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClinicalNote":
        """Create a note from a dictionary"""
        note_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "datetime" in note_data and note_data["datetime"]:
            note_data["datetime"] = datetime.fromisoformat(note_data["datetime"].replace("Z", "+00:00"))
        if "signed_datetime" in note_data and note_data["signed_datetime"]:
            note_data["signed_datetime"] = datetime.fromisoformat(note_data["signed_datetime"].replace("Z", "+00:00"))
        
        return cls(**note_data)


@dataclass
class EncounterService:
    """
    Services provided during the encounter.
    """
    id: str
    encounter_id: str
    service_code: str
    service_description: str
    service_id: Optional[str] = None
    provider_id: Optional[str] = None
    datetime: Optional[datetime] = None
    quantity: int = 1
    status: Union[ServiceStatus, str] = ServiceStatus.COMPLETED
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.status, str):
            self.status = ServiceStatus(self.status)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the service and return any validation errors"""
        results = []
        
        # Validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the service to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "service_code": self.service_code,
            "service_description": self.service_description,
            "service_id": self.service_id,
            "provider_id": self.provider_id,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "quantity": self.quantity,
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterService":
        """Create a service from a dictionary"""
        service_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "datetime" in service_data and service_data["datetime"]:
            service_data["datetime"] = datetime.fromisoformat(service_data["datetime"].replace("Z", "+00:00"))
        
        return cls(**service_data)


@dataclass
class EncounterAssessment:
    """
    Assessments performed during the encounter.
    """
    id: str
    encounter_id: str
    assessment_type: Union[AssessmentType, str]
    datetime: datetime = field(default_factory=datetime.now)
    provider_id: Optional[str] = None
    result: Dict[str, Any] = field(default_factory=dict)
    interpretation: Optional[str] = None
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.assessment_type, str):
            self.assessment_type = AssessmentType(self.assessment_type)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the assessment and return any validation errors"""
        results = []
        
        # Validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the assessment to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "assessment_type": self.assessment_type.value,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "provider_id": self.provider_id,
            "result": self.result,
            "interpretation": self.interpretation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterAssessment":
        """Create an assessment from a dictionary"""
        assessment_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "datetime" in assessment_data and assessment_data["datetime"]:
            assessment_data["datetime"] = datetime.fromisoformat(assessment_data["datetime"].replace("Z", "+00:00"))
        
        return cls(**assessment_data)


@dataclass
class EncounterMedication:
    """
    Medications administered during the encounter.
    """
    id: str
    encounter_id: str
    medication_id: str
    order_id: Optional[str] = None
    datetime: Optional[datetime] = None
    dose: Optional[str] = None
    route: Union[MedicationRoute, str] = MedicationRoute.ORAL
    provider_id: Optional[str] = None
    status: Union[MedicationStatus, str] = MedicationStatus.ADMINISTERED
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.route, str):
            self.route = MedicationRoute(self.route)
        if isinstance(self.status, str):
            self.status = MedicationStatus(self.status)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the medication and return any validation errors"""
        results = []
        
        # Validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the medication to a dictionary"""
        return {
            "id": self.id,
            "encounter_id": self.encounter_id,
            "medication_id": self.medication_id,
            "order_id": self.order_id,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "dose": self.dose,
            "route": self.route.value,
            "provider_id": self.provider_id,
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterMedication":
        """Create a medication from a dictionary"""
        medication_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "datetime" in medication_data and medication_data["datetime"]:
            medication_data["datetime"] = datetime.fromisoformat(medication_data["datetime"].replace("Z", "+00:00"))
        
        return cls(**medication_data)


@dataclass
class EncounterTransition:
    """
    Transitions between encounters (e.g., ER to inpatient).
    """
    id: str
    from_encounter_id: str
    to_encounter_id: str
    transition_type: Union[TransitionType, str]
    datetime: datetime = field(default_factory=datetime.now)
    reason: Optional[str] = None
    authorizing_provider_id: Optional[str] = None
    
    def __post_init__(self):
        """Convert string enums to enum objects if needed"""
        if isinstance(self.transition_type, str):
            self.transition_type = TransitionType(self.transition_type)
    
    def validate(self) -> List[ValidationResult]:
        """Validate the transition and return any validation errors"""
        results = []
        
        # Validation rules would be implemented here
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the transition to a dictionary"""
        return {
            "id": self.id,
            "from_encounter_id": self.from_encounter_id,
            "to_encounter_id": self.to_encounter_id,
            "transition_type": self.transition_type.value,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "reason": self.reason,
            "authorizing_provider_id": self.authorizing_provider_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncounterTransition":
        """Create a transition from a dictionary"""
        transition_data = data.copy()
        
        # Convert ISO datetime strings to datetime objects
        if "datetime" in transition_data and transition_data["datetime"]:
            transition_data["datetime"] = datetime.fromisoformat(transition_data["datetime"].replace("Z", "+00:00"))
        
        return cls(**transition_data)
