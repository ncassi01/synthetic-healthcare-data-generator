"""
Data Consistency Validator for the synthetic healthcare data generator.

This module provides functionality to validate the consistency of generated data
across different domains, ensuring that the data is realistic and coherent.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class DataConsistencyValidator:
    """
    Validator for ensuring consistency across generated healthcare data.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data consistency validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.validation_config = config.get("consistency_validation_config", {})
        self.validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
    def validate_member_data(self, members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate member data for consistency.
        
        Args:
            members: List of member dictionaries to validate
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Validating {len(members)} members for consistency")
        
        # Reset validation results
        self.validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Validate each member
        for member in members:
            self._validate_member_demographics(member)
            self._validate_member_insurance(member)
            self._validate_member_risk_scores(member)
        
        # Log validation summary
        error_count = len(self.validation_results["errors"])
        warning_count = len(self.validation_results["warnings"])
        info_count = len(self.validation_results["info"])
        
        logger.info(f"Member validation complete: {error_count} errors, {warning_count} warnings, {info_count} info messages")
        
        return self.validation_results
    
    def validate_claims_data(self, claims: List[Dict[str, Any]], members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate claims data for consistency.
        
        Args:
            claims: List of claim dictionaries to validate
            members: List of member dictionaries to reference
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Validating {len(claims)} claims for consistency")
        
        # Reset validation results
        self.validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Create a lookup of member IDs for quick reference
        member_ids = {member.get("id"): member for member in members}
        
        # Validate each claim
        for claim in claims:
            self._validate_claim_basics(claim)
            self._validate_claim_member_reference(claim, member_ids)
            self._validate_claim_dates(claim, member_ids)
            self._validate_claim_amounts(claim)
        
        # Log validation summary
        error_count = len(self.validation_results["errors"])
        warning_count = len(self.validation_results["warnings"])
        info_count = len(self.validation_results["info"])
        
        logger.info(f"Claims validation complete: {error_count} errors, {warning_count} warnings, {info_count} info messages")
        
        return self.validation_results
    
    def validate_enhanced_data_models(self, data: Dict[str, Any], members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate enhanced data models for consistency.
        
        Args:
            data: Dictionary containing enhanced data models
            members: List of member dictionaries to reference
            
        Returns:
            Dictionary containing validation results
        """
        logger.info("Validating enhanced data models")
        
        # Reset validation results
        self.validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Create a lookup of member IDs for quick reference
        member_ids = {member.get("id"): member for member in members}
        
        # Validate care episodes
        care_episodes = data.get("care_episodes", [])
        if care_episodes:
            self._validate_care_episodes(care_episodes, member_ids)
        
        # Validate SDOH assessments
        sdoh_assessments = data.get("sdoh_assessments", [])
        if sdoh_assessments:
            self._validate_sdoh_assessments(sdoh_assessments, member_ids)
        
        # Validate risk assessments
        risk_assessments = data.get("risk_assessments", [])
        if risk_assessments:
            self._validate_risk_assessments(risk_assessments, member_ids)
        
        # Validate provider network
        provider_network = data.get("provider_network", {})
        if provider_network:
            self._validate_provider_network(provider_network)
        
        # Validate pharmacy benefit
        pharmacy_benefit = data.get("pharmacy_benefit", {})
        if pharmacy_benefit:
            self._validate_pharmacy_benefit(pharmacy_benefit, member_ids)
        
        # Validate authorization rules
        auth_rules = data.get("authorization_rules", {})
        if auth_rules:
            self._validate_authorization_rules(auth_rules)
        
        # Log validation summary
        error_count = len(self.validation_results["errors"])
        warning_count = len(self.validation_results["warnings"])
        info_count = len(self.validation_results["info"])
        
        logger.info(f"Enhanced data models validation complete: {error_count} errors, {warning_count} warnings, {info_count} info messages")
        
        return self.validation_results
    
    def _validate_member_demographics(self, member: Dict[str, Any]) -> None:
        """
        Validate member demographics for consistency.
        
        Args:
            member: Member dictionary to validate
        """
        member_id = member.get("id", "unknown")
        
        # Check for required fields
        required_fields = ["first_name", "last_name", "date_of_birth", "gender"]
        for field in required_fields:
            if field not in member:
                self.validation_results["errors"].append({
                    "type": "missing_required_field",
                    "entity_type": "member",
                    "entity_id": member_id,
                    "field": field,
                    "message": f"Member {member_id} is missing required field: {field}"
                })
        
        # Validate date of birth
        dob = member.get("date_of_birth")
        if dob:
            try:
                dob_date = datetime.fromisoformat(dob.replace("Z", "+00:00"))
                
                # Check if date of birth is in the future
                if dob_date > datetime.now():
                    self.validation_results["errors"].append({
                        "type": "invalid_date_of_birth",
                        "entity_type": "member",
                        "entity_id": member_id,
                        "field": "date_of_birth",
                        "message": f"Member {member_id} has a date of birth in the future: {dob}"
                    })
                
                # Check if date of birth is too far in the past (e.g., > 120 years)
                if dob_date < datetime.now() - timedelta(days=365 * 120):
                    self.validation_results["warnings"].append({
                        "type": "unlikely_date_of_birth",
                        "entity_type": "member",
                        "entity_id": member_id,
                        "field": "date_of_birth",
                        "message": f"Member {member_id} has an unlikely date of birth (> 120 years ago): {dob}"
                    })
            except ValueError:
                self.validation_results["errors"].append({
                    "type": "invalid_date_format",
                    "entity_type": "member",
                    "entity_id": member_id,
                    "field": "date_of_birth",
                    "message": f"Member {member_id} has an invalid date format for date of birth: {dob}"
                })
    
    def _validate_member_insurance(self, member: Dict[str, Any]) -> None:
        """
        Validate member insurance information for consistency.
        
        Args:
            member: Member dictionary to validate
        """
        member_id = member.get("id", "unknown")
        
        # Check for insurance information
        insurance = member.get("insurance")
        if not insurance:
            self.validation_results["warnings"].append({
                "type": "missing_insurance",
                "entity_type": "member",
                "entity_id": member_id,
                "field": "insurance",
                "message": f"Member {member_id} has no insurance information"
            })
            return
    
    def _validate_member_risk_scores(self, member: Dict[str, Any]) -> None:
        """
        Validate member risk scores for consistency.
        
        Args:
            member: Member dictionary to validate
        """
        member_id = member.get("id", "unknown")
        
        # Check for risk scores
        risk_score = member.get("risk_score")
        if risk_score is not None:
            # Validate risk score range
            if not isinstance(risk_score, (int, float)) or risk_score < 0 or risk_score > 100:
                self.validation_results["warnings"].append({
                    "type": "invalid_risk_score",
                    "entity_type": "member",
                    "entity_id": member_id,
                    "field": "risk_score",
                    "message": f"Member {member_id} has an invalid risk score: {risk_score} (should be between 0 and 100)"
                })
    
    def _validate_claim_basics(self, claim: Dict[str, Any]) -> None:
        """
        Validate basic claim information for consistency.
        
        Args:
            claim: Claim dictionary to validate
        """
        claim_id = claim.get("id", "unknown")
        
        # Check for required fields
        required_fields = ["member_id", "provider_id", "date_of_service", "total_charge"]
        for field in required_fields:
            if field not in claim:
                self.validation_results["errors"].append({
                    "type": "missing_required_field",
                    "entity_type": "claim",
                    "entity_id": claim_id,
                    "field": field,
                    "message": f"Claim {claim_id} is missing required field: {field}"
                })
    
    def _validate_claim_member_reference(self, claim: Dict[str, Any], member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate that the claim references a valid member.
        
        Args:
            claim: Claim dictionary to validate
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        claim_id = claim.get("id", "unknown")
        member_id = claim.get("member_id")
        
        if member_id and member_id not in member_ids:
            self.validation_results["errors"].append({
                "type": "invalid_member_reference",
                "entity_type": "claim",
                "entity_id": claim_id,
                "field": "member_id",
                "message": f"Claim {claim_id} references non-existent member: {member_id}"
            })
    
    def _validate_claim_dates(self, claim: Dict[str, Any], member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate claim dates for consistency.
        
        Args:
            claim: Claim dictionary to validate
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        claim_id = claim.get("id", "unknown")
        member_id = claim.get("member_id")
        
        # Validate date of service
        service_date = claim.get("date_of_service")
        if service_date:
            try:
                service_date_obj = datetime.fromisoformat(service_date.replace("Z", "+00:00"))
                
                # Check if date of service is in the future
                if service_date_obj > datetime.now():
                    self.validation_results["errors"].append({
                        "type": "future_service_date",
                        "entity_type": "claim",
                        "entity_id": claim_id,
                        "field": "date_of_service",
                        "message": f"Claim {claim_id} has a date of service in the future: {service_date}"
                    })
            except ValueError:
                self.validation_results["errors"].append({
                    "type": "invalid_date_format",
                    "entity_type": "claim",
                    "entity_id": claim_id,
                    "field": "date_of_service",
                    "message": f"Claim {claim_id} has an invalid date format for date of service: {service_date}"
                })
    
    def _validate_claim_amounts(self, claim: Dict[str, Any]) -> None:
        """
        Validate claim amounts for consistency.
        
        Args:
            claim: Claim dictionary to validate
        """
        claim_id = claim.get("id", "unknown")
        
        # Validate payment amounts
        total_charge = claim.get("total_charge", 0)
        member_paid = claim.get("member_paid", 0)
        insurance_paid = claim.get("insurance_paid", 0)
        
        # Check for negative amounts
        if member_paid < 0:
            self.validation_results["errors"].append({
                "type": "negative_amount",
                "entity_type": "claim",
                "entity_id": claim_id,
                "field": "member_paid",
                "message": f"Claim {claim_id} has a negative member paid amount: {member_paid}"
            })
    
    def _validate_care_episodes(self, care_episodes: List[Dict[str, Any]], 
                              member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate care episodes for consistency.
        
        Args:
            care_episodes: List of care episode dictionaries
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        for episode in care_episodes:
            episode_id = episode.get("id", "unknown")
            member_id = episode.get("member_id")
            
            # Check if member exists
            if member_id and member_id not in member_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_member_reference",
                    "entity_type": "care_episode",
                    "entity_id": episode_id,
                    "field": "member_id",
                    "message": f"Care episode {episode_id} references non-existent member: {member_id}"
                })
    
    def _validate_sdoh_assessments(self, sdoh_assessments: List[Dict[str, Any]], 
                                 member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate SDOH assessments for consistency.
        
        Args:
            sdoh_assessments: List of SDOH assessment dictionaries
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        for assessment in sdoh_assessments:
            assessment_id = assessment.get("id", "unknown")
            member_id = assessment.get("member_id")
            
            # Check if member exists
            if member_id and member_id not in member_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_member_reference",
                    "entity_type": "sdoh_assessment",
                    "entity_id": assessment_id,
                    "field": "member_id",
                    "message": f"SDOH assessment {assessment_id} references non-existent member: {member_id}"
                })
    
    def _validate_risk_assessments(self, risk_assessments: List[Dict[str, Any]], 
                                 member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate risk assessments for consistency.
        
        Args:
            risk_assessments: List of risk assessment dictionaries
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        for assessment in risk_assessments:
            assessment_id = assessment.get("id", "unknown")
            member_id = assessment.get("member_id")
            
            # Check if member exists
            if member_id and member_id not in member_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_member_reference",
                    "entity_type": "risk_assessment",
                    "entity_id": assessment_id,
                    "field": "member_id",
                    "message": f"Risk assessment {assessment_id} references non-existent member: {member_id}"
                })
    
    def _validate_provider_network(self, provider_network: Dict[str, Any]) -> None:
        """
        Validate provider network for consistency.
        
        Args:
            provider_network: Provider network dictionary
        """
        # Validate providers
        providers = provider_network.get("providers", [])
        for provider in providers:
            provider_id = provider.get("id", "unknown")
            
            # Check for required fields
            required_fields = ["first_name", "last_name", "specialty"]
            for field in required_fields:
                if field not in provider:
                    self.validation_results["warnings"].append({
                        "type": "missing_required_field",
                        "entity_type": "provider",
                        "entity_id": provider_id,
                        "field": field,
                        "message": f"Provider {provider_id} is missing required field: {field}"
                    })
    
    def _validate_pharmacy_benefit(self, pharmacy_benefit: Dict[str, Any], 
                                 member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate pharmacy benefit for consistency.
        
        Args:
            pharmacy_benefit: Pharmacy benefit dictionary
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        # Validate pharmacy claims
        pharmacy_claims = pharmacy_benefit.get("pharmacy_claims", [])
        for claim in pharmacy_claims:
            claim_id = claim.get("id", "unknown")
            member_id = claim.get("member_id")
            
            # Check if member exists
            if member_id and member_id not in member_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_member_reference",
                    "entity_type": "pharmacy_claim",
                    "entity_id": claim_id,
                    "field": "member_id",
                    "message": f"Pharmacy claim {claim_id} references non-existent member: {member_id}"
                })
    
    def _validate_authorization_rules(self, auth_rules: Dict[str, Any]) -> None:
        """
        Validate authorization rules for consistency.
        
        Args:
            auth_rules: Authorization rules dictionary
        """
        # Validate rules
        rules = auth_rules.get("rules", [])
        for rule in rules:
            rule_id = rule.get("id", "unknown")
            
            # Check for required fields
            required_fields = ["name", "service_type", "service_codes"]
            for field in required_fields:
                if field not in rule:
                    self.validation_results["warnings"].append({
                        "type": "missing_required_field",
                        "entity_type": "authorization_rule",
                        "entity_id": rule_id,
                        "field": field,
                        "message": f"Authorization rule {rule_id} is missing required field: {field}"
                    })
    
    def validate_cross_domain_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate consistency across different domains in the data.
        
        This method checks for consistency between different data domains, ensuring
        that references between domains are valid and that the data is coherent
        across the entire dataset.
        
        Args:
            data: Dictionary containing data from all domains
            
        Returns:
            Dictionary containing validation results
        """
        logger.info("Validating cross-domain consistency")
        
        # Reset validation results
        self.validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Get data from different domains
        members = data.get("members", [])
        care_episodes = data.get("care_episodes", [])
        sdoh_assessments = data.get("sdoh_assessments", [])
        risk_assessments = data.get("risk_assessments", [])
        provider_network = data.get("provider_network", {})
        pharmacy_benefit = data.get("pharmacy_benefit", {})
        auth_rules = data.get("authorization_rules", {})
        
        # Create lookup dictionaries for quick reference
        member_ids = {member.get("id"): member for member in members}
        provider_ids = {provider.get("id"): provider for provider in provider_network.get("providers", [])}
        facility_ids = {facility.get("id"): facility for facility in provider_network.get("facilities", [])}
        
        # Validate care episodes against provider network
        if care_episodes and provider_network:
            self._validate_care_episodes_provider_references(care_episodes, provider_ids, facility_ids)
        
        # Validate pharmacy claims against provider network
        if pharmacy_benefit and provider_network:
            self._validate_pharmacy_provider_references(pharmacy_benefit, provider_ids)
        
        # Validate authorization rules against care episodes
        if auth_rules and care_episodes:
            self._validate_auth_rules_care_episodes(auth_rules, care_episodes)
        
        # Validate risk assessments against SDOH assessments
        if risk_assessments and sdoh_assessments:
            self._validate_risk_sdoh_correlation(risk_assessments, sdoh_assessments, member_ids)
        
        # Log validation summary
        error_count = len(self.validation_results["errors"])
        warning_count = len(self.validation_results["warnings"])
        info_count = len(self.validation_results["info"])
        
        logger.info(f"Cross-domain validation complete: {error_count} errors, {warning_count} warnings, {info_count} info messages")
        
        return self.validation_results
    
    def _validate_care_episodes_provider_references(self, care_episodes: List[Dict[str, Any]],
                                                  provider_ids: Dict[str, Dict[str, Any]],
                                                  facility_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate that care episodes reference valid providers and facilities.
        
        Args:
            care_episodes: List of care episode dictionaries
            provider_ids: Dictionary mapping provider IDs to provider dictionaries
            facility_ids: Dictionary mapping facility IDs to facility dictionaries
        """
        for episode in care_episodes:
            episode_id = episode.get("id", "unknown")
            provider_id = episode.get("provider_id")
            facility_id = episode.get("facility_id")
            
            # Check if provider exists
            if provider_id and provider_id not in provider_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_provider_reference",
                    "entity_type": "care_episode",
                    "entity_id": episode_id,
                    "field": "provider_id",
                    "message": f"Care episode {episode_id} references non-existent provider: {provider_id}"
                })
            
            # Check if facility exists
            if facility_id and facility_id not in facility_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_facility_reference",
                    "entity_type": "care_episode",
                    "entity_id": episode_id,
                    "field": "facility_id",
                    "message": f"Care episode {episode_id} references non-existent facility: {facility_id}"
                })
    
    def _validate_pharmacy_provider_references(self, pharmacy_benefit: Dict[str, Any],
                                             provider_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate that pharmacy claims reference valid providers.
        
        Args:
            pharmacy_benefit: Pharmacy benefit dictionary
            provider_ids: Dictionary mapping provider IDs to provider dictionaries
        """
        pharmacy_claims = pharmacy_benefit.get("pharmacy_claims", [])
        for claim in pharmacy_claims:
            claim_id = claim.get("id", "unknown")
            prescriber_id = claim.get("prescriber_id")
            
            # Check if prescriber exists
            if prescriber_id and prescriber_id not in provider_ids:
                self.validation_results["errors"].append({
                    "type": "invalid_prescriber_reference",
                    "entity_type": "pharmacy_claim",
                    "entity_id": claim_id,
                    "field": "prescriber_id",
                    "message": f"Pharmacy claim {claim_id} references non-existent prescriber: {prescriber_id}"
                })
    
    def _validate_auth_rules_care_episodes(self, auth_rules: Dict[str, Any],
                                         care_episodes: List[Dict[str, Any]]) -> None:
        """
        Validate that authorization rules are consistent with care episodes.
        
        Args:
            auth_rules: Authorization rules dictionary
            care_episodes: List of care episode dictionaries
        """
        # Extract service types from care episodes
        care_episode_service_types = set()
        for episode in care_episodes:
            service_type = episode.get("service_type")
            if service_type:
                care_episode_service_types.add(service_type)
        
        # Check if authorization rules cover all service types in care episodes
        rules = auth_rules.get("rules", [])
        rule_service_types = set()
        for rule in rules:
            service_type = rule.get("service_type")
            if service_type:
                rule_service_types.add(service_type)
        
        # Find service types in care episodes that are not covered by authorization rules
        uncovered_service_types = care_episode_service_types - rule_service_types
        if uncovered_service_types:
            self.validation_results["warnings"].append({
                "type": "uncovered_service_types",
                "entity_type": "authorization_rules",
                "entity_id": "global",
                "field": "service_type",
                "message": f"The following service types in care episodes are not covered by authorization rules: {', '.join(uncovered_service_types)}"
            })
    
    def _validate_risk_sdoh_correlation(self, risk_assessments: List[Dict[str, Any]],
                                      sdoh_assessments: List[Dict[str, Any]],
                                      member_ids: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate correlation between risk assessments and SDOH assessments.
        
        Args:
            risk_assessments: List of risk assessment dictionaries
            sdoh_assessments: List of SDOH assessment dictionaries
            member_ids: Dictionary mapping member IDs to member dictionaries
        """
        # Group assessments by member ID
        risk_by_member = {}
        for assessment in risk_assessments:
            member_id = assessment.get("member_id")
            if member_id:
                if member_id not in risk_by_member:
                    risk_by_member[member_id] = []
                risk_by_member[member_id].append(assessment)
        
        sdoh_by_member = {}
        for assessment in sdoh_assessments:
            member_id = assessment.get("member_id")
            if member_id:
                if member_id not in sdoh_by_member:
                    sdoh_by_member[member_id] = []
                sdoh_by_member[member_id].append(assessment)
        
        # Check for members with high risk scores but no SDOH assessments
        for member_id, risk_assessments in risk_by_member.items():
            # Find the highest risk score for the member
            highest_risk = 0
            for assessment in risk_assessments:
                risk_score = assessment.get("risk_score", 0)
                if risk_score > highest_risk:
                    highest_risk = risk_score
            
            # Check if high-risk members have SDOH assessments
            if highest_risk >= 75 and member_id not in sdoh_by_member:
                self.validation_results["warnings"].append({
                    "type": "missing_sdoh_for_high_risk",
                    "entity_type": "member",
                    "entity_id": member_id,
                    "field": "sdoh_assessments",
                    "message": f"Member {member_id} has a high risk score ({highest_risk}) but no SDOH assessments"
                })
