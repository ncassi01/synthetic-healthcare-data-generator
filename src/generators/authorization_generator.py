"""
Prior Authorization generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic prior authorization data.
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
from src.models.insurance import PriorAuthorization, AuthorizationStatus, ServiceLine, ServiceType


class AuthorizationGenerator(BaseGenerator):
    """Generator for synthetic prior authorization data."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the authorization generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract authorization configuration
        self.auth_config = config.get('authorization_config', {})
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
        
        # Common service codes (CPT/HCPCS) that typically require authorization
        self.service_codes = {
            ServiceType.INPATIENT: [
                {"code": "99221", "description": "Initial hospital care, low complexity"},
                {"code": "99222", "description": "Initial hospital care, moderate complexity"},
                {"code": "99223", "description": "Initial hospital care, high complexity"}
            ],
            ServiceType.IMAGING: [
                {"code": "70450", "description": "CT scan, head/brain, without contrast"},
                {"code": "70460", "description": "CT scan, head/brain, with contrast"},
                {"code": "70470", "description": "CT scan, head/brain, without & with contrast"},
                {"code": "70551", "description": "MRI, brain, without contrast"},
                {"code": "70552", "description": "MRI, brain, with contrast"},
                {"code": "70553", "description": "MRI, brain, without & with contrast"},
                {"code": "72148", "description": "MRI, spinal canal, lumbar, without contrast"},
                {"code": "73721", "description": "MRI, joint of lower extremity, without contrast"}
            ],
            ServiceType.OUTPATIENT: [
                {"code": "43239", "description": "Upper GI endoscopy, biopsy"},
                {"code": "45378", "description": "Colonoscopy, diagnostic"},
                {"code": "45380", "description": "Colonoscopy with biopsy"},
                {"code": "66984", "description": "Cataract removal with lens insertion"}
            ],
            ServiceType.THERAPY: [
                {"code": "97110", "description": "Therapeutic exercises, 15 minutes"},
                {"code": "97112", "description": "Neuromuscular reeducation, 15 minutes"},
                {"code": "97116", "description": "Gait training, 15 minutes"},
                {"code": "97140", "description": "Manual therapy, 15 minutes"}
            ],
            ServiceType.MENTAL_HEALTH: [
                {"code": "90791", "description": "Psychiatric diagnostic evaluation"},
                {"code": "90837", "description": "Psychotherapy, 60 minutes"},
                {"code": "90853", "description": "Group psychotherapy"}
            ],
            ServiceType.PHARMACY: [
                {"code": "J0129", "description": "Injection, abatacept, 10 mg"},
                {"code": "J0178", "description": "Injection, aflibercept, 1 mg"},
                {"code": "J0585", "description": "Injection, onabotulinumtoxinA, 1 unit"},
                {"code": "J1745", "description": "Injection, infliximab, 10 mg"},
                {"code": "J2323", "description": "Injection, natalizumab, 1 mg"},
                {"code": "J2350", "description": "Injection, ocrelizumab, 1 mg"}
            ]
        }
        
        # Clinical justification templates
        self.clinical_justifications = {
            ServiceType.INPATIENT: [
                "Patient requires inpatient admission due to {condition} with symptoms of {symptom1} and {symptom2}. Outpatient management has been unsuccessful.",
                "Patient presents with acute exacerbation of {condition} requiring continuous monitoring and IV medications.",
                "Patient has severe {condition} with complications including {symptom1} and {symptom2}, necessitating inpatient care."
            ],
            ServiceType.IMAGING: [
                "Patient with {condition} presents with {symptom1} and {symptom2}. Imaging needed to rule out {complication}.",
                "Follow-up imaging for known {condition} to assess disease progression after {timeframe} of treatment.",
                "Patient with history of {condition} now presenting with new symptoms of {symptom1}. Imaging needed for diagnosis."
            ],
            ServiceType.OUTPATIENT: [
                "Patient with {condition} requires {procedure} due to persistent symptoms of {symptom1} despite conservative management.",
                "Diagnostic {procedure} indicated for patient with {condition} to evaluate for {complication}.",
                "Patient with {condition} and abnormal findings on {test} requires {procedure} for further evaluation."
            ],
            ServiceType.THERAPY: [
                "Patient with {condition} requires physical therapy to improve mobility and function after {event}.",
                "Patient with {condition} has functional deficits in {area} requiring therapeutic intervention.",
                "Patient recovering from {event} needs therapy to address {symptom1} and improve activities of daily living."
            ],
            ServiceType.MENTAL_HEALTH: [
                "Patient with {condition} experiencing worsening symptoms of {symptom1} and {symptom2} requiring intensive therapy.",
                "Patient with history of {condition} now experiencing acute {symptom1} with impact on daily functioning.",
                "Patient with {condition} has not responded adequately to outpatient management and requires more intensive intervention."
            ],
            ServiceType.PHARMACY: [
                "Patient with {condition} has failed conventional therapy with {medication1} and {medication2}. Biologic therapy now indicated.",
                "Patient with {condition} has demonstrated intolerance to {medication1} and requires alternative therapy.",
                "Patient with severe {condition} requires {medication} as standard treatments have been ineffective in controlling {symptom1}."
            ]
        }
        
        # Symptoms for clinical justification
        self.symptoms = [
            "pain", "swelling", "fever", "fatigue", "weakness", 
            "numbness", "tingling", "dizziness", "headache", "nausea", 
            "vomiting", "shortness of breath", "chest pain", "palpitations", 
            "abdominal pain", "diarrhea", "constipation", "rash", "itching", 
            "joint pain", "muscle pain", "back pain", "neck pain", "cough", 
            "wheezing", "confusion", "memory loss", "anxiety", "depression", 
            "insomnia", "weight loss", "weight gain", "loss of appetite", 
            "excessive thirst", "frequent urination", "blurred vision", 
            "hearing loss", "difficulty walking", "difficulty speaking"
        ]
        
        # Complications for clinical justification
        self.complications = [
            "infection", "bleeding", "thrombosis", "embolism", "organ failure", 
            "respiratory failure", "renal failure", "hepatic failure", "sepsis", 
            "shock", "malignancy", "metastasis", "fracture", "dislocation", 
            "nerve damage", "vascular damage", "perforation", "obstruction", 
            "rupture", "aneurysm", "stroke", "heart attack", "arrhythmia", 
            "hypertensive crisis", "diabetic ketoacidosis", "hypoglycemia", 
            "dehydration", "electrolyte imbalance", "anaphylaxis", "adverse drug reaction"
        ]
        
        # Medications for clinical justification
        self.medications = [
            "acetaminophen", "ibuprofen", "naproxen", "aspirin", "prednisone", 
            "methylprednisolone", "hydrocortisone", "methotrexate", "azathioprine", 
            "hydroxychloroquine", "sulfasalazine", "mesalamine", "leflunomide", 
            "cyclosporine", "tacrolimus", "mycophenolate", "cyclophosphamide", 
            "rituximab", "adalimumab", "etanercept", "infliximab", "certolizumab", 
            "golimumab", "tocilizumab", "abatacept", "ustekinumab", "secukinumab", 
            "ixekizumab", "guselkumab", "tildrakizumab", "risankizumab", "vedolizumab", 
            "natalizumab", "ocrelizumab", "ofatumumab", "eculizumab", "belimumab"
        ]
        
        # Timeframes for clinical justification
        self.timeframes = [
            "1 week", "2 weeks", "3 weeks", "1 month", "2 months", 
            "3 months", "6 months", "1 year", "2 years"
        ]
        
        # Events for clinical justification
        self.events = [
            "surgery", "injury", "fall", "accident", "hospitalization", 
            "illness", "infection", "stroke", "heart attack", "trauma"
        ]
        
        # Areas for clinical justification
        self.areas = [
            "upper extremity", "lower extremity", "back", "neck", "shoulder", 
            "hip", "knee", "ankle", "wrist", "hand", "foot", "spine", 
            "abdomen", "chest", "head", "face"
        ]
        
        # Tests for clinical justification
        self.tests = [
            "blood test", "urine test", "X-ray", "CT scan", "MRI", 
            "ultrasound", "endoscopy", "colonoscopy", "biopsy", "ECG", 
            "echocardiogram", "stress test", "pulmonary function test", 
            "sleep study", "nerve conduction study", "EMG"
        ]
        
        # Service type price ranges
        self.service_price_ranges = {
            ServiceType.INPATIENT: (1500, 10000),
            ServiceType.OUTPATIENT: (200, 1000),
            ServiceType.DIAGNOSTIC: (50, 500),
            ServiceType.IMAGING: (200, 2500),
            ServiceType.PHARMACY: (500, 5000),
            ServiceType.THERAPY: (75, 200),
            ServiceType.MENTAL_HEALTH: (100, 300)
        }
    
    def generate(self, count: int, members: List[Dict]) -> List[PriorAuthorization]:
        """
        Generate synthetic prior authorization data.
        
        Args:
            count: Number of authorizations to generate.
            members: List of member data to associate authorizations with.
            
        Returns:
            List of generated PriorAuthorization objects.
        """
        self.logger.info(f"Generating {count} prior authorizations")
        authorizations = []
        
        # Ensure we have members to work with
        if not members:
            self.logger.warning("No members provided for authorization generation")
            return authorizations
        
        for i in range(count):
            # Select a random member
            member = random.choice(members)
            authorization = self._generate_authorization(i, member)
            authorizations.append(authorization)
            
        self.logger.info(f"Generated {len(authorizations)} prior authorizations")
        return authorizations
    
    def _generate_authorization(self, index: int, member: Dict) -> PriorAuthorization:
        """
        Generate a single synthetic prior authorization.
        
        Args:
            index: Index of the authorization (used for ID generation).
            member: Member data to associate the authorization with.
            
        Returns:
            A synthetic PriorAuthorization object.
        """
        # Generate authorization ID
        auth_id = f"AUTH{index:08d}"
        
        # Get member ID
        member_id = member.get('id', f"MEM{random.randint(10000, 99999)}")
        
        # Generate provider ID
        provider_id = f"PRV{random.randint(10000, 99999)}"
        
        # Generate dates
        today = date.today()
        date_requested = today - timedelta(days=random.randint(1, 180))
        
        # Generate authorization status
        status_weights = self.auth_config.get('status_distribution', {
            AuthorizationStatus.SUBMITTED.value: 0.05,
            AuthorizationStatus.PENDING.value: 0.15,
            AuthorizationStatus.ADDITIONAL_INFO_NEEDED.value: 0.1,
            AuthorizationStatus.APPROVED.value: 0.6,
            AuthorizationStatus.DENIED.value: 0.05,
            AuthorizationStatus.APPEALED.value: 0.05
        })
        
        status_value = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values()),
            k=1
        )[0]
        status = AuthorizationStatus(status_value)
        
        # Generate authorization type
        auth_type_options = ["procedure", "medication", "equipment", "imaging", "therapy", "inpatient"]
        auth_type_weights = [0.3, 0.3, 0.1, 0.15, 0.1, 0.05]
        authorization_type = random.choices(auth_type_options, weights=auth_type_weights, k=1)[0]
        
        # Map authorization type to service type
        service_type_map = {
            "procedure": [ServiceType.OUTPATIENT],
            "medication": [ServiceType.PHARMACY],
            "equipment": [ServiceType.OUTPATIENT],
            "imaging": [ServiceType.IMAGING],
            "therapy": [ServiceType.THERAPY, ServiceType.MENTAL_HEALTH],
            "inpatient": [ServiceType.INPATIENT]
        }
        
        service_type_options = service_type_map.get(authorization_type, [random.choice(list(ServiceType))])
        service_type = random.choice(service_type_options)
        
        # Generate service lines
        num_service_lines = random.randint(1, 3)
        service_lines = []
        
        for _ in range(num_service_lines):
            service_line = self._generate_service_line(service_type)
            service_lines.append(service_line)
        
        # Generate diagnosis codes
        num_diagnosis_codes = random.randint(1, 3)
        diagnosis_codes = random.sample(self.diagnosis_codes, num_diagnosis_codes)
        
        # Generate clinical justification
        clinical_justification = self._generate_clinical_justification(service_type, diagnosis_codes[0] if diagnosis_codes else None)
        
        # Generate decision information based on status
        date_decision = None
        decision_rationale = None
        expiration_date = None
        
        if status in [AuthorizationStatus.APPROVED, AuthorizationStatus.DENIED]:
            # Generate decision date
            date_decision = date_requested + timedelta(days=random.randint(1, 14))
            
            if status == AuthorizationStatus.APPROVED:
                # Generate approval rationale
                approval_rationales = [
                    "Medical necessity criteria met",
                    "Meets plan coverage guidelines",
                    "Appropriate for diagnosis",
                    "Standard of care for condition",
                    "Prior treatments failed",
                    "No alternative treatments available"
                ]
                decision_rationale = random.choice(approval_rationales)
                
                # Generate expiration date (typically 3-12 months from approval)
                expiration_date = date_decision + timedelta(days=random.randint(90, 365))
                
            elif status == AuthorizationStatus.DENIED:
                # Generate denial rationale
                denial_rationales = [
                    "Medical necessity criteria not met",
                    "Experimental/investigational treatment",
                    "Not covered by plan",
                    "Alternative treatments not tried",
                    "Insufficient clinical information provided",
                    "Out of network provider",
                    "Service can be provided at lower level of care"
                ]
                decision_rationale = random.choice(denial_rationales)
        
        elif status == AuthorizationStatus.ADDITIONAL_INFO_NEEDED:
            # Generate additional info needed rationale
            additional_info_rationales = [
                "Clinical notes required",
                "Test results needed",
                "Treatment history required",
                "Specialist consultation needed",
                "Detailed prescription information required",
                "Documentation of failed treatments needed"
            ]
            decision_rationale = random.choice(additional_info_rationales)
        
        # Create and return authorization
        return PriorAuthorization(
            id=auth_id,
            member_id=member_id,
            provider_id=provider_id,
            date_requested=date_requested,
            status=status,
            service_lines=service_lines,
            diagnosis_codes=diagnosis_codes,
            clinical_justification=clinical_justification,
            authorization_type=authorization_type,
            date_decision=date_decision,
            decision_rationale=decision_rationale,
            expiration_date=expiration_date
        )
    
    def _generate_service_line(self, service_type: ServiceType) -> ServiceLine:
        """
        Generate a service line for an authorization.
        
        Args:
            service_type: Type of service.
            
        Returns:
            A synthetic ServiceLine object.
        """
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
            quantity = random.randint(1, 12)  # For therapy, this might be number of sessions
        
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
    
    def _generate_clinical_justification(self, service_type: ServiceType, diagnosis_code: Optional[str] = None) -> str:
        """
        Generate clinical justification for an authorization.
        
        Args:
            service_type: Type of service.
            diagnosis_code: ICD-10 diagnosis code.
            
        Returns:
            Clinical justification text.
        """
        # Map diagnosis code to condition name (simplified for this example)
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
        
        # Get condition name or use a generic one
        condition = condition_map.get(diagnosis_code, random.choice(list(condition_map.values()))) if diagnosis_code else random.choice(list(condition_map.values()))
        
        # Get justification template for service type or use a generic one
        if service_type in self.clinical_justifications:
            template = random.choice(self.clinical_justifications[service_type])
        else:
            template = "Patient with {condition} requires treatment due to {symptom1} and {symptom2}."
        
        # Fill in template placeholders
        justification = template.format(
            condition=condition,
            symptom1=random.choice(self.symptoms),
            symptom2=random.choice(self.symptoms),
            complication=random.choice(self.complications),
            medication1=random.choice(self.medications),
            medication2=random.choice(self.medications),
            medication=random.choice(self.medications),
            timeframe=random.choice(self.timeframes),
            event=random.choice(self.events),
            area=random.choice(self.areas),
            test=random.choice(self.tests),
            procedure=service_type.value.replace("_", " ")
        )
        
        return justification