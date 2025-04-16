"""
Insurance processor for the synthetic healthcare data generator.

This module provides functionality to process and enrich synthetic insurance data.
"""

import logging
import os
import sys
import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from faker import Faker

from src.processors.base_processor import BaseProcessor
from src.models.insurance import (
    Claim, PriorAuthorization, ExplanationOfBenefit, PlanCoverage,
    ClaimStatus, AuthorizationStatus, ServiceType
)


class InsuranceProcessor(BaseProcessor):
    """Processor for synthetic insurance data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the insurance processor.
        
        Args:
            config: Configuration dictionary for the processor.
        """
        super().__init__(config)
        self.faker = Faker()
        
        # Extract processor configuration
        self.processor_config = config.get('processor_config', {})
        self.enrichment_config = config.get('enrichment_config', {})
    
    def process(self, data: List[Union[Claim, PriorAuthorization, ExplanationOfBenefit, PlanCoverage]]) -> List[Union[Claim, PriorAuthorization, ExplanationOfBenefit, PlanCoverage]]:
        """
        Process and enrich insurance data.
        
        Args:
            data: List of insurance objects to process.
            
        Returns:
            List of processed insurance objects.
        """
        if not data:
            self.logger.warning("No data provided for processing")
            return []
        
        # Determine the type of data we're processing
        data_type = type(data[0]).__name__ if data else None
        self.logger.info(f"Processing {len(data)} {data_type} objects")
        
        processed_data = []
        
        # Process based on data type
        if data_type == "Claim":
            processed_data = self._process_claims(data)
        elif data_type == "PriorAuthorization":
            processed_data = self._process_authorizations(data)
        elif data_type == "ExplanationOfBenefit":
            processed_data = self._process_eobs(data)
        elif data_type == "PlanCoverage":
            processed_data = self._process_plans(data)
        else:
            self.logger.warning(f"Unknown data type: {data_type}")
            return data
        
        self.logger.info(f"Processed {len(processed_data)} {data_type} objects")
        return processed_data
    
    def _process_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Process and enrich claim data.
        
        Args:
            claims: List of Claim objects to process.
            
        Returns:
            List of processed Claim objects.
        """
        processed_claims = []
        
        for claim in claims:
            # Apply enrichment based on configuration
            if self.enrichment_config.get('enrich_claims', True):
                claim = self._enrich_claim(claim)
            
            processed_claims.append(claim)
        
        return processed_claims
    
    def _process_authorizations(self, authorizations: List[PriorAuthorization]) -> List[PriorAuthorization]:
        """
        Process and enrich authorization data.
        
        Args:
            authorizations: List of PriorAuthorization objects to process.
            
        Returns:
            List of processed PriorAuthorization objects.
        """
        processed_authorizations = []
        
        for authorization in authorizations:
            # Apply enrichment based on configuration
            if self.enrichment_config.get('enrich_authorizations', True):
                authorization = self._enrich_authorization(authorization)
            
            processed_authorizations.append(authorization)
        
        return processed_authorizations
    
    def _process_eobs(self, eobs: List[ExplanationOfBenefit]) -> List[ExplanationOfBenefit]:
        """
        Process and enrich EOB data.
        
        Args:
            eobs: List of ExplanationOfBenefit objects to process.
            
        Returns:
            List of processed ExplanationOfBenefit objects.
        """
        processed_eobs = []
        
        for eob in eobs:
            # Apply enrichment based on configuration
            if self.enrichment_config.get('enrich_eobs', True):
                eob = self._enrich_eob(eob)
            
            processed_eobs.append(eob)
        
        return processed_eobs
    
    def _process_plans(self, plans: List[PlanCoverage]) -> List[PlanCoverage]:
        """
        Process and enrich plan data.
        
        Args:
            plans: List of PlanCoverage objects to process.
            
        Returns:
            List of processed PlanCoverage objects.
        """
        processed_plans = []
        
        for plan in plans:
            # Apply enrichment based on configuration
            if self.enrichment_config.get('enrich_plans', True):
                plan = self._enrich_plan(plan)
            
            processed_plans.append(plan)
        
        return processed_plans
    
    def _enrich_claim(self, claim: Claim) -> Claim:
        """
        Enrich a claim with additional information.
        
        Args:
            claim: Claim object to enrich.
            
        Returns:
            Enriched Claim object.
        """
        # Ensure consistency between claim status and financial information
        if claim.status == ClaimStatus.PAID:
            # For paid claims, ensure insurance_paid is close to total_billed
            if claim.insurance_paid < claim.total_billed * 0.7:
                claim.insurance_paid = round(claim.total_billed * random.uniform(0.7, 0.95), 2)
                claim.patient_responsibility = round(claim.total_billed - claim.insurance_paid, 2)
        
        elif claim.status == ClaimStatus.PARTIALLY_PAID:
            # For partially paid claims, ensure insurance_paid is less than total_billed
            if claim.insurance_paid > claim.total_billed * 0.7 or claim.insurance_paid == 0:
                claim.insurance_paid = round(claim.total_billed * random.uniform(0.3, 0.7), 2)
                claim.patient_responsibility = round(claim.total_billed - claim.insurance_paid, 2)
        
        elif claim.status == ClaimStatus.DENIED:
            # For denied claims, ensure insurance_paid is 0
            claim.insurance_paid = 0.0
            claim.patient_responsibility = claim.total_billed
            
            # Ensure denial reason is provided
            if not claim.denial_reason:
                denial_reasons = [
                    "Service not covered by plan",
                    "Prior authorization required but not obtained",
                    "Out of network provider",
                    "Duplicate claim",
                    "Medical necessity not established",
                    "Claim submitted after filing deadline",
                    "Incomplete information provided"
                ]
                claim.denial_reason = random.choice(denial_reasons)
        
        # Ensure date_processed is set for appropriate statuses
        if claim.status in [ClaimStatus.PAID, ClaimStatus.PARTIALLY_PAID, ClaimStatus.DENIED] and not claim.date_processed:
            claim.date_processed = claim.date_submitted + timedelta(days=random.randint(1, 30))
        
        # Ensure service lines are consistent with claim total
        total_service_line_price = sum(sl.total_price for sl in claim.service_lines)
        if abs(total_service_line_price - claim.total_billed) > 0.01:
            # Adjust the last service line to make the total match
            if claim.service_lines:
                adjustment = claim.total_billed - (total_service_line_price - claim.service_lines[-1].total_price)
                claim.service_lines[-1].total_price = round(adjustment, 2)
                claim.service_lines[-1].unit_price = round(adjustment / claim.service_lines[-1].quantity, 2)
        
        return claim
    
    def _enrich_authorization(self, authorization: PriorAuthorization) -> PriorAuthorization:
        """
        Enrich an authorization with additional information.
        
        Args:
            authorization: PriorAuthorization object to enrich.
            
        Returns:
            Enriched PriorAuthorization object.
        """
        # Ensure consistency between authorization status and decision information
        if authorization.status == AuthorizationStatus.APPROVED:
            # For approved authorizations, ensure decision date and expiration date are set
            if not authorization.date_decision:
                authorization.date_decision = authorization.date_requested + timedelta(days=random.randint(1, 14))
            
            if not authorization.expiration_date:
                authorization.expiration_date = authorization.date_decision + timedelta(days=random.randint(90, 365))
            
            # Ensure decision rationale is provided
            if not authorization.decision_rationale:
                approval_rationales = [
                    "Medical necessity criteria met",
                    "Meets plan coverage guidelines",
                    "Appropriate for diagnosis",
                    "Standard of care for condition",
                    "Prior treatments failed",
                    "No alternative treatments available"
                ]
                authorization.decision_rationale = random.choice(approval_rationales)
        
        elif authorization.status == AuthorizationStatus.DENIED:
            # For denied authorizations, ensure decision date is set
            if not authorization.date_decision:
                authorization.date_decision = authorization.date_requested + timedelta(days=random.randint(1, 14))
            
            # Ensure decision rationale is provided
            if not authorization.decision_rationale:
                denial_rationales = [
                    "Medical necessity criteria not met",
                    "Experimental/investigational treatment",
                    "Not covered by plan",
                    "Alternative treatments not tried",
                    "Insufficient clinical information provided",
                    "Out of network provider",
                    "Service can be provided at lower level of care"
                ]
                authorization.decision_rationale = random.choice(denial_rationales)
        
        elif authorization.status == AuthorizationStatus.ADDITIONAL_INFO_NEEDED:
            # Ensure decision rationale is provided
            if not authorization.decision_rationale:
                additional_info_rationales = [
                    "Clinical notes required",
                    "Test results needed",
                    "Treatment history required",
                    "Specialist consultation needed",
                    "Detailed prescription information required",
                    "Documentation of failed treatments needed"
                ]
                authorization.decision_rationale = random.choice(additional_info_rationales)
        
        # Enhance clinical justification if it's too short
        if len(authorization.clinical_justification) < 50:
            condition = "chronic condition"
            if authorization.diagnosis_codes:
                condition_map = {
                    "E11.9": "Type 2 diabetes",
                    "I10": "hypertension",
                    "J45.909": "asthma",
                    "M19.90": "osteoarthritis",
                    "F32.9": "depression",
                    "F41.9": "anxiety disorder",
                    "K21.9": "GERD",
                    "E78.5": "hyperlipidemia",
                    "E03.9": "hypothyroidism",
                    "M54.5": "low back pain",
                    "M81.0": "osteoporosis",
                    "J30.9": "allergic rhinitis",
                    "G43.909": "migraine",
                    "G47.00": "insomnia",
                    "N40.0": "benign prostatic hyperplasia"
                }
                condition = condition_map.get(authorization.diagnosis_codes[0], "chronic condition")
            
            symptoms = ["pain", "discomfort", "fatigue", "weakness", "numbness", "dizziness", "shortness of breath"]
            symptom1 = random.choice(symptoms)
            symptom2 = random.choice([s for s in symptoms if s != symptom1])
            
            authorization.clinical_justification = f"Patient with {condition} presents with {symptom1} and {symptom2}. Previous treatments have been ineffective. The requested service is medically necessary to address ongoing symptoms and prevent further deterioration."
        
        return authorization
    
    def _enrich_eob(self, eob: ExplanationOfBenefit) -> ExplanationOfBenefit:
        """
        Enrich an EOB with additional information.
        
        Args:
            eob: ExplanationOfBenefit object to enrich.
            
        Returns:
            Enriched ExplanationOfBenefit object.
        """
        # Ensure consistency between EOB totals and service line details
        total_billed_from_lines = sum(line.get('billed_amount', 0) for line in eob.service_lines)
        total_allowed_from_lines = sum(line.get('allowed_amount', 0) for line in eob.service_lines)
        total_insurance_paid_from_lines = sum(line.get('insurance_paid', 0) for line in eob.service_lines)
        total_patient_responsibility_from_lines = sum(line.get('patient_responsibility', 0) for line in eob.service_lines)
        
        # If there's a significant discrepancy, adjust the service lines
        if abs(total_billed_from_lines - eob.total_billed) > 0.01 and eob.service_lines:
            # Distribute the difference proportionally across service lines
            ratio = eob.total_billed / total_billed_from_lines if total_billed_from_lines > 0 else 1
            
            for line in eob.service_lines:
                line['billed_amount'] = round(line.get('billed_amount', 0) * ratio, 2)
                line['allowed_amount'] = round(line.get('allowed_amount', 0) * ratio, 2)
                line['insurance_paid'] = round(line.get('insurance_paid', 0) * ratio, 2)
                line['patient_responsibility'] = round(line.get('patient_responsibility', 0) * ratio, 2)
        
        # Ensure remark codes are present
        if not eob.remark_codes:
            common_remark_codes = [
                "M80", "MA01", "MA07", "MA18", "N4", "N20", "N130", "N381",
                "PR1", "PR2", "PR3", "PR4", "OA23", "PI11", "PI16", "PI125"
            ]
            num_codes = random.randint(1, 5)
            eob.remark_codes = random.sample(common_remark_codes, num_codes)
        
        return eob
    
    def _enrich_plan(self, plan: PlanCoverage) -> PlanCoverage:
        """
        Enrich a plan with additional information.
        
        Args:
            plan: PlanCoverage object to enrich.
            
        Returns:
            Enriched PlanCoverage object.
        """
        # Ensure family deductible and out-of-pocket max are consistent
        if plan.deductible_family < plan.deductible_individual * 1.5:
            plan.deductible_family = plan.deductible_individual * 2
        
        if plan.out_of_pocket_max_family < plan.out_of_pocket_max_individual * 1.5:
            plan.out_of_pocket_max_family = plan.out_of_pocket_max_individual * 2
        
        # Ensure benefit coverages are consistent with plan type and metal level
        for service_type, coverage in plan.benefit_coverages.items():
            # For HDHP plans, ensure deductible applies to most services
            if plan.plan_type == "HDHP" and service_type != ServiceType.PREVENTIVE_CARE.value:
                coverage.deductible_applies = True
                coverage.copay_applies = False
            
            # For preventive care, ensure it's covered at 100% with no cost sharing
            if service_type == ServiceType.PREVENTIVE_CARE.value:
                coverage.deductible_applies = False
                coverage.coinsurance_applies = False
                coverage.copay_applies = False
                coverage.coverage_percentage = 1.0
            
            # Adjust coverage percentage based on metal level
            if coverage.coinsurance_applies:
                base_percentage = {
                    "Bronze": 0.6,
                    "Silver": 0.7,
                    "Gold": 0.8,
                    "Platinum": 0.9
                }.get(plan.metal_level, 0.7)
                
                # Add some variation
                coverage.coverage_percentage = round(base_percentage + random.uniform(-0.05, 0.05), 2)
                coverage.coverage_percentage = max(0.5, min(1.0, coverage.coverage_percentage))
                
                # Update coinsurance rate to match coverage percentage
                coverage.coinsurance_rate = round(1.0 - coverage.coverage_percentage, 2)
        
        # Ensure formulary tiers are consistent
        if plan.formulary_tiers:
            # Ensure tier copays increase appropriately
            tiers = ["tier1", "tier2", "tier3", "tier4"]
            for i in range(1, len(tiers)):
                current_tier = tiers[i]
                previous_tier = tiers[i-1]
                
                if current_tier in plan.formulary_tiers and previous_tier in plan.formulary_tiers:
                    current_copay = plan.formulary_tiers[current_tier].get("copay", 0)
                    previous_copay = plan.formulary_tiers[previous_tier].get("copay", 0)
                    
                    if current_copay <= previous_copay:
                        plan.formulary_tiers[current_tier]["copay"] = previous_copay + random.randint(5, 20)
        
        return plan