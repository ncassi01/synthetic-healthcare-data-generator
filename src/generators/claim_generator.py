"""
Claim generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic insurance claim data.
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
from src.models.insurance import Claim, ClaimStatus, ServiceLine, ServiceType


class ClaimGenerator(BaseGenerator):
    """Generator for synthetic insurance claim data."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the claim generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract claim configuration
        self.claim_config = config.get('claim_config', {})
        self.service_config = config.get('service_config', {})
        
        # Common diagnosis codes (ICD-10)
        self.diagnosis_codes = [
            "E11.9",   # Type 2 diabetes without complications
            "I10",     # Essential hypertension
            "J45.909", # Unspecified asthma, uncomplicated
            "M19.90",  # Unspecified osteoarthritis, unspecified site
            "F32.9",   # Major depressive disorder, single episode, unspecified
            "F41.9",   # Anxiety disorder, unspecified
            "K21.9",   # Gastro-esophageal reflux disease without esophagitis
            "E78.5",   # Hyperlipidemia, unspecified
            "E03.9",   # Hypothyroidism, unspecified
            "M54.5",   # Low back pain
            "M81.0",   # Age-related osteoporosis without current pathological fracture
            "J30.9",   # Allergic rhinitis, unspecified
            "G43.909", # Migraine, unspecified, not intractable, without status migrainosus
            "G47.00",  # Insomnia, unspecified
            "N40.0"    # Benign prostatic hyperplasia without lower urinary tract symptoms
        ]
        
        # Common service codes (CPT/HCPCS)
        self.service_codes = {
            ServiceType.OFFICE_VISIT: [
                {"code": "99213", "description": "Office visit, established patient, 15 minutes"},
                {"code": "99214", "description": "Office visit, established patient, 25 minutes"},
                {"code": "99203", "description": "Office visit, new patient, 30 minutes"},
                {"code": "99204", "description": "Office visit, new patient, 45 minutes"}
            ],
            ServiceType.PREVENTIVE_CARE: [
                {"code": "99385", "description": "Preventive visit, new patient, 18-39 years"},
                {"code": "99386", "description": "Preventive visit, new patient, 40-64 years"},
                {"code": "99387", "description": "Preventive visit, new patient, 65+ years"},
                {"code": "99395", "description": "Preventive visit, established patient, 18-39 years"},
                {"code": "99396", "description": "Preventive visit, established patient, 40-64 years"},
                {"code": "99397", "description": "Preventive visit, established patient, 65+ years"}
            ],
            ServiceType.SPECIALIST_VISIT: [
                {"code": "99243", "description": "Office consultation, 40 minutes"},
                {"code": "99244", "description": "Office consultation, 60 minutes"},
                {"code": "99245", "description": "Office consultation, 80 minutes"}
            ],
            ServiceType.EMERGENCY: [
                {"code": "99281", "description": "Emergency department visit, minor"},
                {"code": "99282", "description": "Emergency department visit, low complexity"},
                {"code": "99283", "description": "Emergency department visit, moderate complexity"},
                {"code": "99284", "description": "Emergency department visit, high complexity"},
                {"code": "99285", "description": "Emergency department visit, high severity"}
            ],
            ServiceType.URGENT_CARE: [
                {"code": "S9083", "description": "Urgent care center visit"},
                {"code": "99058", "description": "Office services provided on an emergency basis"}
            ],
            ServiceType.INPATIENT: [
                {"code": "99221", "description": "Initial hospital care, low complexity"},
                {"code": "99222", "description": "Initial hospital care, moderate complexity"},
                {"code": "99223", "description": "Initial hospital care, high complexity"},
                {"code": "99231", "description": "Subsequent hospital care, low complexity"},
                {"code": "99232", "description": "Subsequent hospital care, moderate complexity"},
                {"code": "99233", "description": "Subsequent hospital care, high complexity"}
            ],
            ServiceType.OUTPATIENT: [
                {"code": "99211", "description": "Office visit, established patient, minimal"},
                {"code": "99212", "description": "Office visit, established patient, problem-focused"},
                {"code": "99213", "description": "Office visit, established patient, expanded problem-focused"}
            ],
            ServiceType.DIAGNOSTIC: [
                {"code": "80053", "description": "Comprehensive metabolic panel"},
                {"code": "85025", "description": "Complete blood count (CBC)"},
                {"code": "82607", "description": "Vitamin B-12 level"},
                {"code": "83036", "description": "Hemoglobin A1C level"}
            ],
            ServiceType.LABORATORY: [
                {"code": "80061", "description": "Lipid panel"},
                {"code": "84443", "description": "Thyroid stimulating hormone (TSH)"},
                {"code": "84153", "description": "Prostate specific antigen (PSA)"},
                {"code": "82465", "description": "Cholesterol level"}
            ],
            ServiceType.IMAGING: [
                {"code": "70450", "description": "CT scan, head/brain, without contrast"},
                {"code": "71045", "description": "X-ray, chest, single view"},
                {"code": "71046", "description": "X-ray, chest, 2 views"},
                {"code": "72100", "description": "X-ray, spine, lumbosacral, 2-3 views"},
                {"code": "73721", "description": "MRI, joint of lower extremity, without contrast"}
            ],
            ServiceType.PHARMACY: [
                {"code": "J0131", "description": "Injection, acetaminophen, 10 mg"},
                {"code": "J0133", "description": "Injection, acyclovir, 5 mg"},
                {"code": "J0171", "description": "Injection, adrenalin, epinephrine, 0.1 mg"},
                {"code": "J1100", "description": "Injection, dexamethasone sodium phosphate, 1 mg"}
            ],
            ServiceType.THERAPY: [
                {"code": "97110", "description": "Therapeutic exercises, 15 minutes"},
                {"code": "97112", "description": "Neuromuscular reeducation, 15 minutes"},
                {"code": "97116", "description": "Gait training, 15 minutes"},
                {"code": "97140", "description": "Manual therapy, 15 minutes"}
            ],
            ServiceType.MENTAL_HEALTH: [
                {"code": "90791", "description": "Psychiatric diagnostic evaluation"},
                {"code": "90832", "description": "Psychotherapy, 30 minutes"},
                {"code": "90834", "description": "Psychotherapy, 45 minutes"},
                {"code": "90837", "description": "Psychotherapy, 60 minutes"}
            ]
        }
        
        # Service type price ranges
        self.service_price_ranges = {
            ServiceType.OFFICE_VISIT: (75, 250),
            ServiceType.PREVENTIVE_CARE: (150, 350),
            ServiceType.SPECIALIST_VISIT: (150, 400),
            ServiceType.EMERGENCY: (500, 3000),
            ServiceType.URGENT_CARE: (125, 300),
            ServiceType.INPATIENT: (1500, 10000),
            ServiceType.OUTPATIENT: (200, 1000),
            ServiceType.DIAGNOSTIC: (50, 500),
            ServiceType.LABORATORY: (20, 300),
            ServiceType.IMAGING: (200, 2500),
            ServiceType.PHARMACY: (10, 1000),
            ServiceType.THERAPY: (75, 200),
            ServiceType.MENTAL_HEALTH: (100, 300)
        }
    
    def generate(self, count: int, members: List[Dict]) -> List[Claim]:
        """
        Generate synthetic claim data.
        
        Args:
            count: Number of claims to generate.
            members: List of member data to associate claims with.
            
        Returns:
            List of generated Claim objects.
        """
        self.logger.info(f"Generating {count} claims")
        claims = []
        
        # Ensure we have members to work with
        if not members:
            self.logger.warning("No members provided for claim generation")
            return claims
        
        for i in range(count):
            # Select a random member
            member = random.choice(members)
            claim = self._generate_claim(i, member)
            claims.append(claim)
            
        self.logger.info(f"Generated {len(claims)} claims")
        return claims
    
    def _generate_claim(self, index: int, member: Dict) -> Claim:
        """
        Generate a single synthetic claim.
        
        Args:
            index: Index of the claim (used for ID generation).
            member: Member data to associate the claim with.
            
        Returns:
            A synthetic Claim object.
        """
        # Generate claim ID
        claim_id = f"CLM{index:08d}"
        
        # Get member ID
        member_id = member.get('id', f"MEM{random.randint(10000, 99999)}")
        
        # Generate provider ID
        provider_id = f"PRV{random.randint(10000, 99999)}"
        
        # Generate dates
        today = date.today()
        date_of_service = today - timedelta(days=random.randint(1, 365))
        date_submitted = date_of_service + timedelta(days=random.randint(1, 30))
        
        # Generate claim status
        status_weights = self.claim_config.get('status_distribution', {
            ClaimStatus.SUBMITTED.value: 0.05,
            ClaimStatus.PENDING.value: 0.1,
            ClaimStatus.IN_PROCESS.value: 0.1,
            ClaimStatus.DENIED.value: 0.1,
            ClaimStatus.PARTIALLY_PAID.value: 0.15,
            ClaimStatus.PAID.value: 0.45,
            ClaimStatus.APPEALED.value: 0.05
        })
        
        status_value = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values()),
            k=1
        )[0]
        status = ClaimStatus(status_value)
        
        # Generate place of service
        place_of_service_options = ["office", "inpatient", "outpatient", "emergency", "ambulatory_surgical_center", "home"]
        place_of_service = random.choice(place_of_service_options)
        
        # Generate claim type
        claim_type_options = ["medical", "pharmacy", "dental", "vision"]
        claim_type_weights = [0.7, 0.2, 0.05, 0.05]
        claim_type = random.choices(claim_type_options, weights=claim_type_weights, k=1)[0]
        
        # Generate service lines
        num_service_lines = random.randint(1, 5)
        service_lines = []
        total_billed = 0.0
        
        for _ in range(num_service_lines):
            service_line = self._generate_service_line(claim_type)
            service_lines.append(service_line)
            total_billed += service_line.total_price
        
        # Round total billed to 2 decimal places
        total_billed = round(total_billed, 2)
        
        # Generate diagnosis codes
        num_diagnosis_codes = random.randint(1, 3)
        diagnosis_codes = random.sample(self.diagnosis_codes, num_diagnosis_codes)
        
        # Generate financial information based on status
        insurance_paid = 0.0
        patient_responsibility = 0.0
        date_processed = None
        denial_reason = None
        
        if status in [ClaimStatus.PAID, ClaimStatus.PARTIALLY_PAID]:
            # Calculate insurance paid and patient responsibility
            if status == ClaimStatus.PAID:
                insurance_percentage = random.uniform(0.7, 1.0)
            else:  # PARTIALLY_PAID
                insurance_percentage = random.uniform(0.3, 0.7)
                
            insurance_paid = round(total_billed * insurance_percentage, 2)
            patient_responsibility = round(total_billed - insurance_paid, 2)
            date_processed = date_submitted + timedelta(days=random.randint(1, 30))
            
        elif status == ClaimStatus.DENIED:
            patient_responsibility = total_billed
            date_processed = date_submitted + timedelta(days=random.randint(1, 30))
            
            # Generate denial reason
            denial_reasons = [
                "Service not covered by plan",
                "Prior authorization required but not obtained",
                "Out of network provider",
                "Duplicate claim",
                "Medical necessity not established",
                "Claim submitted after filing deadline",
                "Incomplete information provided"
            ]
            denial_reason = random.choice(denial_reasons)
        
        # Create and return claim
        return Claim(
            id=claim_id,
            member_id=member_id,
            provider_id=provider_id,
            date_of_service=date_of_service,
            date_submitted=date_submitted,
            status=status,
            total_billed=total_billed,
            service_lines=service_lines,
            diagnosis_codes=diagnosis_codes,
            place_of_service=place_of_service,
            claim_type=claim_type,
            insurance_paid=insurance_paid,
            patient_responsibility=patient_responsibility,
            date_processed=date_processed,
            denial_reason=denial_reason
        )
    
    def _generate_service_line(self, claim_type: str) -> ServiceLine:
        """
        Generate a service line for a claim.
        
        Args:
            claim_type: Type of claim (medical, pharmacy, dental, vision).
            
        Returns:
            A synthetic ServiceLine object.
        """
        # Select service type based on claim type
        if claim_type == "medical":
            service_type_options = [
                ServiceType.OFFICE_VISIT, ServiceType.PREVENTIVE_CARE, 
                ServiceType.SPECIALIST_VISIT, ServiceType.EMERGENCY,
                ServiceType.URGENT_CARE, ServiceType.INPATIENT,
                ServiceType.OUTPATIENT, ServiceType.DIAGNOSTIC,
                ServiceType.LABORATORY, ServiceType.IMAGING,
                ServiceType.THERAPY, ServiceType.MENTAL_HEALTH
            ]
            service_type_weights = [0.25, 0.15, 0.1, 0.05, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05, 0.03, 0.02]
        elif claim_type == "pharmacy":
            service_type_options = [ServiceType.PHARMACY]
            service_type_weights = [1.0]
        elif claim_type == "dental":
            service_type_options = [ServiceType.DENTAL]
            service_type_weights = [1.0]
        else:  # vision
            service_type_options = [ServiceType.VISION]
            service_type_weights = [1.0]
        
        service_type = random.choices(service_type_options, weights=service_type_weights, k=1)[0]
        
        # Select service code and description
        if service_type in self.service_codes:
            service_code_info = random.choice(self.service_codes[service_type])
            service_code = service_code_info["code"]
            description = service_code_info["description"]
        else:
            service_code = f"CODE{random.randint(10000, 99999)}"
            description = f"Service description for {service_type.value}"
        
        # Generate quantity
        quantity = 1
        if service_type in [ServiceType.PHARMACY, ServiceType.THERAPY]:
            quantity = random.randint(1, 10)
        
        # Generate unit price
        if service_type in self.service_price_ranges:
            min_price, max_price = self.service_price_ranges[service_type]
            unit_price = round(random.uniform(min_price, max_price), 2)
        else:
            unit_price = round(random.uniform(50, 500), 2)
        
        # Calculate total price
        total_price = round(unit_price * quantity, 2)
        
        return ServiceLine(
            service_code=service_code,
            description=description,
            service_type=service_type,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )