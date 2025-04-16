"""
Insurance data models for the synthetic healthcare data generator.

This module defines the data models for representing insurance-related entities
such as claims, prior authorizations, explanation of benefits, and plan coverage.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class ClaimStatus(Enum):
    """Status of a healthcare claim."""
    
    SUBMITTED = "submitted"
    PENDING = "pending"
    IN_PROCESS = "in_process"
    DENIED = "denied"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    APPEALED = "appealed"


class AuthorizationStatus(Enum):
    """Status of a prior authorization request."""
    
    SUBMITTED = "submitted"
    PENDING = "pending"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"
    APPROVED = "approved"
    DENIED = "denied"
    APPEALED = "appealed"


class ServiceType(Enum):
    """Type of healthcare service."""
    
    OFFICE_VISIT = "office_visit"
    PREVENTIVE_CARE = "preventive_care"
    SPECIALIST_VISIT = "specialist_visit"
    EMERGENCY = "emergency"
    URGENT_CARE = "urgent_care"
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    DIAGNOSTIC = "diagnostic"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PHARMACY = "pharmacy"
    THERAPY = "therapy"
    MENTAL_HEALTH = "mental_health"
    DENTAL = "dental"
    VISION = "vision"


@dataclass
class ServiceLine:
    """Service line item for claims and authorizations."""
    
    service_code: str  # CPT, HCPCS, or other service code
    description: str
    service_type: ServiceType
    quantity: int = 1
    unit_price: float = 0.0
    total_price: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert the service line to a dictionary for serialization."""
        return {
            "service_code": self.service_code,
            "description": self.description,
            "service_type": self.service_type.value if isinstance(self.service_type, Enum) else self.service_type,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price
        }


@dataclass
class Claim:
    """Healthcare insurance claim."""
    
    id: str
    member_id: str
    provider_id: str
    date_of_service: date
    date_submitted: date
    status: ClaimStatus
    total_billed: float
    service_lines: List[ServiceLine] = field(default_factory=list)
    diagnosis_codes: List[str] = field(default_factory=list)
    place_of_service: str = "office"
    claim_type: str = "medical"  # medical, pharmacy, dental, vision
    insurance_paid: float = 0.0
    patient_responsibility: float = 0.0
    date_processed: Optional[date] = None
    denial_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert the claim to a dictionary for serialization."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "date_of_service": self.date_of_service.isoformat(),
            "date_submitted": self.date_submitted.isoformat(),
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "total_billed": self.total_billed,
            "service_lines": [sl.to_dict() for sl in self.service_lines],
            "diagnosis_codes": self.diagnosis_codes,
            "place_of_service": self.place_of_service,
            "claim_type": self.claim_type,
            "insurance_paid": self.insurance_paid,
            "patient_responsibility": self.patient_responsibility,
            "date_processed": self.date_processed.isoformat() if self.date_processed else None,
            "denial_reason": self.denial_reason,
            # Add flattened fields for compatibility with web frontend
            "service_date": self.date_of_service.isoformat(),
            "date_received": self.date_submitted.isoformat(),  # Add submission date
            "status": self.status.value if isinstance(self.status, Enum) else self.status,  # Use status instead of claim_status
            "claim_status": self.status.value if isinstance(self.status, Enum) else self.status,  # Keep claim_status for backward compatibility
            "total_amount": self.total_billed,
            "total_charge": self.total_billed,  # Add total_charge as an alias for total_billed
            "provider_id": self.provider_id,  # Use provider_id as the flattened field name
            "provider_name": self.provider_id,  # Add provider_name field for consistency
            # Add service description from the first service line if available
            "service_description": self.service_lines[0].description if self.service_lines else "Medical service",
            # Format diagnosis codes as objects with code and description properties
            "diagnoses": [{"code": code, "description": f"Diagnosis code {code}"} for code in self.diagnosis_codes]
        }


@dataclass
class PriorAuthorization:
    """Prior authorization request for healthcare services."""
    
    id: str
    member_id: str
    provider_id: str
    date_requested: date
    status: AuthorizationStatus
    service_lines: List[ServiceLine] = field(default_factory=list)
    diagnosis_codes: List[str] = field(default_factory=list)
    clinical_justification: str = ""
    authorization_type: str = "procedure"  # procedure, medication, equipment, etc.
    date_decision: Optional[date] = None
    decision_rationale: Optional[str] = None
    expiration_date: Optional[date] = None
    
    def to_dict(self) -> Dict:
        """Convert the prior authorization to a dictionary for serialization."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "date_requested": self.date_requested.isoformat(),
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "service_lines": [sl.to_dict() for sl in self.service_lines],
            "diagnosis_codes": self.diagnosis_codes,
            "clinical_justification": self.clinical_justification,
            "authorization_type": self.authorization_type,
            "date_decision": self.date_decision.isoformat() if self.date_decision else None,
            "decision_rationale": self.decision_rationale,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            # Add flattened fields for compatibility with web frontend
            "auth_status": self.status.value if isinstance(self.status, Enum) else self.status,
            "request_date": self.date_requested.isoformat(),
            "auth_type": self.authorization_type,
            "decision_date": self.date_decision.isoformat() if self.date_decision else None,
            "provider_name": self.provider_id,  # Add provider_name field for consistency
            # Format diagnosis codes as objects with code and description properties
            "diagnoses": [{"code": code, "description": f"Diagnosis code {code}"} for code in self.diagnosis_codes],
            # Add service description from the first service line if available
            "service_description": self.service_lines[0].description if self.service_lines else "No service details"
        }


@dataclass
class ExplanationOfBenefit:
    """Explanation of benefits (EOB) for a processed claim."""
    
    id: str
    claim_id: str
    member_id: str
    provider_id: str
    date_of_service: date
    date_processed: date
    total_billed: float
    insurance_paid: float
    patient_responsibility: float
    service_lines: List[Dict] = field(default_factory=list)
    remark_codes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert the EOB to a dictionary for serialization."""
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "date_of_service": self.date_of_service.isoformat(),
            "date_processed": self.date_processed.isoformat(),
            "total_billed": self.total_billed,
            "insurance_paid": self.insurance_paid,
            "patient_responsibility": self.patient_responsibility,
            "service_lines": self.service_lines,
            "remark_codes": self.remark_codes,
            # Add flattened fields for compatibility with web frontend
            "service_date": self.date_of_service.isoformat(),
            "process_date": self.date_processed.isoformat(),
            "total_amount": self.total_billed,
            "billed_amount": self.total_billed,  # Add billed_amount as an alias
            "patient_cost": self.patient_responsibility,
            "patient_responsibility": self.patient_responsibility,  # Ensure consistency
            "provider_name": self.provider_id  # Add provider_name field for consistency
        }


@dataclass
class BenefitCoverage:
    """Benefit coverage details for a specific service type."""
    
    service_type: ServiceType
    requires_authorization: bool = False
    deductible_applies: bool = True
    coinsurance_applies: bool = True
    copay_applies: bool = True
    copay_amount: float = 0.0
    coinsurance_rate: float = 0.2  # 20%
    coverage_percentage: float = 0.8  # 80%
    coverage_limits: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert the benefit coverage to a dictionary for serialization."""
        return {
            "service_type": self.service_type.value if isinstance(self.service_type, Enum) else self.service_type,
            "requires_authorization": self.requires_authorization,
            "deductible_applies": self.deductible_applies,
            "coinsurance_applies": self.coinsurance_applies,
            "copay_applies": self.copay_applies,
            "copay_amount": self.copay_amount,
            "coinsurance_rate": self.coinsurance_rate,
            "coverage_percentage": self.coverage_percentage,
            "coverage_limits": self.coverage_limits
        }


@dataclass
class PlanCoverage:
    """Insurance plan coverage details."""
    
    id: str
    plan_name: str
    plan_type: str  # HMO, PPO, EPO, POS, HDHP
    metal_level: str  # Bronze, Silver, Gold, Platinum
    year: int
    deductible_individual: float
    deductible_family: float
    out_of_pocket_max_individual: float
    out_of_pocket_max_family: float
    benefit_coverages: Dict[str, BenefitCoverage] = field(default_factory=dict)
    formulary_tiers: Dict[str, Dict] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert the plan coverage to a dictionary for serialization."""
        return {
            "id": self.id,
            "plan_name": self.plan_name,
            "plan_type": self.plan_type,
            "metal_level": self.metal_level,
            "year": self.year,
            "deductible_individual": self.deductible_individual,
            "deductible_family": self.deductible_family,
            "out_of_pocket_max_individual": self.out_of_pocket_max_individual,
            "out_of_pocket_max_family": self.out_of_pocket_max_family,
            "benefit_coverages": {k: v.to_dict() for k, v in self.benefit_coverages.items()},
            "formulary_tiers": self.formulary_tiers,
            # Add flattened fields for compatibility with web frontend
            "plan_display_name": self.plan_name,
            "plan_level": self.metal_level,
            "coverage_year": self.year,
            "individual_deductible": self.deductible_individual,
            "individual_max_oop": self.out_of_pocket_max_individual
        }