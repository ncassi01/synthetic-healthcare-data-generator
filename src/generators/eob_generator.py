"""
Explanation of Benefits (EOB) generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic EOB data based on claims.
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
from src.models.insurance import ExplanationOfBenefit, Claim, ClaimStatus


class EOBGenerator(BaseGenerator):
    """Generator for synthetic Explanation of Benefits (EOB) data."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the EOB generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract EOB configuration
        self.eob_config = config.get('eob_config', {})
        
        # Common remark codes
        self.remark_codes = [
            "M80", # Services denied due to failure to file timely
            "MA01", # Alert: If you do not agree with what we approved for these services, you may appeal our decision
            "MA07", # Alert: The claim information has also been forwarded to Medicaid for review
            "MA18", # Alert: The claim information is also being forwarded to the patient's supplemental insurer
            "N4", # Missing/incomplete/invalid prior insurance carrier EOB
            "N20", # Service not payable with other service rendered on the same date
            "N130", # Consult plan benefit documents/guidelines for information about restrictions for this service
            "N381", # Alert: Consult our contractual agreement for restrictions/billing/payment information
            "PR1", # Patient responsibility
            "PR2", # Patient responsibility - coinsurance amount
            "PR3", # Patient responsibility - copay amount
            "PR4", # Patient responsibility - deductible amount
            "OA23", # Funds have been obligated for this claim/service
            "PI11", # The diagnosis is inconsistent with the procedure
            "PI16", # The procedure/service is inconsistent with the patient's age
            "PI125", # Submission/billing error(s)
        ]
    
    def generate(self, claims: List[Claim]) -> List[ExplanationOfBenefit]:
        """
        Generate synthetic EOB data based on claims.
        
        Args:
            claims: List of Claim objects to generate EOBs for.
            
        Returns:
            List of generated ExplanationOfBenefit objects.
        """
        self.logger.info(f"Generating EOBs for {len(claims)} claims")
        eobs = []
        
        # Filter claims that are eligible for EOB generation (paid or partially paid)
        eligible_claims = [
            claim for claim in claims 
            if claim.status in [ClaimStatus.PAID, ClaimStatus.PARTIALLY_PAID] and claim.date_processed is not None
        ]
        
        self.logger.info(f"Found {len(eligible_claims)} eligible claims for EOB generation")
        
        for i, claim in enumerate(eligible_claims):
            eob = self._generate_eob(i, claim)
            eobs.append(eob)
            
        self.logger.info(f"Generated {len(eobs)} EOBs")
        return eobs
    
    def _generate_eob(self, index: int, claim: Claim) -> ExplanationOfBenefit:
        """
        Generate a single synthetic EOB based on a claim.
        
        Args:
            index: Index of the EOB (used for ID generation).
            claim: Claim object to generate the EOB for.
            
        Returns:
            A synthetic ExplanationOfBenefit object.
        """
        # Generate EOB ID
        eob_id = f"EOB{index:08d}"
        
        # Extract claim information
        claim_id = claim.id
        member_id = claim.member_id
        provider_id = claim.provider_id
        date_of_service = claim.date_of_service
        date_processed = claim.date_processed if claim.date_processed else date.today()
        total_billed = claim.total_billed
        insurance_paid = claim.insurance_paid
        patient_responsibility = claim.patient_responsibility
        
        # Generate service lines for EOB
        service_lines = []
        for service_line in claim.service_lines:
            # Calculate allowed amount (typically less than billed amount)
            allowed_amount = round(service_line.total_price * random.uniform(0.6, 0.9), 2)
            
            # Calculate insurance paid for this service line
            line_insurance_paid = round(allowed_amount * random.uniform(0.7, 1.0), 2)
            
            # Calculate patient responsibility for this service line
            line_patient_responsibility = round(allowed_amount - line_insurance_paid, 2)
            
            # Determine if deductible, copay, or coinsurance applies
            deductible_amount = 0.0
            copay_amount = 0.0
            coinsurance_amount = 0.0
            
            # Randomly assign patient responsibility to deductible, copay, or coinsurance
            if line_patient_responsibility > 0:
                responsibility_type = random.choices(
                    ["deductible", "copay", "coinsurance"],
                    weights=[0.3, 0.4, 0.3],
                    k=1
                )[0]
                
                if responsibility_type == "deductible":
                    deductible_amount = line_patient_responsibility
                elif responsibility_type == "copay":
                    copay_amount = line_patient_responsibility
                else:  # coinsurance
                    coinsurance_amount = line_patient_responsibility
            
            # Create EOB service line
            eob_service_line = {
                "service_code": service_line.service_code,
                "description": service_line.description,
                "service_type": service_line.service_type.value if hasattr(service_line.service_type, "value") else service_line.service_type,
                "date_of_service": date_of_service.isoformat(),
                "billed_amount": service_line.total_price,
                "allowed_amount": allowed_amount,
                "insurance_paid": line_insurance_paid,
                "patient_responsibility": line_patient_responsibility,
                "deductible_amount": deductible_amount,
                "copay_amount": copay_amount,
                "coinsurance_amount": coinsurance_amount
            }
            
            service_lines.append(eob_service_line)
        
        # Generate remark codes
        num_remark_codes = random.randint(1, 5)
        remark_codes = random.sample(self.remark_codes, num_remark_codes)
        
        # Create and return EOB
        return ExplanationOfBenefit(
            id=eob_id,
            claim_id=claim_id,
            member_id=member_id,
            provider_id=provider_id,
            date_of_service=date_of_service,
            date_processed=date_processed,
            total_billed=total_billed,
            insurance_paid=insurance_paid,
            patient_responsibility=patient_responsibility,
            service_lines=service_lines,
            remark_codes=remark_codes
        )