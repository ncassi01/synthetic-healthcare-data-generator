"""
Authorization Rules Engine for the synthetic healthcare data generator.

This module provides functionality to generate and apply authorization rules
for healthcare services, determining when prior authorization is required
and the criteria for approval or denial.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable

from src.utils.file_utils import load_config


class AuthorizationRule:
    """
    Represents a rule for determining when prior authorization is required.
    """
    
    def __init__(self, rule_id: Optional[str] = None):
        """
        Initialize an authorization rule.
        
        Args:
            rule_id: Rule ID (generated if not provided)
        """
        self.id = rule_id or f"RULE{uuid.uuid4().hex[:8].upper()}"
        self.name = None
        self.description = None
        self.service_type = None
        self.service_codes = []
        self.effective_date = None
        self.end_date = None
        self.criteria = {}
        self.exceptions = []
        self.approval_criteria = {}
        self.denial_criteria = {}
        self.review_type = None
        
    def set_basic_info(self, name: str, description: str, service_type: str) -> None:
        """
        Set basic rule information.
        
        Args:
            name: Rule name
            description: Rule description
            service_type: Type of service (procedure, medication, etc.)
        """
        self.name = name
        self.description = description
        self.service_type = service_type
        
    def set_service_codes(self, codes: List[str]) -> None:
        """
        Set the service codes that this rule applies to.
        
        Args:
            codes: List of service codes (CPT, HCPCS, ICD-10, etc.)
        """
        self.service_codes = codes
        
    def set_effective_period(self, effective_date: datetime, end_date: Optional[datetime] = None) -> None:
        """
        Set the effective period for the rule.
        
        Args:
            effective_date: Date when the rule becomes effective
            end_date: Date when the rule ends (None if ongoing)
        """
        self.effective_date = effective_date
        self.end_date = end_date
        
    def add_criterion(self, name: str, description: str, condition: Dict[str, Any]) -> None:
        """
        Add a criterion for when authorization is required.
        
        Args:
            name: Criterion name
            description: Criterion description
            condition: Dictionary containing the condition logic
        """
        self.criteria[name] = {
            "description": description,
            "condition": condition
        }
        
    def add_exception(self, name: str, description: str, condition: Dict[str, Any]) -> None:
        """
        Add an exception to the rule.
        
        Args:
            name: Exception name
            description: Exception description
            condition: Dictionary containing the exception logic
        """
        self.exceptions.append({
            "name": name,
            "description": description,
            "condition": condition
        })
        
    def add_approval_criterion(self, name: str, description: str, condition: Dict[str, Any]) -> None:
        """
        Add a criterion for approval.
        
        Args:
            name: Criterion name
            description: Criterion description
            condition: Dictionary containing the condition logic
        """
        self.approval_criteria[name] = {
            "description": description,
            "condition": condition
        }
        
    def add_denial_criterion(self, name: str, description: str, condition: Dict[str, Any]) -> None:
        """
        Add a criterion for denial.
        
        Args:
            name: Criterion name
            description: Criterion description
            condition: Dictionary containing the condition logic
        """
        self.denial_criteria[name] = {
            "description": description,
            "condition": condition
        }
        
    def set_review_type(self, review_type: str) -> None:
        """
        Set the type of review required.
        
        Args:
            review_type: Type of review (clinical, administrative, etc.)
        """
        self.review_type = review_type
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the authorization rule to a dictionary.
        
        Returns:
            Dictionary representation of the authorization rule
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "service_type": self.service_type,
            "service_codes": self.service_codes,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "criteria": self.criteria,
            "exceptions": self.exceptions,
            "approval_criteria": self.approval_criteria,
            "denial_criteria": self.denial_criteria,
            "review_type": self.review_type
        }


class AuthorizationDecision:
    """
    Represents a decision made by applying authorization rules.
    """
    
    def __init__(self, decision_id: Optional[str] = None):
        """
        Initialize an authorization decision.
        
        Args:
            decision_id: Decision ID (generated if not provided)
        """
        self.id = decision_id or f"DEC{uuid.uuid4().hex[:8].upper()}"
        self.authorization_id = None
        self.rule_id = None
        self.decision = None
        self.decision_date = None
        self.rationale = None
        self.criteria_met = []
        self.criteria_not_met = []
        self.reviewer_id = None
        self.reviewer_notes = None
        
    def set_basic_info(self, authorization_id: str, rule_id: str, decision: str, decision_date: datetime) -> None:
        """
        Set basic decision information.
        
        Args:
            authorization_id: ID of the authorization request
            rule_id: ID of the rule applied
            decision: Decision (approved, denied, pending)
            decision_date: Date of the decision
        """
        self.authorization_id = authorization_id
        self.rule_id = rule_id
        self.decision = decision
        self.decision_date = decision_date
        
    def set_rationale(self, rationale: str) -> None:
        """
        Set the rationale for the decision.
        
        Args:
            rationale: Decision rationale
        """
        self.rationale = rationale
        
    def add_criterion_met(self, criterion_name: str, details: str) -> None:
        """
        Add a criterion that was met.
        
        Args:
            criterion_name: Name of the criterion
            details: Details about how the criterion was met
        """
        self.criteria_met.append({
            "name": criterion_name,
            "details": details
        })
        
    def add_criterion_not_met(self, criterion_name: str, details: str) -> None:
        """
        Add a criterion that was not met.
        
        Args:
            criterion_name: Name of the criterion
            details: Details about how the criterion was not met
        """
        self.criteria_not_met.append({
            "name": criterion_name,
            "details": details
        })
        
    def set_reviewer_info(self, reviewer_id: str, reviewer_notes: str) -> None:
        """
        Set reviewer information.
        
        Args:
            reviewer_id: ID of the reviewer
            reviewer_notes: Notes from the reviewer
        """
        self.reviewer_id = reviewer_id
        self.reviewer_notes = reviewer_notes
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the authorization decision to a dictionary.
        
        Returns:
            Dictionary representation of the authorization decision
        """
        return {
            "id": self.id,
            "authorization_id": self.authorization_id,
            "rule_id": self.rule_id,
            "decision": self.decision,
            "decision_date": self.decision_date.isoformat() if self.decision_date else None,
            "rationale": self.rationale,
            "criteria_met": self.criteria_met,
            "criteria_not_met": self.criteria_not_met,
            "reviewer_id": self.reviewer_id,
            "reviewer_notes": self.reviewer_notes
        }


class AuthorizationRulesEngine:
    """
    Engine for generating and applying authorization rules.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the authorization rules engine.
        
        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config
        self.rules_config = config.get("authorization_rules_config", {})
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load reference data
        self.service_types = self.rules_config.get("service_types", [
            "procedure", "medication", "durable_medical_equipment", "imaging",
            "lab_test", "inpatient_admission", "outpatient_service", "therapy"
        ])
        
        self.procedure_codes = self.rules_config.get("procedure_codes", {
            "surgery": ["27447", "27130", "47562", "43644", "33533"],
            "diagnostic": ["45378", "43235", "64483", "31231", "92557"],
            "therapy": ["97110", "97140", "97530", "92507", "90853"]
        })
        
        self.medication_codes = self.rules_config.get("medication_codes", {
            "specialty": ["J9355", "J9271", "J0129", "J2323", "J0178"],
            "infusion": ["J1745", "J1569", "J1561", "J1459", "J1557"],
            "injection": ["J1050", "J1030", "J0585", "J0775", "J1100"]
        })
        
        self.dme_codes = self.rules_config.get("dme_codes", {
            "mobility": ["E0110", "E0130", "E0250", "K0001", "K0011"],
            "respiratory": ["E0424", "E0431", "E0470", "E0601", "E1390"],
            "other": ["E0935", "E0621", "E0217", "E0607", "E0650"]
        })
        
        self.imaging_codes = self.rules_config.get("imaging_codes", {
            "mri": ["70551", "72148", "73721", "74183", "70553"],
            "ct": ["70450", "71250", "72192", "73700", "74176"],
            "ultrasound": ["76700", "76770", "76856", "76830", "76536"]
        })
        
        self.lab_codes = self.rules_config.get("lab_codes", {
            "genetic": ["81228", "81229", "81415", "81420", "81443"],
            "molecular": ["87631", "87651", "87801", "87880", "87910"],
            "chemistry": ["80053", "80061", "80076", "80197", "80307"]
        })
        
        self.diagnosis_codes = self.rules_config.get("diagnosis_codes", {
            "cardiovascular": ["I25.10", "I50.9", "I48.91", "I10", "I25.110"],
            "respiratory": ["J44.9", "J45.909", "J18.9", "J96.00", "J43.9"],
            "musculoskeletal": ["M17.0", "M54.5", "M51.36", "M25.561", "M79.7"],
            "neurological": ["G40.909", "G43.909", "G47.33", "G20", "G35"],
            "gastrointestinal": ["K21.9", "K57.30", "K50.90", "K51.90", "K59.00"],
            "endocrine": ["E11.9", "E78.5", "E03.9", "E05.90", "E66.9"]
        })
        
        self.review_types = self.rules_config.get("review_types", [
            "clinical", "administrative", "pharmacy", "dme", "radiology"
        ])
        
        # Initialize rule templates
        self.rule_templates = {
            "procedure": self._generate_procedure_rule_template,
            "medication": self._generate_medication_rule_template,
            "durable_medical_equipment": self._generate_dme_rule_template,
            "imaging": self._generate_imaging_rule_template,
            "lab_test": self._generate_lab_test_rule_template,
            "inpatient_admission": self._generate_inpatient_rule_template,
            "outpatient_service": self._generate_outpatient_rule_template,
            "therapy": self._generate_therapy_rule_template
        }
        
    def generate_rules(self, count: int) -> List[AuthorizationRule]:
        """
        Generate synthetic authorization rules.
        
        Args:
            count: Number of rules to generate
            
        Returns:
            List of generated AuthorizationRule objects
        """
        rules = []
        
        # Generate rules
        for _ in range(count):
            # Select a random service type
            service_type = random.choice(self.service_types)
            
            # Use the appropriate template to generate the rule
            if service_type in self.rule_templates:
                rule = self.rule_templates[service_type]()
                rules.append(rule)
        
        return rules
    
    def apply_rules(self, authorization: Dict[str, Any], rules: List[AuthorizationRule]) -> AuthorizationDecision:
        """
        Apply authorization rules to an authorization request.
        
        Args:
            authorization: Authorization request dictionary
            rules: List of authorization rules to apply
            
        Returns:
            AuthorizationDecision object with the result
        """
        # Find applicable rules
        applicable_rules = []
        for rule in rules:
            # Check if the service type matches
            if rule.service_type == authorization.get("service_type"):
                # Check if the service code is in the rule's service codes
                service_code = authorization.get("service_code")
                if service_code in rule.service_codes:
                    applicable_rules.append(rule)
        
        # If no applicable rules, no authorization required
        if not applicable_rules:
            decision = AuthorizationDecision()
            decision.set_basic_info(
                authorization.get("id", ""),
                "",
                "approved",
                datetime.now()
            )
            decision.set_rationale("No authorization required for this service")
            return decision
        
        # Apply the most specific rule (the one with the most criteria)
        applicable_rules.sort(key=lambda r: len(r.criteria), reverse=True)
        rule = applicable_rules[0]
        
        # Create a decision
        decision = AuthorizationDecision()
        decision.set_basic_info(
            authorization.get("id", ""),
            rule.id,
            "pending",  # Initial status
            datetime.now()
        )
        
        # Check if any exceptions apply
        for exception in rule.exceptions:
            if self._evaluate_condition(exception["condition"], authorization):
                decision.decision = "approved"
                decision.set_rationale(f"Exception applies: {exception['description']}")
                decision.add_criterion_met(exception["name"], "Exception condition met")
                return decision
        
        # Check approval criteria
        all_approval_criteria_met = True
        for name, criterion in rule.approval_criteria.items():
            if self._evaluate_condition(criterion["condition"], authorization):
                decision.add_criterion_met(name, "Approval criterion met")
            else:
                decision.add_criterion_not_met(name, "Approval criterion not met")
                all_approval_criteria_met = False
        
        # Check denial criteria
        any_denial_criteria_met = False
        for name, criterion in rule.denial_criteria.items():
            if self._evaluate_condition(criterion["condition"], authorization):
                decision.add_criterion_met(name, "Denial criterion met")
                any_denial_criteria_met = True
            else:
                decision.add_criterion_not_met(name, "Denial criterion not met")
        
        # Make the decision
        if any_denial_criteria_met:
            decision.decision = "denied"
            decision.set_rationale("One or more denial criteria were met")
        elif all_approval_criteria_met:
            decision.decision = "approved"
            decision.set_rationale("All approval criteria were met")
        else:
            decision.decision = "pending_review"
            decision.set_rationale("Manual review required")
        
        # Add reviewer information for decisions requiring review
        if decision.decision == "pending_review":
            reviewer_id = f"REV{random.randint(10000, 99999)}"
            reviewer_notes = "Pending clinical review"
            decision.set_reviewer_info(reviewer_id, reviewer_notes)
        
        return decision
    
    def _evaluate_condition(self, condition: Dict[str, Any], authorization: Dict[str, Any]) -> bool:
        """
        Evaluate a condition against an authorization request.
        
        Args:
            condition: Condition dictionary
            authorization: Authorization request dictionary
            
        Returns:
            True if the condition is met, False otherwise
        """
        # This is a simplified implementation
        # In a real system, this would be a more complex rule engine
        
        operator = condition.get("operator", "equals")
        field = condition.get("field", "")
        value = condition.get("value", "")
        
        # Get the field value from the authorization
        field_value = authorization.get(field)
        
        # Evaluate based on the operator
        if operator == "equals":
            return field_value == value
        elif operator == "not_equals":
            return field_value != value
        elif operator == "contains":
            return value in field_value if field_value else False
        elif operator == "not_contains":
            return value not in field_value if field_value else True
        elif operator == "greater_than":
            return field_value > value if field_value is not None else False
        elif operator == "less_than":
            return field_value < value if field_value is not None else False
        elif operator == "in":
            return field_value in value if isinstance(value, list) else False
        elif operator == "not_in":
            return field_value not in value if isinstance(value, list) else True
        elif operator == "all":
            # All sub-conditions must be true
            return all(self._evaluate_condition(subcond, authorization) for subcond in condition.get("conditions", []))
        elif operator == "any":
            # Any sub-condition must be true
            return any(self._evaluate_condition(subcond, authorization) for subcond in condition.get("conditions", []))
        else:
            return False
    
    def _generate_procedure_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for a procedure authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Select a procedure category
        procedure_category = random.choice(list(self.procedure_codes.keys()))
        
        # Set basic info
        name = f"{procedure_category.capitalize()} Procedure Authorization"
        description = f"Authorization rule for {procedure_category} procedures"
        
        rule.set_basic_info(name, description, "procedure")
        
        # Set service codes
        service_codes = self.procedure_codes.get(procedure_category, [])
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "elective_procedure",
            "Authorization required for elective procedures",
            {
                "operator": "equals",
                "field": "is_elective",
                "value": True
            }
        )
        
        rule.add_criterion(
            "high_cost_procedure",
            "Authorization required for procedures with estimated cost above threshold",
            {
                "operator": "greater_than",
                "field": "estimated_cost",
                "value": 5000
            }
        )
        
        # Add exceptions
        rule.add_exception(
            "emergency_exception",
            "No authorization required for emergency procedures",
            {
                "operator": "equals",
                "field": "is_emergency",
                "value": True
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "medical_necessity",
            "Procedure must be medically necessary",
            {
                "operator": "equals",
                "field": "is_medically_necessary",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "conservative_treatment",
            "Conservative treatment has been attempted",
            {
                "operator": "equals",
                "field": "conservative_treatment_attempted",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "experimental",
            "Procedure is experimental or investigational",
            {
                "operator": "equals",
                "field": "is_experimental",
                "value": True
            }
        )
        
        rule.add_denial_criterion(
            "cosmetic",
            "Procedure is primarily cosmetic",
            {
                "operator": "equals",
                "field": "is_cosmetic",
                "value": True
            }
        )
        
        # Set review type
        rule.set_review_type("clinical")
        
        return rule
    
    def _generate_medication_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for a medication authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Select a medication category
        medication_category = random.choice(list(self.medication_codes.keys()))
        
        # Set basic info
        name = f"{medication_category.capitalize()} Medication Authorization"
        description = f"Authorization rule for {medication_category} medications"
        
        rule.set_basic_info(name, description, "medication")
        
        # Set service codes
        service_codes = self.medication_codes.get(medication_category, [])
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "non_formulary",
            "Authorization required for non-formulary medications",
            {
                "operator": "equals",
                "field": "is_formulary",
                "value": False
            }
        )
        
        rule.add_criterion(
            "high_cost_medication",
            "Authorization required for medications with cost above threshold",
            {
                "operator": "greater_than",
                "field": "medication_cost",
                "value": 1000
            }
        )
        
        # Add exceptions
        rule.add_exception(
            "continuation_of_therapy",
            "No authorization required for continuation of existing therapy",
            {
                "operator": "equals",
                "field": "is_continuation_of_therapy",
                "value": True
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "step_therapy",
            "Step therapy protocol has been followed",
            {
                "operator": "equals",
                "field": "step_therapy_completed",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "diagnosis_appropriate",
            "Diagnosis is appropriate for the requested medication",
            {
                "operator": "equals",
                "field": "diagnosis_appropriate",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "off_label",
            "Off-label use without supporting evidence",
            {
                "operator": "all",
                "conditions": [
                    {
                        "operator": "equals",
                        "field": "is_off_label",
                        "value": True
                    },
                    {
                        "operator": "equals",
                        "field": "has_supporting_evidence",
                        "value": False
                    }
                ]
            }
        )
        
        # Set review type
        rule.set_review_type("pharmacy")
        
        return rule
    
    def _generate_dme_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for a DME authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Select a DME category
        dme_category = random.choice(list(self.dme_codes.keys()))
        
        # Set basic info
        name = f"{dme_category.capitalize()} DME Authorization"
        description = f"Authorization rule for {dme_category} durable medical equipment"
        
        rule.set_basic_info(name, description, "durable_medical_equipment")
        
        # Set service codes
        service_codes = self.dme_codes.get(dme_category, [])
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "rental_vs_purchase",
            "Authorization required for purchase of equipment",
            {
                "operator": "equals",
                "field": "is_purchase",
                "value": True
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "medical_necessity",
            "Equipment must be medically necessary",
            {
                "operator": "equals",
                "field": "is_medically_necessary",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "appropriate_for_home_use",
            "Equipment is appropriate for home use",
            {
                "operator": "equals",
                "field": "is_appropriate_for_home_use",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "duplicate_equipment",
            "Equipment duplicates existing equipment",
            {
                "operator": "equals",
                "field": "is_duplicate",
                "value": True
            }
        )
        
        # Set review type
        rule.set_review_type("dme")
        
        return rule
    
    def _generate_imaging_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for an imaging authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Select an imaging category
        imaging_category = random.choice(list(self.imaging_codes.keys()))
        
        # Set basic info
        name = f"{imaging_category.upper()} Authorization"
        description = f"Authorization rule for {imaging_category} imaging studies"
        
        rule.set_basic_info(name, description, "imaging")
        
        # Set service codes
        service_codes = self.imaging_codes.get(imaging_category, [])
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "high_radiation",
            "Authorization required for high-radiation imaging studies",
            {
                "operator": "in",
                "field": "service_code",
                "value": self.imaging_codes.get("ct", []) + self.imaging_codes.get("mri", [])
            }
        )
        
        # Add exceptions
        rule.add_exception(
            "emergency_exception",
            "No authorization required for emergency imaging",
            {
                "operator": "equals",
                "field": "is_emergency",
                "value": True
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "appropriate_indication",
            "Imaging is appropriate for the clinical indication",
            {
                "operator": "equals",
                "field": "has_appropriate_indication",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "follows_guidelines",
            "Imaging request follows clinical guidelines",
            {
                "operator": "equals",
                "field": "follows_guidelines",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "repeat_study",
            "Repeat study without change in clinical status",
            {
                "operator": "all",
                "conditions": [
                    {
                        "operator": "equals",
                        "field": "is_repeat_study",
                        "value": True
                    },
                    {
                        "operator": "equals",
                        "field": "has_clinical_change",
                        "value": False
                    }
                ]
            }
        )
        
        # Set review type
        rule.set_review_type("radiology")
        
        return rule
    
    def _generate_lab_test_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for a lab test authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Select a lab category
        lab_category = random.choice(list(self.lab_codes.keys()))
        
        # Set basic info
        name = f"{lab_category.capitalize()} Lab Test Authorization"
        description = f"Authorization rule for {lab_category} laboratory tests"
        
        rule.set_basic_info(name, description, "lab_test")
        
        # Set service codes
        service_codes = self.lab_codes.get(lab_category, [])
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "genetic_testing",
            "Authorization required for genetic testing",
            {
                "operator": "in",
                "field": "service_code",
                "value": self.lab_codes.get("genetic", [])
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "medical_necessity",
            "Test must be medically necessary",
            {
                "operator": "equals",
                "field": "is_medically_necessary",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "appropriate_frequency",
            "Test frequency is appropriate",
            {
                "operator": "equals",
                "field": "is_appropriate_frequency",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "experimental",
            "Test is experimental or investigational",
            {
                "operator": "equals",
                "field": "is_experimental",
                "value": True
            }
        )
        
        # Set review type
        rule.set_review_type("clinical")
        
        return rule
    
    def _generate_inpatient_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for an inpatient admission authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Set basic info
        name = "Inpatient Admission Authorization"
        description = "Authorization rule for inpatient hospital admissions"
        
        rule.set_basic_info(name, description, "inpatient_admission")
        
        # Set service codes (using diagnosis codes as proxy)
        service_codes = []
        for category in self.diagnosis_codes.values():
            service_codes.extend(category[:2])  # Add a few codes from each category
        
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "elective_admission",
            "Authorization required for elective admissions",
            {
                "operator": "equals",
                "field": "is_elective",
                "value": True
            }
        )
        
        # Add exceptions
        rule.add_exception(
            "emergency_exception",
            "No authorization required for emergency admissions",
            {
                "operator": "equals",
                "field": "is_emergency",
                "value": True
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "inpatient_criteria",
            "Meets inpatient level of care criteria",
            {
                "operator": "equals",
                "field": "meets_inpatient_criteria",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "failed_outpatient",
            "Outpatient management has failed or is not appropriate",
            {
                "operator": "equals",
                "field": "outpatient_management_not_appropriate",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "observation_appropriate",
            "Observation status is more appropriate than inpatient",
            {
                "operator": "equals",
                "field": "observation_appropriate",
                "value": True
            }
        )
        
        # Set review type
        rule.set_review_type("clinical")
        
        return rule
    
    def _generate_outpatient_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for an outpatient service authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Set basic info
        name = "Outpatient Service Authorization"
        description = "Authorization rule for outpatient services"
        
        rule.set_basic_info(name, description, "outpatient_service")
        
        # Set service codes (using a mix of procedure codes)
        service_codes = []
        for category in self.procedure_codes.values():
            service_codes.extend(category[:2])  # Add a few codes from each category
        
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "high_cost_service",
            "Authorization required for high-cost outpatient services",
            {
                "operator": "greater_than",
                "field": "estimated_cost",
                "value": 2000
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "medical_necessity",
            "Service must be medically necessary",
            {
                "operator": "equals",
                "field": "is_medically_necessary",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "appropriate_setting",
            "Outpatient setting is appropriate for the service",
            {
                "operator": "equals",
                "field": "is_appropriate_setting",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "experimental",
            "Service is experimental or investigational",
            {
                "operator": "equals",
                "field": "is_experimental",
                "value": True
            }
        )
        
        # Set review type
        rule.set_review_type("clinical")
        
        return rule
    
    def _generate_therapy_rule_template(self) -> AuthorizationRule:
        """
        Generate a template for a therapy authorization rule.
        
        Returns:
            AuthorizationRule object
        """
        rule = AuthorizationRule()
        
        # Set basic info
        name = "Therapy Services Authorization"
        description = "Authorization rule for physical, occupational, and speech therapy"
        
        rule.set_basic_info(name, description, "therapy")
        
        # Set service codes (using therapy procedure codes)
        service_codes = self.procedure_codes.get("therapy", [])
        rule.set_service_codes(service_codes)
        
        # Set effective period
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        rule.set_effective_period(effective_date)
        
        # Add criteria
        rule.add_criterion(
            "visit_threshold",
            "Authorization required after initial visit threshold",
            {
                "operator": "greater_than",
                "field": "visit_count",
                "value": 6
            }
        )
        
        # Add approval criteria
        rule.add_approval_criterion(
            "medical_necessity",
            "Therapy must be medically necessary",
            {
                "operator": "equals",
                "field": "is_medically_necessary",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "functional_improvement",
            "Therapy is resulting in functional improvement",
            {
                "operator": "equals",
                "field": "shows_functional_improvement",
                "value": True
            }
        )
        
        rule.add_approval_criterion(
            "treatment_plan",
            "Documented treatment plan with goals",
            {
                "operator": "equals",
                "field": "has_treatment_plan",
                "value": True
            }
        )
        
        # Add denial criteria
        rule.add_denial_criterion(
            "maintenance_therapy",
            "Therapy is maintenance only",
            {
                "operator": "equals",
                "field": "is_maintenance_only",
                "value": True
            }
        )
        
        rule.add_denial_criterion(
            "no_progress",
            "No progress toward goals after reasonable trial",
            {
                "operator": "equals",
                "field": "shows_progress",
                "value": False
            }
        )
        
        # Set review type
        rule.set_review_type("clinical")
        
        return rule
    
    def generate(self, rule_count: int, authorization_count: int = 0, 
                members: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate synthetic authorization rules and decisions.
        
        Args:
            rule_count: Number of rules to generate
            authorization_count: Number of authorization decisions to generate
            members: List of member dictionaries to associate authorizations with
            
        Returns:
            Dictionary containing the generated rules and decisions
        """
        # Generate rules
        rules = self.generate_rules(rule_count)
        
        # Generate authorization decisions if requested
        decisions = []
        if authorization_count > 0 and members:
            # Generate synthetic authorization requests
            authorizations = self._generate_authorization_requests(authorization_count, members, rules)
            
            # Apply rules to generate decisions
            for authorization in authorizations:
                decision = self.apply_rules(authorization, rules)
                decisions.append(decision)
        
        # Convert to dictionaries
        rule_dicts = [rule.to_dict() for rule in rules]
        decision_dicts = [decision.to_dict() for decision in decisions]
        
        return {
            "rules": rule_dicts,
            "decisions": decision_dicts
        }
    
    def _generate_authorization_requests(self, count: int, members: List[Dict[str, Any]], 
                                        rules: List[AuthorizationRule]) -> List[Dict[str, Any]]:
        """
        Generate synthetic authorization requests.
        
        Args:
            count: Number of requests to generate
            members: List of member dictionaries to associate requests with
            rules: List of rules to reference
            
        Returns:
            List of authorization request dictionaries
        """
        requests = []
        
        for _ in range(count):
            # Select a random member
            member = random.choice(members)
            member_id = member.get("id")
            
            # Select a random rule
            rule = random.choice(rules)
            
            # Select a random service code from the rule
            service_code = random.choice(rule.service_codes) if rule.service_codes else ""
            
            # Generate request
            request = {
                "id": f"AUTH{uuid.uuid4().hex[:8].upper()}",
                "member_id": member_id,
                "service_type": rule.service_type,
                "service_code": service_code,
                "request_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "is_emergency": random.random() < 0.1,
                "is_elective": random.random() < 0.7,
                "estimated_cost": random.uniform(100, 10000),
                "is_medically_necessary": random.random() < 0.8,
                "conservative_treatment_attempted": random.random() < 0.7,
                "is_experimental": random.random() < 0.05,
                "is_cosmetic": random.random() < 0.05,
                "is_formulary": random.random() < 0.8,
                "medication_cost": random.uniform(10, 5000),
                "is_continuation_of_therapy": random.random() < 0.3,
                "step_therapy_completed": random.random() < 0.6,
                "diagnosis_appropriate": random.random() < 0.9,
                "is_off_label": random.random() < 0.1,
                "has_supporting_evidence": random.random() < 0.7,
                "is_purchase": random.random() < 0.6,
                "is_appropriate_for_home_use": random.random() < 0.9,
                "is_duplicate": random.random() < 0.05,
                "has_appropriate_indication": random.random() < 0.85,
                "follows_guidelines": random.random() < 0.8,
                "is_repeat_study": random.random() < 0.2,
                "has_clinical_change": random.random() < 0.6,
                "is_appropriate_frequency": random.random() < 0.9,
                "meets_inpatient_criteria": random.random() < 0.75,
                "outpatient_management_not_appropriate": random.random() < 0.7,
                "observation_appropriate": random.random() < 0.3,
                "is_appropriate_setting": random.random() < 0.9,
                "visit_count": random.randint(1, 20),
                "shows_functional_improvement": random.random() < 0.8,
                "has_treatment_plan": random.random() < 0.9,
                "is_maintenance_only": random.random() < 0.2,
                "shows_progress": random.random() < 0.8
            }
            
            requests.append(request)
        
        return requests