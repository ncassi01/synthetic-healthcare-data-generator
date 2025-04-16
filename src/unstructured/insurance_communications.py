"""
Insurance communications generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic communications from insurance companies
to members and providers, such as coverage determinations, prior authorization responses,
and claim status updates.
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


class InsuranceCommunicationsGenerator(BaseGenerator):
    """Generator for synthetic insurance communications."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the insurance communications generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract configuration
        self.insurance_comm_config = config.get('insurance_communications_config', {})
        
    def generate(self, count: int, member_ids: List[str] = None, provider_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic insurance communications.
        
        Args:
            count: Number of communications to generate.
            member_ids: Optional list of member IDs to associate with the communications.
                If not provided, random IDs will be generated.
            provider_ids: Optional list of provider IDs to use in the communications.
                If not provided, random IDs will be generated.
                
        Returns:
            List of generated insurance communication entries.
        """
        self.logger.info(f"Generating {count} insurance communications")
        
        if member_ids is None:
            # Generate random member IDs if not provided
            member_ids = [f"MEM{i:08d}" for i in range(count)]
        
        if provider_ids is None:
            # Generate random provider IDs if not provided
            provider_ids = [f"PRV{i:08d}" for i in range(20)]  # Generate 20 providers
        
        # If fewer member IDs than count, repeat member IDs
        if len(member_ids) < count:
            member_ids = (member_ids * (count // len(member_ids) + 1))[:count]
        
        communications = []
        
        # Generate different types of insurance communications
        comm_types = [
            'coverage_determination', 
            'prior_auth_response', 
            'claim_status', 
            'benefit_explanation',
            'appeal_response'
        ]
        
        for i in range(count):
            comm_type = random.choice(comm_types)
            
            if comm_type == 'coverage_determination':
                comm = self._generate_coverage_determination(member_ids[i], provider_ids)
            elif comm_type == 'prior_auth_response':
                comm = self._generate_prior_auth_response(member_ids[i], provider_ids)
            elif comm_type == 'claim_status':
                comm = self._generate_claim_status(member_ids[i], provider_ids)
            elif comm_type == 'benefit_explanation':
                comm = self._generate_benefit_explanation(member_ids[i])
            elif comm_type == 'appeal_response':
                comm = self._generate_appeal_response(member_ids[i], provider_ids)
            
            communications.append(comm)
            
        self.logger.info(f"Generated {len(communications)} insurance communications")
        return communications
    
    def _generate_coverage_determination(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a coverage determination communication."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Generate insurance details
        insurance_details = self._generate_insurance_details()
        
        # Generate service details
        service_details = self._generate_service_details()
        
        # Generate determination
        determination = random.choice(['Approved', 'Denied', 'Partially Approved'])
        
        # Generate rationale based on determination
        if determination == 'Approved':
            rationale = self._generate_approval_rationale()
        elif determination == 'Denied':
            rationale = self._generate_denial_rationale()
        else:  # Partially Approved
            rationale = self._generate_partial_approval_rationale()
        
        return {
            "id": f"COV{random.randint(10000, 99999)}",
            "type": "coverage_determination",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": comm_date.strftime("%Y-%m-%d"),
            "insurance": insurance_details,
            "service_requested": service_details,
            "determination": determination,
            "rationale": rationale,
            "effective_date": comm_date.strftime("%Y-%m-%d"),
            "expiration_date": (comm_date + timedelta(days=random.randint(90, 365))).strftime("%Y-%m-%d") if determination != 'Denied' else None,
            "appeal_rights": self._generate_appeal_rights(determination),
            "additional_information": self.faker.paragraph() if random.random() > 0.7 else None
        }
    
    def _generate_prior_auth_response(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a prior authorization response communication."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Generate insurance details
        insurance_details = self._generate_insurance_details()
        
        # Generate service details
        service_details = self._generate_service_details()
        
        # Generate authorization details
        auth_number = f"AUTH{random.randint(100000, 999999)}"
        
        # Generate determination
        determination = random.choice(['Approved', 'Denied', 'Pending Additional Information'])
        
        # Generate rationale based on determination
        if determination == 'Approved':
            rationale = self._generate_approval_rationale()
        elif determination == 'Denied':
            rationale = self._generate_denial_rationale()
        else:  # Pending Additional Information
            rationale = self._generate_pending_rationale()
        
        return {
            "id": f"PA{random.randint(10000, 99999)}",
            "type": "prior_auth_response",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": comm_date.strftime("%Y-%m-%d"),
            "insurance": insurance_details,
            "service_requested": service_details,
            "auth_number": auth_number if determination == 'Approved' else None,
            "determination": determination,
            "rationale": rationale,
            "effective_date": comm_date.strftime("%Y-%m-%d") if determination == 'Approved' else None,
            "expiration_date": (comm_date + timedelta(days=random.randint(90, 365))).strftime("%Y-%m-%d") if determination == 'Approved' else None,
            "units_approved": random.randint(1, 10) if determination == 'Approved' else None,
            "additional_information_needed": self._generate_additional_info_needed() if determination == 'Pending Additional Information' else None,
            "appeal_rights": self._generate_appeal_rights(determination) if determination != 'Pending Additional Information' else None
        }
    
    def _generate_claim_status(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a claim status communication."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random date within the last 90 days
        service_date = datetime.now() - timedelta(days=random.randint(30, 120))
        claim_date = service_date + timedelta(days=random.randint(1, 14))
        status_date = claim_date + timedelta(days=random.randint(7, 30))
        
        # Generate insurance details
        insurance_details = self._generate_insurance_details()
        
        # Generate claim details
        claim_number = f"CLM{random.randint(1000000, 9999999)}"
        
        # Generate service details
        service_details = self._generate_service_details()
        
        # Generate claim status
        status = random.choice(['Paid', 'Denied', 'Pending', 'Partially Paid'])
        
        # Generate financial details based on status
        if status in ['Paid', 'Partially Paid']:
            financial_details = self._generate_financial_details(service_details['estimated_cost'])
        else:
            financial_details = None
        
        # Generate reason based on status
        if status == 'Denied':
            reason = self._generate_claim_denial_reason()
        elif status == 'Pending':
            reason = self._generate_claim_pending_reason()
        elif status == 'Partially Paid':
            reason = self._generate_partial_payment_reason()
        else:  # Paid
            reason = None
        
        return {
            "id": f"CS{random.randint(10000, 99999)}",
            "type": "claim_status",
            "member_id": member_id,
            "provider_id": provider_id,
            "claim_number": claim_number,
            "service_date": service_date.strftime("%Y-%m-%d"),
            "claim_submission_date": claim_date.strftime("%Y-%m-%d"),
            "status_date": status_date.strftime("%Y-%m-%d"),
            "insurance": insurance_details,
            "service": service_details,
            "status": status,
            "financial_details": financial_details,
            "reason": reason,
            "next_steps": self._generate_next_steps(status) if status != 'Paid' else None,
            "appeal_rights": self._generate_appeal_rights(status) if status in ['Denied', 'Partially Paid'] else None
        }
    
    def _generate_benefit_explanation(self, member_id: str) -> Dict[str, Any]:
        """Generate a benefit explanation communication."""
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Generate insurance details
        insurance_details = self._generate_insurance_details()
        
        # Generate benefit category
        benefit_categories = [
            'Preventive Care', 'Primary Care', 'Specialty Care', 
            'Emergency Services', 'Hospital Services', 'Prescription Drugs',
            'Mental Health', 'Rehabilitation', 'Durable Medical Equipment'
        ]
        
        category = random.choice(benefit_categories)
        
        # Generate benefit details based on category
        if category == 'Preventive Care':
            details = {
                "coverage": "100% covered",
                "network_restrictions": "In-network only",
                "frequency_limits": random.choice([
                    "Annual wellness visit", 
                    "Age-appropriate screenings", 
                    "Immunizations per CDC schedule"
                ]),
                "examples": [
                    "Annual physical", 
                    "Mammogram", 
                    "Colonoscopy", 
                    "Immunizations"
                ]
            }
        elif category == 'Primary Care':
            details = {
                "coverage": f"${random.choice([20, 25, 30, 35, 40])} copay",
                "network_restrictions": "In-network preferred",
                "out_of_network": f"{random.randint(30, 50)}% coinsurance after deductible",
                "referral_requirements": random.choice([True, False])
            }
        elif category == 'Specialty Care':
            details = {
                "coverage": f"${random.choice([40, 50, 60, 75])} copay",
                "network_restrictions": "In-network preferred",
                "out_of_network": f"{random.randint(30, 50)}% coinsurance after deductible",
                "referral_requirements": random.choice([True, False]),
                "prior_auth_services": [
                    "Complex imaging", 
                    "Certain procedures", 
                    "Specialty medications"
                ]
            }
        elif category == 'Prescription Drugs':
            details = {
                "tiers": {
                    "Tier 1 (Generic)": f"${random.choice([5, 10, 15])} copay",
                    "Tier 2 (Preferred Brand)": f"${random.choice([30, 40, 50])} copay",
                    "Tier 3 (Non-Preferred Brand)": f"${random.choice([60, 75, 100])} copay",
                    "Tier 4 (Specialty)": f"{random.randint(20, 40)}% coinsurance"
                },
                "mail_order": "90-day supply for 2x copay",
                "formulary_restrictions": "Some medications require prior authorization or step therapy",
                "pharmacy_network": random.choice(["Any pharmacy", "Preferred pharmacy network"])
            }
        else:
            details = {
                "coverage": random.choice([
                    f"${random.randint(20, 100)} copay",
                    f"{random.randint(10, 30)}% coinsurance after deductible",
                    f"${random.randint(250, 1000)} copay then {random.randint(10, 30)}% coinsurance"
                ]),
                "network_restrictions": random.choice([
                    "In-network only",
                    "In-network preferred",
                    "Any provider with higher cost-sharing out-of-network"
                ]),
                "prior_authorization": random.choice([True, False]),
                "limitations": random.choice([
                    f"Limited to {random.randint(20, 60)} visits per year",
                    f"Limited to {random.randint(20, 60)} days per year",
                    "Medical necessity review required after initial treatment",
                    None
                ])
            }
        
        return {
            "id": f"BE{random.randint(10000, 99999)}",
            "type": "benefit_explanation",
            "member_id": member_id,
            "date": comm_date.strftime("%Y-%m-%d"),
            "insurance": insurance_details,
            "benefit_category": category,
            "details": details,
            "deductible_applies": random.choice([True, False]) if category != 'Preventive Care' else False,
            "out_of_pocket_applies": random.choice([True, False]) if category != 'Preventive Care' else False,
            "additional_information": self.faker.paragraph() if random.random() > 0.7 else None,
            "disclaimer": "This is a summary of benefits. Please refer to your plan documents for complete details."
        }
    
    def _generate_appeal_response(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate an appeal response communication."""
        # Select random provider
        provider_id = random.choice(provider_ids)
        
        # Generate random dates
        service_date = datetime.now() - timedelta(days=random.randint(60, 180))
        denial_date = service_date + timedelta(days=random.randint(14, 30))
        appeal_date = denial_date + timedelta(days=random.randint(7, 30))
        response_date = appeal_date + timedelta(days=random.randint(14, 30))
        
        # Generate insurance details
        insurance_details = self._generate_insurance_details()
        
        # Generate service details
        service_details = self._generate_service_details()
        
        # Generate appeal details
        appeal_number = f"APP{random.randint(10000, 99999)}"
        original_denial_reason = self._generate_denial_rationale()
        
        # Generate determination
        determination = random.choice(['Upheld', 'Overturned', 'Partially Overturned'])
        
        # Generate rationale based on determination
        if determination == 'Upheld':
            rationale = self._generate_appeal_upheld_rationale()
        elif determination == 'Overturned':
            rationale = self._generate_appeal_overturned_rationale()
        else:  # Partially Overturned
            rationale = self._generate_appeal_partially_overturned_rationale()
        
        return {
            "id": f"AR{random.randint(10000, 99999)}",
            "type": "appeal_response",
            "member_id": member_id,
            "provider_id": provider_id,
            "date": response_date.strftime("%Y-%m-%d"),
            "insurance": insurance_details,
            "service": service_details,
            "appeal_number": appeal_number,
            "original_denial_date": denial_date.strftime("%Y-%m-%d"),
            "appeal_submission_date": appeal_date.strftime("%Y-%m-%d"),
            "original_denial_reason": original_denial_reason,
            "determination": determination,
            "rationale": rationale,
            "next_level_appeal": self._generate_next_level_appeal(determination) if determination in ['Upheld', 'Partially Overturned'] else None,
            "financial_adjustment": self._generate_financial_adjustment(service_details['estimated_cost']) if determination in ['Overturned', 'Partially Overturned'] else None,
            "additional_information": self.faker.paragraph() if random.random() > 0.7 else None
        }
    
    def _generate_insurance_details(self) -> Dict[str, str]:
        """Generate insurance plan details."""
        # Insurance company names
        companies = [
            "Blue Cross Blue Shield", "Aetna", "UnitedHealthcare", 
            "Cigna", "Humana", "Kaiser Permanente", "Anthem",
            "Centene", "Molina Healthcare", "Health Net"
        ]
        
        # Plan types
        plan_types = ["HMO", "PPO", "EPO", "POS", "HDHP"]
        
        # Metal levels
        metal_levels = ["Bronze", "Silver", "Gold", "Platinum"]
        
        return {
            "company": random.choice(companies),
            "plan_name": f"{random.choice(companies)} {random.choice(metal_levels)} {random.choice(plan_types)}",
            "plan_type": random.choice(plan_types),
            "metal_level": random.choice(metal_levels),
            "group_number": f"GRP{random.randint(10000, 99999)}",
            "member_id": f"ID{random.randint(100000, 999999)}"
        }
    
    def _generate_service_details(self) -> Dict[str, Any]:
        """Generate healthcare service details."""
        # Service categories
        categories = [
            "Diagnostic", "Preventive", "Surgical", "Therapeutic", 
            "Consultation", "Durable Medical Equipment", "Imaging",
            "Laboratory", "Medication", "Procedure"
        ]
        
        # Specific services by category
        services = {
            "Diagnostic": [
                "MRI", "CT Scan", "Ultrasound", "X-ray", 
                "EKG", "Echocardiogram", "Colonoscopy", "Endoscopy"
            ],
            "Preventive": [
                "Annual physical", "Mammogram", "Colonoscopy screening", 
                "Immunization", "Well-child visit", "Pap smear"
            ],
            "Surgical": [
                "Appendectomy", "Cholecystectomy", "Hernia repair", 
                "Joint replacement", "Cataract surgery", "Tonsillectomy"
            ],
            "Therapeutic": [
                "Physical therapy", "Occupational therapy", "Speech therapy", 
                "Chemotherapy", "Radiation therapy", "Dialysis"
            ],
            "Consultation": [
                "Specialist consultation", "Second opinion", 
                "New patient visit", "Follow-up visit"
            ],
            "Durable Medical Equipment": [
                "Wheelchair", "Hospital bed", "CPAP machine", 
                "Oxygen equipment", "Walker", "Prosthetic device"
            ],
            "Imaging": [
                "MRI", "CT Scan", "Ultrasound", "X-ray", 
                "PET scan", "Bone density scan", "Mammogram"
            ],
            "Laboratory": [
                "Blood test", "Urinalysis", "Biopsy", "Genetic testing", 
                "Pathology", "Microbiology culture"
            ],
            "Medication": [
                "Specialty medication", "Infusion therapy", 
                "Injectable medication", "Chemotherapy drugs"
            ],
            "Procedure": [
                "Biopsy", "Cardiac catheterization", "Endoscopy", 
                "Joint injection", "Lumbar puncture", "Skin lesion removal"
            ]
        }
        
        # Select category and service
        category = random.choice(categories)
        service = random.choice(services[category])
        
        # Generate CPT/HCPCS code (simplified)
        code = f"{random.choice(['A', 'B', 'C', 'E', 'G', 'J', 'K', 'L', 'M', 'P', 'Q', 'S', 'T'])}{random.randint(1000, 9999)}"
        
        # Generate diagnosis codes (ICD-10, simplified)
        diagnosis_codes = []
        for _ in range(random.randint(1, 3)):
            diagnosis_codes.append(f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Z'])}{random.randint(10, 99)}.{random.randint(0, 9)}")
        
        # Generate place of service
        places_of_service = [
            "Office", "Outpatient Hospital", "Inpatient Hospital", 
            "Emergency Room", "Ambulatory Surgical Center", "Home",
            "Skilled Nursing Facility", "Independent Laboratory"
        ]
        
        # Generate cost
        if category in ["Surgical", "Imaging", "Diagnostic"] and service in ["MRI", "CT Scan", "Joint replacement"]:
            estimated_cost = random.randint(1000, 10000)
        elif category in ["Therapeutic", "Durable Medical Equipment"]:
            estimated_cost = random.randint(500, 3000)
        else:
            estimated_cost = random.randint(100, 1000)
        
        return {
            "category": category,
            "service": service,
            "code": code,
            "diagnosis_codes": diagnosis_codes,
            "place_of_service": random.choice(places_of_service),
            "estimated_cost": estimated_cost,
            "quantity": random.randint(1, 5) if category in ["Therapeutic", "Durable Medical Equipment", "Medication"] else 1
        }
    
    def _generate_approval_rationale(self) -> str:
        """Generate rationale for an approval."""
        rationales = [
            "Service meets medical necessity criteria based on clinical documentation provided.",
            "Requested service is a covered benefit under the member's plan and is medically necessary.",
            "Clinical information provided supports the medical necessity of the requested service.",
            "Service is appropriate based on the member's diagnosis and clinical condition.",
            "Requested service follows evidence-based guidelines for the member's condition.",
            "Documentation demonstrates that the service is required for the member's medical condition."
        ]
        
        return random.choice(rationales)
    
    def _generate_denial_rationale(self) -> str:
        """Generate rationale for a denial."""
        rationales = [
            "Service does not meet medical necessity criteria based on the clinical information provided.",
            "Requested service is not a covered benefit under the member's current plan.",
            "Documentation provided does not support the medical necessity of the requested service.",
            "Alternative, more conservative treatment options have not been adequately tried or considered.",
            "Service is considered experimental or investigational for the member's condition.",
            "Insufficient clinical information was provided to determine medical necessity.",
            "Service is not appropriate for the member's diagnosis or clinical condition based on evidence-based guidelines.",
            "The requested service exceeds the frequency or duration limits specified in the member's plan."
        ]
        
        return random.choice(rationales)
    
    def _generate_partial_approval_rationale(self) -> str:
        """Generate rationale for a partial approval."""
        rationales = [
            "Partial approval for reduced duration based on medical necessity criteria.",
            "Approved for fewer units/visits than requested based on the member's clinical condition.",
            "Alternative service approved that better aligns with evidence-based guidelines for the member's condition.",
            "Partial approval based on plan limitations for the requested service.",
            "Some components of the requested service are approved, while others do not meet medical necessity criteria.",
            "Approved at a lower level of care that is appropriate for the member's clinical condition."
        ]
        
        return random.choice(rationales)
    
    def _generate_pending_rationale(self) -> str:
        """Generate rationale for a pending determination."""
        rationales = [
            "Additional clinical information is needed to determine medical necessity.",
            "Specialist review is required before a determination can be made.",
            "Documentation provided is incomplete or insufficient for determination.",
            "Clarification needed regarding the specific service being requested.",
            "Additional information about previous treatments and outcomes is required.",
            "Medical records from the past 6 months are needed to complete the review."
        ]
        
        return random.choice(rationales)
    
    def _generate_appeal_rights(self, determination: str) -> Dict[str, Any]:
        """Generate appeal rights information."""
        if determination in ['Denied', 'Partially Approved', 'Upheld', 'Partially Overturned']:
            return {
                "appeal_deadline": f"{random.randint(30, 180)} days from the date of this notice",
                "submission_methods": [
                    {
                        "method": "Mail",
                        "address": f"{random.randint(100, 999)} Main Street, Suite {random.randint(100, 999)}, {self.faker.city()}, {self.faker.state_abbr()} {self.faker.zipcode()}"
                    },
                    {
                        "method": "Fax",
                        "number": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                    },
                    {
                        "method": "Online",
                        "website": f"www.{self.faker.domain_name()}/appeals"
                    }
                ],
                "required_documentation": [
                    "Written appeal request",
                    "Copy of denial notice",
                    "Supporting clinical documentation",
                    "Letter of medical necessity from provider"
                ],
                "expedited_option": random.choice([True, False]),
                "external_review_rights": "You may have the right to an external review if your appeal is denied."
            }
        else:
            return {}
    
    def _generate_additional_info_needed(self) -> List[str]:
        """Generate list of additional information needed."""
        info_items = [
            "Complete medical records for the past 6 months",
            "Recent lab results related to the condition",
            "Imaging reports",
            "Previous treatment history and outcomes",
            "Detailed letter of medical necessity",
            "Clinical notes documenting failure of conservative treatment",
            "Specialist consultation notes",
            "Current medication list",
            "Functional assessment results",
            "Treatment plan with expected outcomes and duration"
        ]
        
        # Select 2-5 items
        num_items = random.randint(2, 5)
        
        return random.sample(info_items, num_items)
    
    def _generate_financial_details(self, billed_amount: float) -> Dict[str, float]:
        """Generate financial details for a claim."""
        # Generate allowed amount (typically less than billed)
        allowed_amount = round(billed_amount * random.uniform(0.4, 0.8), 2)
        
        # Generate member responsibility
        deductible = round(allowed_amount * random.uniform(0, 0.3), 2)
        coinsurance = round((allowed_amount - deductible) * random.uniform(0, 0.3), 2)
        copay = random.choice([0, 20, 25, 30, 40, 50, 75, 100]) if random.random() > 0.5 else 0
        
        # Calculate plan paid amount
        plan_paid = round(allowed_amount - deductible - coinsurance - copay, 2)
        
        # Ensure plan_paid is not negative
        if plan_paid < 0:
            plan_paid = 0
            coinsurance = allowed_amount - deductible - copay
        
        return {
            "billed_amount": billed_amount,
            "allowed_amount": allowed_amount,
            "deductible": deductible,
            "coinsurance": coinsurance,
            "copay": copay,
            "plan_paid": plan_paid,
            "member_responsibility": round(deductible + coinsurance + copay, 2)
        }
    
    def _generate_claim_denial_reason(self) -> str:
        """Generate reason for claim denial."""
        reasons = [
            "Service not covered under the member's plan",
            "Prior authorization required but not obtained",
            "Claim submitted after filing deadline",
            "Duplicate claim",
            "Service provided by out-of-network provider",
            "Insufficient information provided on claim",
            "Member not eligible at time of service",
            "Service considered experimental or investigational",
            "Service not medically necessary based on clinical review",
            "Diagnosis does not support the service provided",
            "Service exceeds plan frequency limitations",
            "Bundled service billed separately"
        ]
        
        return random.choice(reasons)
    
    def _generate_claim_pending_reason(self) -> str:
        """Generate reason for pending claim."""
        reasons = [
            "Awaiting additional information from provider",
            "Coordination of benefits information needed",
            "Medical necessity review in progress",
            "Awaiting medical records",
            "Claim under review for proper coding",
            "Verification of eligibility in process",
            "Awaiting information from member",
            "Third-party liability investigation",
            "Claim requires manual processing",
            "Specialist review required"
        ]
        
        return random.choice(reasons)
    
    def _generate_partial_payment_reason(self) -> str:
        """Generate reason for partial claim payment."""
        reasons = [
            "Some services not covered under the member's plan",
            "Portion of charge exceeds allowed amount",
            "Multiple procedure payment reduction applied",
            "Some services denied as not medically necessary",
            "Service partially covered due to plan limitations",
            "Bundled services separately billed",
            "Portion of stay/service not authorized",
            "Global period payment adjustment",
            "Assistant surgeon payment reduction",
            "Frequency limitation exceeded for some services"
        ]
        
        return random.choice(reasons)
    
    def _generate_next_steps(self, status: str) -> List[str]:
        """Generate next steps based on claim status."""
        if status == 'Denied':
            steps = [
                "Review denial reason carefully",
                "Contact provider for additional information if needed",
                "Submit appeal within timeframe if you disagree",
                "Provide any requested documentation",
                "Consider requesting peer-to-peer review"
            ]
        elif status == 'Pending':
            steps = [
                "No action needed at this time",
                "Await final determination",
                "Provide any requested information promptly",
                "Check claim status again in 7-10 business days",
                "Contact customer service if pending more than 30 days"
            ]
        elif status == 'Partially Paid':
            steps = [
                "Review explanation of benefits carefully",
                "Contact provider regarding balance billing questions",
                "Submit appeal for denied portion if appropriate",
                "Pay member responsibility amount to provider",
                "Request detailed breakdown if needed"
            ]
        else:
            steps = []
        
        # Select 2-4 steps
        num_steps = random.randint(2, 4)
        
        return random.sample(steps, min(num_steps, len(steps)))
    
    def _generate_appeal_upheld_rationale(self) -> str:
        """Generate rationale for upholding original denial."""
        rationales = [
            "After thorough review, the original determination was appropriate based on the member's benefits and medical necessity criteria.",
            "The additional information provided does not support the medical necessity of the requested service.",
            "The service remains non-covered under the member's benefit plan as outlined in the plan documents.",
            "The service does not meet evidence-based guidelines for the member's condition even with the additional information provided.",
            "The documentation provided does not demonstrate that the service is required for the member's medical condition.",
            "The requested service remains experimental/investigational for the member's diagnosis based on current medical literature."
        ]
        
        return random.choice(rationales)
    
    def _generate_appeal_overturned_rationale(self) -> str:
        """Generate rationale for overturning original denial."""
        rationales = [
            "Based on the additional clinical information provided, the service meets medical necessity criteria.",
            "Upon further review, the requested service is a covered benefit under the member's plan.",
            "The appeal provided sufficient documentation to demonstrate the medical necessity of the requested service.",
            "After specialist review, the service is determined to be appropriate for the member's condition.",
            "The additional information clarified that the service follows evidence-based guidelines for the member's condition.",
            "Documentation provided with the appeal demonstrates that alternative treatments have been tried without success."
        ]
        
        return random.choice(rationales)
    
    def _generate_appeal_partially_overturned_rationale(self) -> str:
        """Generate rationale for partially overturning original denial."""
        rationales = [
            "Based on the additional information, a modified service/duration is approved that meets medical necessity criteria.",
            "Partial approval granted for reduced frequency/duration based on clinical guidelines for the member's condition.",
            "Some components of the requested service are now approved, while others remain non-covered benefits.",
            "Alternative service approved that is medically appropriate based on the additional documentation provided.",
            "Partial approval based on the member's specific clinical circumstances as documented in the appeal.",
            "Modified authorization granted that aligns with evidence-based guidelines for the member's condition."
        ]
        
        return random.choice(rationales)
    
    def _generate_next_level_appeal(self, determination: str) -> Dict[str, Any]:
        """Generate information about next level appeal options."""
        if determination in ['Upheld', 'Partially Overturned']:
            return {
                "level": random.choice(["Second Level Internal Appeal", "External Independent Review"]),
                "deadline": f"{random.randint(30, 180)} days from the date of this notice",
                "submission_methods": [
                    {
                        "method": "Mail",
                        "address": f"{random.randint(100, 999)} Main Street, Suite {random.randint(100, 999)}, {self.faker.city()}, {self.faker.state_abbr()} {self.faker.zipcode()}"
                    },
                    {
                        "method": "Fax",
                        "number": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                    }
                ],
                "required_documentation": [
                    "Written appeal request",
                    "Copy of all previous denial notices",
                    "Any new supporting clinical documentation",
                    "Specific reason for disagreement with appeal decision"
                ],
                "expedited_option": random.choice([True, False])
            }
        else:
            return {}
    
    def _generate_financial_adjustment(self, original_amount: float) -> Dict[str, float]:
        """Generate financial adjustment details for overturned appeals."""
        if original_amount <= 0:
            original_amount = random.randint(100, 5000)
            
        # For overturned appeals, generate the adjustment
        adjusted_amount = round(original_amount * random.uniform(0.7, 1.0), 2)
        
        # Generate member responsibility
        member_responsibility = round(adjusted_amount * random.uniform(0, 0.3), 2)
        
        # Calculate plan paid amount
        plan_paid = round(adjusted_amount - member_responsibility, 2)
        
        return {
            "original_amount": original_amount,
            "adjusted_amount": adjusted_amount,
            "plan_paid": plan_paid,
            "member_responsibility": member_responsibility,
            "payment_date": (datetime.now() + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d")
        }