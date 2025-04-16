"""
Member data model for the synthetic healthcare data generator.

This module defines the data model for representing members in the healthcare system.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class Address:
    """Address information for a member."""
    
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"


@dataclass
class Contact:
    """Contact information for a member."""
    
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_contact_method: str = "email"


@dataclass
class Insurance:
    """Insurance information for a member."""
    
    plan_type: str  # HMO, PPO, EPO, POS, HDHP
    metal_level: str  # Bronze, Silver, Gold, Platinum
    member_id: str
    group_id: Optional[str] = None
    coverage_start_date: date = field(default_factory=date.today)
    coverage_end_date: Optional[date] = None
    primary_care_provider_id: Optional[str] = None
    deductible: float = 0.0
    out_of_pocket_max: float = 0.0
    copay: Dict[str, float] = field(default_factory=dict)
    coinsurance: Dict[str, float] = field(default_factory=dict)


@dataclass
class Demographics:
    """Demographic information for a member."""
    
    date_of_birth: date
    gender: str
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    language: str = "en"
    marital_status: Optional[str] = None


@dataclass
class Member:
    """Member data model representing a healthcare member/patient."""
    
    id: str
    first_name: str
    last_name: str
    demographics: Demographics
    address: Address
    contact: Contact
    insurance: Insurance
    conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    procedures: List[str] = field(default_factory=list)
    risk_scores: Dict[str, float] = field(default_factory=dict)
    risk_score: float = 0.0  # Single risk score for compatibility with web frontend
    care_gaps: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def full_name(self) -> str:
        """Get the full name of the member."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculate the age of the member based on their date of birth."""
        today = date.today()
        born = self.demographics.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    def to_dict(self) -> Dict:
        """Convert the member to a dictionary for serialization."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "age": self.age,
            "demographics": {
                "date_of_birth": self.demographics.date_of_birth.isoformat(),
                "gender": self.demographics.gender,
                "race": self.demographics.race,
                "ethnicity": self.demographics.ethnicity,
                "language": self.demographics.language,
                "marital_status": self.demographics.marital_status,
            },
            "address": {
                "street": self.address.street,
                "city": self.address.city,
                "state": self.address.state,
                "zip_code": self.address.zip_code,
                "country": self.address.country,
            },
            "contact": {
                "email": self.contact.email,
                "phone": self.contact.phone,
                "preferred_contact_method": self.contact.preferred_contact_method,
            },
            "insurance": {
                "plan_type": self.insurance.plan_type,
                "metal_level": self.insurance.metal_level,
                "plan_name": self.insurance.plan_type + " " + self.insurance.metal_level,
                "member_id": self.insurance.member_id,
                "group_id": self.insurance.group_id,
                "coverage_start_date": self.insurance.coverage_start_date.isoformat(),
                "effective_date": self.insurance.coverage_start_date.isoformat(),  # Alias for compatibility
                "coverage_end_date": self.insurance.coverage_end_date.isoformat() if self.insurance.coverage_end_date else None,
                "primary_care_provider_id": self.insurance.primary_care_provider_id,
                "deductible": self.insurance.deductible,
                "out_of_pocket_max": self.insurance.out_of_pocket_max,
                "copay": self.insurance.copay,
                "coinsurance": self.insurance.coinsurance,
            },
            "conditions": self.conditions,
            "medications": self.medications,
            "procedures": self.procedures,
            "risk_scores": self.risk_scores,
            "risk_score": self.risk_score,
            "care_gaps": self.care_gaps,
            # Add flattened contact information for compatibility with web frontend
            "email": self.contact.email,
            "phone": self.contact.phone,
            # Add flattened demographics information for compatibility with web frontend
            "gender": self.demographics.gender,
            "date_of_birth": self.demographics.date_of_birth.isoformat(),
            # Add flattened insurance information for compatibility with web frontend
            "plan_name": self.insurance.plan_type + " " + self.insurance.metal_level,
            "effective_date": self.insurance.coverage_start_date.isoformat(),
        }