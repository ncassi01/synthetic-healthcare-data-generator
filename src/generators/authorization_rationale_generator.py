"""
Authorization rationale generator for the synthetic healthcare data generator.

This module generates synthetic authorization rationales based on authorization data.
"""

import json
import logging
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from faker import Faker

from src.generators.base_generator import BaseGenerator
from src.models.narrative import AuthorizationRationale


class AuthorizationRationaleGenerator(BaseGenerator):
    """Generator for synthetic authorization rationales."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the authorization rationale generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            self.faker.seed_instance(seed)
        
        # Load templates and clinical guidelines
        self.templates = self._load_templates()
        self.clinical_guidelines = self._load_clinical_guidelines()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """
        Load authorization rationale templates from the configuration.
        
        Returns:
            Dictionary of templates for different sections of the rationale.
        """
        templates = {}
        
        # Default templates if not provided in config
        default_templates = {
            "clinical_summary": [
                "Patient is a {age}-year-old {gender} with a history of {conditions}. The patient has been experiencing {symptoms} for {duration}. Previous treatments include {previous_treatments}, which have resulted in {treatment_results}.",
                "{age}-year-old {gender} with {conditions} presenting with {symptoms} for {duration}. Patient has tried {previous_treatments} with {treatment_results}.",
                "This {age}-year-old {gender} has a documented history of {conditions}. Current symptoms include {symptoms}, which have been present for {duration}. The patient has undergone {previous_treatments} with {treatment_results}."
            ],
            "medical_necessity": [
                "The requested {service} is medically necessary for this patient due to {necessity_reason}. Standard treatments including {standard_treatments} have been {treatment_outcome}. The requested service is consistent with {guideline_reference} for patients with {condition_specifics}.",
                "Medical necessity for {service} is established based on {necessity_reason}. The patient has failed {standard_treatments}, which resulted in {treatment_outcome}. According to {guideline_reference}, {service} is indicated for patients with {condition_specifics}.",
                "The {service} is medically necessary because {necessity_reason}. Previous attempts with {standard_treatments} have been {treatment_outcome}. Clinical guidelines ({guideline_reference}) support the use of {service} in patients with {condition_specifics}."
            ]
        }
        
        # Use templates from config if available, otherwise use defaults
        auth_templates = self.config.get("authorization_rationale_templates", default_templates)
        
        for section, section_templates in auth_templates.items():
            templates[section] = section_templates
        
        return templates
    
    def _load_clinical_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """
        Load clinical guidelines for different conditions and services.
        
        Returns:
            Dictionary mapping conditions to guidelines.
        """
        # Default clinical guidelines if not provided in config
        default_guidelines = {
            "diabetes": {
                "continuous glucose monitoring": {
                    "guideline_references": [
                        "American Diabetes Association Standards of Care",
                        "Endocrine Society Clinical Practice Guidelines",
                        "International Consensus on CGM Use"
                    ],
                    "criteria": [
                        "Type 1 diabetes requiring multiple daily insulin injections",
                        "History of severe hypoglycemia or hypoglycemia unawareness",
                        "Wide glycemic excursions despite optimal insulin therapy",
                        "Pregnancy with pre-existing diabetes"
                    ],
                    "evidence_references": [
                        "Beck et al. (2017). Effect of CGM on Glycemic Control in Adults With Type 1 Diabetes",
                        "Battelino et al. (2019). Clinical Targets for CGM Data Interpretation",
                        "Lind et al. (2017). CGM vs Conventional Therapy for Glycemic Control"
                    ],
                    "alternatives": [
                        "Self-monitoring of blood glucose (fingerstick)",
                        "Intermittent CGM use",
                        "Insulin pump therapy without CGM"
                    ]
                },
                "insulin pump therapy": {
                    "guideline_references": [
                        "American Diabetes Association Standards of Care",
                        "American Association of Clinical Endocrinologists Guidelines",
                        "International Consensus on Insulin Pump Therapy"
                    ],
                    "criteria": [
                        "Suboptimal glycemic control despite multiple daily injections",
                        "Recurrent severe hypoglycemia",
                        "Wide glycemic excursions",
                        "Dawn phenomenon not managed with other insulin regimens",
                        "Need for increased insulin delivery flexibility"
                    ],
                    "evidence_references": [
                        "Pickup et al. (2014). Insulin Pump Therapy for Type 1 Diabetes",
                        "Reznik et al. (2014). Insulin Pump Treatment Compared with Multiple Daily Injections",
                        "Bergenstal et al. (2013). Threshold-Based Insulin-Pump Interruption for Hypoglycemia"
                    ],
                    "alternatives": [
                        "Multiple daily injections with long-acting and rapid-acting insulin",
                        "Basal-bolus injection therapy with insulin pens",
                        "Fixed-dose combination insulins"
                    ]
                }
            },
            "asthma": {
                "biologics": {
                    "guideline_references": [
                        "Global Initiative for Asthma (GINA) Guidelines",
                        "American Thoracic Society Guidelines",
                        "European Respiratory Society Guidelines"
                    ],
                    "criteria": [
                        "Severe persistent asthma (Step 5 therapy)",
                        "Exacerbations despite high-dose inhaled corticosteroids and LABA",
                        "Elevated blood eosinophil count or FeNO",
                        "Need for maintenance oral corticosteroids"
                    ],
                    "evidence_references": [
                        "Castro et al. (2018). Dupilumab Efficacy and Safety in Moderate-to-Severe Uncontrolled Asthma",
                        "Bleecker et al. (2016). Benralizumab for Severe Eosinophilic Asthma",
                        "Ortega et al. (2014). Mepolizumab Treatment in Patients with Severe Eosinophilic Asthma"
                    ],
                    "alternatives": [
                        "High-dose inhaled corticosteroids with LABA",
                        "Addition of tiotropium",
                        "Maintenance oral corticosteroids",
                        "Leukotriene modifiers"
                    ]
                },
                "bronchial thermoplasty": {
                    "guideline_references": [
                        "Global Initiative for Asthma (GINA) Guidelines",
                        "American Thoracic Society Guidelines",
                        "British Thoracic Society Guidelines"
                    ],
                    "criteria": [
                        "Severe persistent asthma not controlled with maximal medical therapy",
                        "Age 18 years or older",
                        "FEV1 > 60% predicted",
                        "Not responsive to biologics or not eligible for biologic therapy"
                    ],
                    "evidence_references": [
                        "Castro et al. (2010). Effectiveness and Safety of Bronchial Thermoplasty in the Treatment of Severe Asthma",
                        "Wechsler et al. (2013). Bronchial Thermoplasty: Long-term Safety and Effectiveness",
                        "Chupp et al. (2017). Long-term Outcomes of Bronchial Thermoplasty"
                    ],
                    "alternatives": [
                        "Biologic therapy",
                        "Maintenance oral corticosteroids",
                        "Maximal inhaled therapy",
                        "Participation in clinical trials"
                    ]
                }
            },
            "chronic pain": {
                "spinal cord stimulator": {
                    "guideline_references": [
                        "American Society of Interventional Pain Physicians Guidelines",
                        "North American Neuromodulation Society Guidelines",
                        "International Neuromodulation Society Guidelines"
                    ],
                    "criteria": [
                        "Failed back surgery syndrome or complex regional pain syndrome",
                        "Neuropathic pain refractory to conventional medical management",
                        "Successful trial stimulation (>50% pain reduction)",
                        "No untreated substance use disorder",
                        "Psychological clearance"
                    ],
                    "evidence_references": [
                        "Kumar et al. (2007). Spinal Cord Stimulation versus Conventional Medical Management",
                        "Kapural et al. (2015). Novel 10-kHz High-frequency Therapy for Chronic Pain",
                        "North et al. (2005). Spinal Cord Stimulation versus Reoperation for Failed Back Surgery Syndrome"
                    ],
                    "alternatives": [
                        "Comprehensive pain rehabilitation program",
                        "Continued conservative management",
                        "Intrathecal drug delivery system",
                        "Peripheral nerve stimulation"
                    ]
                },
                "intrathecal pain pump": {
                    "guideline_references": [
                        "Polyanalgesic Consensus Conference Guidelines",
                        "American Society of Interventional Pain Physicians Guidelines",
                        "American Pain Society Guidelines"
                    ],
                    "criteria": [
                        "Chronic intractable pain not adequately controlled with systemic opioids",
                        "Failure of conservative treatments and less invasive options",
                        "Positive response to intrathecal trial",
                        "No active infection or coagulopathy",
                        "Psychological clearance"
                    ],
                    "evidence_references": [
                        "Deer et al. (2017). The Polyanalgesic Consensus Conference (PACC)",
                        "Hamza et al. (2015). Prospective Study of Intrathecal Ziconotide for Chronic Pain",
                        "Smith et al. (2002). Randomized Clinical Trial of an Implantable Drug Delivery System"
                    ],
                    "alternatives": [
                        "Spinal cord stimulation",
                        "Comprehensive pain rehabilitation",
                        "Continued systemic analgesics",
                        "Nerve blocks and ablation procedures"
                    ]
                }
            },
            "heart failure": {
                "left ventricular assist device": {
                    "guideline_references": [
                        "American College of Cardiology/American Heart Association Guidelines",
                        "International Society for Heart and Lung Transplantation Guidelines",
                        "European Society of Cardiology Guidelines"
                    ],
                    "criteria": [
                        "NYHA Class IIIB or IV heart failure refractory to optimal medical therapy",
                        "LVEF < 25%",
                        "Peak VO2 < 14 ml/kg/min",
                        "Inotrope dependence or recurrent hospitalizations",
                        "No significant right ventricular failure or other contraindications"
                    ],
                    "evidence_references": [
                        "Slaughter et al. (2009). Advanced Heart Failure Treated with Continuous-Flow LVAD",
                        "Rogers et al. (2017). The ROADMAP Study of the HeartMate II LVAD",
                        "Mehra et al. (2017). A Fully Magnetically Levitated Circulatory Pump for Advanced Heart Failure"
                    ],
                    "alternatives": [
                        "Heart transplantation",
                        "Continued optimal medical therapy",
                        "Palliative care and hospice",
                        "Investigational therapies"
                    ]
                },
                "cardiac resynchronization therapy": {
                    "guideline_references": [
                        "American College of Cardiology/American Heart Association Guidelines",
                        "Heart Rhythm Society Guidelines",
                        "European Society of Cardiology Guidelines"
                    ],
                    "criteria": [
                        "NYHA Class II-IV heart failure on optimal medical therapy",
                        "LVEF ≤ 35%",
                        "QRS duration ≥ 130 ms (especially LBBB)",
                        "Sinus rhythm (typically)",
                        "Expected survival > 1 year"
                    ],
                    "evidence_references": [
                        "Bristow et al. (2004). Cardiac-Resynchronization Therapy with or without an ICD",
                        "Moss et al. (2009). Cardiac-Resynchronization Therapy for Mild Heart Failure",
                        "Tang et al. (2010). Cardiac-Resynchronization Therapy for Mild-to-Moderate Heart Failure"
                    ],
                    "alternatives": [
                        "Continued optimal medical therapy alone",
                        "ICD without CRT capability",
                        "Heart transplantation evaluation",
                        "LVAD evaluation"
                    ]
                }
            }
        }
        
        # Use clinical guidelines from config if available, otherwise use defaults
        return self.config.get("clinical_guidelines", default_guidelines)
    
    def generate(self, authorizations: List[Dict], members: List[Dict], count: Optional[int] = None) -> List[AuthorizationRationale]:
        """
        Generate synthetic authorization rationales based on authorization data.
        
        Args:
            authorizations: List of authorization dictionaries to generate rationales for.
            members: List of member dictionaries to reference.
            count: Optional number of rationales to generate. If not provided,
                   will generate for all authorizations.
                   
        Returns:
            List of generated authorization rationales.
        """
        if not authorizations:
            self.logger.warning("No authorizations provided for rationale generation")
            return []
        
        rationales = []
        
        # Create a lookup for members by ID
        member_lookup = {member["id"]: member for member in members}
        
        # Determine which authorizations to generate rationales for
        selected_authorizations = authorizations
        if count is not None and count < len(authorizations):
            selected_authorizations = random.sample(authorizations, count)
        
        for auth in selected_authorizations:
            # Get the member data
            member_id = auth.get("member_id")
            member = member_lookup.get(member_id)
            
            if not member:
                self.logger.warning(f"Member {member_id} not found for authorization {auth.get('id')}")
                continue
            
            # Generate the rationale
            rationale = self._generate_rationale_for_authorization(auth, member)
            rationales.append(rationale)
        
        return rationales
    
    def _generate_rationale_for_authorization(self, authorization: Dict, member: Dict) -> AuthorizationRationale:
        """
        Generate an authorization rationale for a specific authorization.
        
        Args:
            authorization: Authorization dictionary to generate rationale for.
            member: Member dictionary for the patient.
            
        Returns:
            Generated authorization rationale.
        """
        # Get authorization details
        auth_id = authorization.get("id")
        member_id = authorization.get("member_id")
        provider_id = authorization.get("provider_id")
        
        # Get service details
        service_lines = authorization.get("service_lines", [])
        service_description = service_lines[0].get("description", "requested service") if service_lines else "requested service"
        service_type = service_lines[0].get("service_type", "procedure") if service_lines else "procedure"
        
        # Get diagnosis codes
        diagnosis_codes = authorization.get("diagnosis_codes", [])
        
        # Get member details
        age = member.get("age", 50)
        gender = member.get("demographics", {}).get("gender", "female")
        conditions = member.get("conditions", [])
        
        # Generate date (usually same as or shortly after authorization request date)
        auth_date = authorization.get("date_requested")
        if isinstance(auth_date, str):
            try:
                auth_date = datetime.fromisoformat(auth_date)
            except ValueError:
                auth_date = datetime.now() - timedelta(days=random.randint(1, 30))
        else:
            auth_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        # Generate rationale date (0-3 days after authorization request)
        days_after = random.randint(0, 3)
        rationale_date = auth_date + timedelta(days=days_after)
        
        # Generate clinical summary
        clinical_summary = self._generate_clinical_summary(age, gender, conditions, service_description)
        
        # Generate medical necessity justification
        medical_necessity = self._generate_medical_necessity(service_description, conditions, service_type)
        
        # Generate evidence references
        evidence_references = self._generate_evidence_references(conditions, service_description)
        
        # Generate guidelines referenced
        guidelines_referenced = self._generate_guidelines_referenced(conditions, service_description)
        
        # Generate alternatives considered
        alternatives_considered = self._generate_alternatives_considered(conditions, service_description)
        
        # Create the authorization rationale
        rationale = AuthorizationRationale(
            id=f"RAT{uuid.uuid4().hex[:8]}",
            authorization_id=auth_id,
            member_id=member_id,
            provider_id=provider_id,
            date_created=rationale_date,
            clinical_summary=clinical_summary,
            medical_necessity=medical_necessity,
            evidence_references=evidence_references,
            guidelines_referenced=guidelines_referenced,
            alternatives_considered=alternatives_considered
        )
        
        return rationale
    
    def _generate_clinical_summary(self, age: int, gender: str, conditions: List[str], 
                                  service: str) -> str:
        """
        Generate the clinical summary section of the rationale.
        
        Args:
            age: Age of the member.
            gender: Gender of the member.
            conditions: List of member's conditions.
            service: Service being requested.
            
        Returns:
            Generated clinical summary.
        """
        if not self.templates.get("clinical_summary"):
            return f"Patient is a {age}-year-old {gender} with a history of {', '.join(conditions)}."
        
        template = random.choice(self.templates["clinical_summary"])
        
        # Format conditions as a comma-separated list
        conditions_text = "no significant medical history"
        if conditions:
            if len(conditions) == 1:
                conditions_text = conditions[0]
            else:
                conditions_text = ", ".join(conditions[:-1]) + " and " + conditions[-1]
        
        # Generate symptom descriptions
        symptoms = [
            "pain", "fatigue", "shortness of breath", "dizziness", 
            "weakness", "numbness", "swelling", "limited mobility"
        ]
        selected_symptoms = random.sample(symptoms, min(3, len(symptoms)))
        symptoms_text = ", ".join(selected_symptoms)
        
        # Generate duration
        durations = [
            f"{random.randint(1, 11)} months",
            f"{random.randint(1, 5)} years",
            "several months",
            "over a year",
            "an extended period"
        ]
        duration = random.choice(durations)
        
        # Generate previous treatments
        treatments = [
            "conservative management", "physical therapy", "medication trials",
            "lifestyle modifications", "injections", "standard therapies",
            "first-line treatments", "non-invasive interventions"
        ]
        selected_treatments = random.sample(treatments, min(3, len(treatments)))
        previous_treatments = ", ".join(selected_treatments)
        
        # Generate treatment results
        results = [
            "minimal improvement", "inadequate relief", "partial response",
            "temporary benefit only", "continued symptoms", "intolerable side effects",
            "disease progression despite therapy", "failure to achieve therapeutic goals"
        ]
        treatment_results = random.choice(results)
        
        # Replace placeholders in the template
        summary = template.replace("{age}", str(age))
        summary = summary.replace("{gender}", gender)
        summary = summary.replace("{conditions}", conditions_text)
        summary = summary.replace("{symptoms}", symptoms_text)
        summary = summary.replace("{duration}", duration)
        summary = summary.replace("{previous_treatments}", previous_treatments)
        summary = summary.replace("{treatment_results}", treatment_results)
        
        return summary
    
    def _generate_medical_necessity(self, service: str, conditions: List[str], 
                                   service_type: str) -> str:
        """
        Generate the medical necessity section of the rationale.
        
        Args:
            service: Service being requested.
            conditions: List of member's conditions.
            service_type: Type of service being requested.
            
        Returns:
            Generated medical necessity justification.
        """
        if not self.templates.get("medical_necessity"):
            return f"The {service} is medically necessary based on the patient's clinical presentation and condition."
        
        template = random.choice(self.templates["medical_necessity"])
        
        # Select a condition to focus on
        condition = random.choice(conditions) if conditions else "the patient's condition"
        
        # Generate necessity reasons
        necessity_reasons = [
            "failure of conservative treatments", 
            "progressive symptoms despite standard therapy",
            "functional limitations affecting activities of daily living",
            "risk of complications without intervention",
            "specific clinical findings indicating need for this service",
            "disease severity meeting established criteria"
        ]
        necessity_reason = random.choice(necessity_reasons)
        
        # Generate standard treatments
        standard_treatments = [
            "first-line medications", "conservative management",
            "physical therapy", "less invasive procedures",
            "standard therapeutic approaches", "conventional treatments"
        ]
        standard_treatment = ", ".join(random.sample(standard_treatments, min(3, len(standard_treatments))))
        
        # Generate treatment outcomes
        treatment_outcomes = [
            "ineffective", "only partially effective",
            "not tolerated due to side effects", "contraindicated",
            "exhausted without adequate improvement", "insufficient to meet therapeutic goals"
        ]
        treatment_outcome = random.choice(treatment_outcomes)
        
        # Generate guideline references
        guideline_references = [
            "current clinical practice guidelines",
            "evidence-based protocols",
            "specialty society recommendations",
            "peer-reviewed literature",
            "standard of care for this condition"
        ]
        guideline_reference = random.choice(guideline_references)
        
        # Generate condition specifics
        condition_specifics = [
            f"refractory {condition}",
            f"moderate to severe {condition}",
            f"{condition} not responsive to standard treatments",
            f"complex presentation of {condition}",
            f"{condition} with specific risk factors"
        ]
        condition_specific = random.choice(condition_specifics)
        
        # Replace placeholders in the template
        necessity = template.replace("{service}", service)
        necessity = necessity.replace("{necessity_reason}", necessity_reason)
        necessity = necessity.replace("{standard_treatments}", standard_treatment)
        necessity = necessity.replace("{treatment_outcome}", treatment_outcome)
        necessity = necessity.replace("{guideline_reference}", guideline_reference)
        necessity = necessity.replace("{condition_specifics}", condition_specific)
        
        return necessity
    
    def _generate_evidence_references(self, conditions: List[str], service: str) -> List[str]:
        """
        Generate evidence references for the rationale.
        
        Args:
            conditions: List of member's conditions.
            service: Service being requested.
            
        Returns:
            List of evidence references.
        """
        # Try to find condition-specific evidence references
        evidence_refs = []
        
        # Convert service to lowercase and simplify for matching
        service_lower = service.lower()
        
        # Check if we have guidelines for any of the conditions
        for condition in conditions:
            condition_lower = condition.lower()
            if condition_lower in self.clinical_guidelines:
                # Check if we have guidelines for this service
                for service_key, guidelines in self.clinical_guidelines[condition_lower].items():
                    if service_key in service_lower or any(word in service_lower for word in service_key.split()):
                        if "evidence_references" in guidelines:
                            # Use the specific evidence references
                            evidence_refs = guidelines["evidence_references"]
                            break
            
            if evidence_refs:
                break
        
        # If no specific evidence references found, generate generic ones
        if not evidence_refs:
            current_year = datetime.now().year
            authors = [
                "Smith et al.", "Johnson et al.", "Williams et al.", "Brown et al.",
                "Jones et al.", "Miller et al.", "Davis et al.", "Garcia et al."
            ]
            journals = [
                "Journal of the American Medical Association",
                "New England Journal of Medicine",
                "The Lancet",
                "British Medical Journal",
                "Annals of Internal Medicine",
                "Journal of Clinical Investigation",
                "Nature Medicine",
                "JAMA Internal Medicine"
            ]
            topics = [
                "Efficacy and Safety of",
                "Clinical Outcomes of",
                "Randomized Controlled Trial of",
                "Long-term Results of",
                "Comparative Effectiveness of",
                "Meta-analysis of",
                "Systematic Review of",
                "Real-world Evidence for"
            ]
            
            # Generate 2-4 generic evidence references
            num_refs = random.randint(2, 4)
            for _ in range(num_refs):
                year = random.randint(current_year - 10, current_year - 1)
                author = random.choice(authors)
                journal = random.choice(journals)
                topic = random.choice(topics)
                
                if conditions:
                    condition = random.choice(conditions)
                    ref = f"{author} ({year}). {topic} {service} in Patients with {condition}. {journal}."
                else:
                    ref = f"{author} ({year}). {topic} {service} in Clinical Practice. {journal}."
                
                evidence_refs.append(ref)
        
        return evidence_refs
    
    def _generate_guidelines_referenced(self, conditions: List[str], service: str) -> List[str]:
        """
        Generate guidelines referenced for the rationale.
        
        Args:
            conditions: List of member's conditions.
            service: Service being requested.
            
        Returns:
            List of guidelines referenced.
        """
        # Try to find condition-specific guideline references
        guideline_refs = []
        
        # Convert service to lowercase and simplify for matching
        service_lower = service.lower()
        
        # Check if we have guidelines for any of the conditions
        for condition in conditions:
            condition_lower = condition.lower()
            if condition_lower in self.clinical_guidelines:
                # Check if we have guidelines for this service
                for service_key, guidelines in self.clinical_guidelines[condition_lower].items():
                    if service_key in service_lower or any(word in service_lower for word in service_key.split()):
                        if "guideline_references" in guidelines:
                            # Use the specific guideline references
                            guideline_refs = guidelines["guideline_references"]
                            break
            
            if guideline_refs:
                break
        
        # If no specific guideline references found, generate generic ones
        if not guideline_refs:
            generic_guidelines = [
                "American College of Physicians Clinical Guidelines",
                "American Medical Association Best Practices",
                "National Institute for Health and Care Excellence (NICE) Guidelines",
                "U.S. Preventive Services Task Force Recommendations",
                "Centers for Medicare & Medicaid Services Coverage Criteria",
                "Specialty Society Appropriate Use Criteria",
                "International Clinical Practice Guidelines",
                "Evidence-Based Clinical Practice Guidelines"
            ]
            
            # Generate 2-3 generic guideline references
            num_refs = random.randint(2, 3)
            guideline_refs = random.sample(generic_guidelines, num_refs)
        
        return guideline_refs
    
    def _generate_alternatives_considered(self, conditions: List[str], service: str) -> List[str]:
        """
        Generate alternatives considered for the rationale.
        
        Args:
            conditions: List of member's conditions.
            service: Service being requested.
            
        Returns:
            List of alternatives considered.
        """
        # Try to find condition-specific alternatives
        alternatives = []
        
        # Convert service to lowercase and simplify for matching
        service_lower = service.lower()
        
        # Check if we have guidelines for any of the conditions
        for condition in conditions:
            condition_lower = condition.lower()
            if condition_lower in self.clinical_guidelines:
                # Check if we have guidelines for this service
                for service_key, guidelines in self.clinical_guidelines[condition_lower].items():
                    if service_key in service_lower or any(word in service_lower for word in service_key.split()):
                        if "alternatives" in guidelines:
                            # Use the specific alternatives
                            alternatives = guidelines["alternatives"]
                            break
            
            if alternatives:
                break
        
        # If no specific alternatives found, generate generic ones
        if not alternatives:
            generic_alternatives = [
                "Continued conservative management",
                "Alternative medication therapy",
                "Less invasive procedural options",
                "Physical therapy and rehabilitation",
                "Lifestyle and behavioral modifications",
                "Watchful waiting with symptomatic treatment",
                "Alternative diagnostic approaches",
                "Non-pharmacological interventions"
            ]
            
            # Generate 2-4 generic alternatives
            num_alts = random.randint(2, 4)
            alternatives = random.sample(generic_alternatives, num_alts)
        
        return alternatives