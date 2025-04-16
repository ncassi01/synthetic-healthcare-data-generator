"""
Validation utility functions for the synthetic healthcare data generator.

This module provides utility functions for validating generated data.
"""

import logging
import re
import os
import sys
from datetime import date
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.member import Member


logger = logging.getLogger(__name__)


def validate_member(member: Member) -> List[str]:
    """
    Validate a member object for data consistency and quality.
    
    Args:
        member: Member object to validate.
        
    Returns:
        List of validation errors, empty if no errors.
    """
    errors = []
    
    # Validate member ID
    if not member.id or not re.match(r'^MEM\d{8}$', member.id):
        errors.append(f"Invalid member ID format: {member.id}")
    
    # Validate name
    if not member.first_name:
        errors.append("Missing first name")
    if not member.last_name:
        errors.append("Missing last name")
    
    # Validate demographics
    if not member.demographics.date_of_birth:
        errors.append("Missing date of birth")
    elif member.demographics.date_of_birth > date.today():
        errors.append(f"Invalid date of birth (future date): {member.demographics.date_of_birth}")
    
    if not member.demographics.gender:
        errors.append("Missing gender")
    
    # Validate address
    if not member.address.street:
        errors.append("Missing street address")
    if not member.address.city:
        errors.append("Missing city")
    if not member.address.state:
        errors.append("Missing state")
    if not member.address.zip_code:
        errors.append("Missing ZIP code")
    elif not re.match(r'^\d{5}(-\d{4})?$', member.address.zip_code):
        errors.append(f"Invalid ZIP code format: {member.address.zip_code}")
    
    # Validate insurance
    if not member.insurance.plan_type:
        errors.append("Missing insurance plan type")
    if not member.insurance.metal_level:
        errors.append("Missing insurance metal level")
    if not member.insurance.member_id:
        errors.append("Missing insurance member ID")
    if not member.insurance.coverage_start_date:
        errors.append("Missing insurance coverage start date")
    elif member.insurance.coverage_end_date and member.insurance.coverage_end_date < member.insurance.coverage_start_date:
        errors.append("Insurance coverage end date is before start date")
    
    # Validate risk scores
    if hasattr(member, 'risk_scores') and member.risk_scores:
        for score_type, score_value in member.risk_scores.items():
            if not isinstance(score_value, (int, float)):
                errors.append(f"Invalid risk score value for {score_type}: {score_value}")
            elif score_value < 0 or score_value > 1:
                errors.append(f"Risk score {score_type} out of range (0-1): {score_value}")
    
    # Validate care gaps
    if hasattr(member, 'care_gaps') and member.care_gaps:
        for i, gap in enumerate(member.care_gaps):
            if not isinstance(gap, dict):
                errors.append(f"Care gap at index {i} is not a dictionary")
                continue
            
            if 'description' not in gap:
                errors.append(f"Care gap at index {i} missing description")
            
            if 'priority' not in gap:
                errors.append(f"Care gap at index {i} missing priority")
            elif gap['priority'] not in ['low', 'medium', 'high']:
                errors.append(f"Invalid priority for care gap at index {i}: {gap['priority']}")
            
            if 'type' not in gap:
                errors.append(f"Care gap at index {i} missing type")
    
    return errors


def validate_dataset(members: List[Member]) -> Dict[str, List[str]]:
    """
    Validate a dataset of members for data consistency and quality.
    
    Args:
        members: List of Member objects to validate.
        
    Returns:
        Dictionary mapping member IDs to lists of validation errors.
    """
    validation_results = {}
    
    for member in members:
        errors = validate_member(member)
        if errors:
            validation_results[member.id] = errors
    
    if validation_results:
        logger.warning(f"Found validation errors in {len(validation_results)} members")
    else:
        logger.info("No validation errors found")
    
    return validation_results


def check_data_distribution(members: List[Member]) -> Dict[str, Dict[str, int]]:
    """
    Check the distribution of key attributes in the dataset.
    
    Args:
        members: List of Member objects to analyze.
        
    Returns:
        Dictionary with distribution statistics.
    """
    distributions = {
        'gender': {},
        'state': {},
        'plan_type': {},
        'metal_level': {},
        'age_groups': {
            '0-17': 0,
            '18-34': 0,
            '35-50': 0,
            '51-64': 0,
            '65+': 0
        },
        'conditions': {},
        'medications': {},
        'procedures': {},
        'care_gap_types': {},
        'care_gap_priorities': {},
        'risk_score_ranges': {
            'clinical_risk': {
                '0.0-0.2': 0,
                '0.2-0.4': 0,
                '0.4-0.6': 0,
                '0.6-0.8': 0,
                '0.8-1.0': 0
            },
            'readmission_risk': {
                '0.0-0.2': 0,
                '0.2-0.4': 0,
                '0.4-0.6': 0,
                '0.6-0.8': 0,
                '0.8-1.0': 0
            },
            'medication_adherence': {
                '0.0-0.2': 0,
                '0.2-0.4': 0,
                '0.4-0.6': 0,
                '0.6-0.8': 0,
                '0.8-1.0': 0
            }
        }
    }
    
    for member in members:
        # Gender distribution
        gender = member.demographics.gender
        distributions['gender'][gender] = distributions['gender'].get(gender, 0) + 1
        
        # State distribution
        state = member.address.state
        distributions['state'][state] = distributions['state'].get(state, 0) + 1
        
        # Plan type distribution
        plan_type = member.insurance.plan_type
        distributions['plan_type'][plan_type] = distributions['plan_type'].get(plan_type, 0) + 1
        
        # Metal level distribution
        metal_level = member.insurance.metal_level
        distributions['metal_level'][metal_level] = distributions['metal_level'].get(metal_level, 0) + 1
        
        # Age group distribution
        age = member.age
        if age < 18:
            distributions['age_groups']['0-17'] += 1
        elif age < 35:
            distributions['age_groups']['18-34'] += 1
        elif age < 51:
            distributions['age_groups']['35-50'] += 1
        elif age < 65:
            distributions['age_groups']['51-64'] += 1
        else:
            distributions['age_groups']['65+'] += 1
        
        # Conditions distribution
        for condition in member.conditions:
            distributions['conditions'][condition] = distributions['conditions'].get(condition, 0) + 1
        
        # Medications distribution
        for medication in member.medications:
            distributions['medications'][medication] = distributions['medications'].get(medication, 0) + 1
        
        # Procedures distribution
        for procedure in member.procedures:
            distributions['procedures'][procedure] = distributions['procedures'].get(procedure, 0) + 1
        
        # Care gap distributions
        if hasattr(member, 'care_gaps') and member.care_gaps:
            for gap in member.care_gaps:
                if 'type' in gap:
                    gap_type = gap['type']
                    distributions['care_gap_types'][gap_type] = distributions['care_gap_types'].get(gap_type, 0) + 1
                
                if 'priority' in gap:
                    priority = gap['priority']
                    distributions['care_gap_priorities'][priority] = distributions['care_gap_priorities'].get(priority, 0) + 1
        
        # Risk score distributions
        if hasattr(member, 'risk_scores') and member.risk_scores:
            for score_type, score_value in member.risk_scores.items():
                if score_type in distributions['risk_score_ranges']:
                    # Determine which range the score falls into
                    if 0.0 <= score_value < 0.2:
                        distributions['risk_score_ranges'][score_type]['0.0-0.2'] += 1
                    elif 0.2 <= score_value < 0.4:
                        distributions['risk_score_ranges'][score_type]['0.2-0.4'] += 1
                    elif 0.4 <= score_value < 0.6:
                        distributions['risk_score_ranges'][score_type]['0.4-0.6'] += 1
                    elif 0.6 <= score_value < 0.8:
                        distributions['risk_score_ranges'][score_type]['0.6-0.8'] += 1
                    elif 0.8 <= score_value <= 1.0:
                        distributions['risk_score_ranges'][score_type]['0.8-1.0'] += 1
    
    return distributions