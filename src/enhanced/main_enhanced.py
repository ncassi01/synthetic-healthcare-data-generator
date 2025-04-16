"""
Enhanced data model generation functions for the synthetic healthcare data generator.

This module provides functions to generate and save enhanced data models (Phase 7).
"""

import json
import logging
import os
from typing import Dict, List, Any

from src.enhanced.care_episodes import CareEpisodesGenerator
from src.enhanced.sdoh import SDOHAssessmentGenerator
from src.enhanced.risk_assessment import RiskAssessmentGenerator
from src.enhanced.provider_network import ProviderNetworkGenerator
from src.enhanced.pharmacy import PharmacyBenefitGenerator
from src.enhanced.auth_rules import AuthorizationRulesEngine
from src.enhanced.consistency import DataConsistencyValidator

from src.utils.file_utils import get_output_path

logger = logging.getLogger(__name__)


def generate_care_episodes(config: Dict, members: List[Dict], seed: int = None) -> List[Any]:
    """
    Generate synthetic care episodes.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate care episodes with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated care episode objects.
    """
    # Get care episode count from config
    episode_config = config.get('care_episode_config', {})
    episode_count_config = episode_config.get('episodes_per_member', {
        'min': 0,
        'max': 3,
        'mean': 1
    })
    
    # Calculate total episodes to generate
    mean_episodes_per_member = episode_count_config.get('mean', 1)
    total_episodes = int(len(members) * mean_episodes_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_episodes} care episodes with seed {seed}")
    
    # Create care episodes generator
    episode_generator = CareEpisodesGenerator(config, seed)
    
    # Generate care episodes
    episodes = episode_generator.generate(total_episodes, members)
    
    logger.info(f"Generated {len(episodes)} care episodes")
    
    return episodes


def generate_sdoh_assessments(config: Dict, members: List[Dict], seed: int = None) -> List[Any]:
    """
    Generate synthetic SDOH assessments.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate SDOH assessments with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated SDOH assessment objects.
    """
    # Get SDOH assessment count from config
    sdoh_config = config.get('sdoh_config', {})
    sdoh_count_config = sdoh_config.get('assessments_per_member', {
        'min': 0,
        'max': 2,
        'mean': 1
    })
    
    # Calculate total assessments to generate
    mean_assessments_per_member = sdoh_count_config.get('mean', 1)
    total_assessments = int(len(members) * mean_assessments_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_assessments} SDOH assessments with seed {seed}")
    
    # Create SDOH assessment generator
    sdoh_generator = SDOHAssessmentGenerator(config, seed)
    
    # Generate SDOH assessments
    assessments = sdoh_generator.generate(total_assessments, members)
    
    logger.info(f"Generated {len(assessments)} SDOH assessments")
    
    return assessments


def generate_risk_assessments(config: Dict, members: List[Dict], seed: int = None) -> List[Any]:
    """
    Generate synthetic risk assessments.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate risk assessments with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated risk assessment objects.
    """
    # Get risk assessment count from config
    risk_config = config.get('risk_assessment_config', {})
    risk_count_config = risk_config.get('assessments_per_member', {
        'min': 1,
        'max': 3,
        'mean': 1
    })
    
    # Calculate total assessments to generate
    mean_assessments_per_member = risk_count_config.get('mean', 1)
    total_assessments = int(len(members) * mean_assessments_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_assessments} risk assessments with seed {seed}")
    
    # Create risk assessment generator
    risk_generator = RiskAssessmentGenerator(config, seed)
    
    # Generate risk assessments
    assessments = risk_generator.generate(total_assessments, members)
    
    logger.info(f"Generated {len(assessments)} risk assessments")
    
    return assessments


def generate_provider_network(config: Dict, seed: int = None) -> Dict[str, Any]:
    """
    Generate synthetic provider network.
    
    Args:
        config: Configuration dictionary.
        seed: Random seed (overrides config).
        
    Returns:
        Dictionary containing the generated provider network.
    """
    # Get provider and facility counts from config
    network_config = config.get('provider_network_config', {})
    provider_count = network_config.get('provider_count', 100)
    facility_count = network_config.get('facility_count', 20)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating provider network with {provider_count} providers and {facility_count} facilities with seed {seed}")
    
    # Create provider network generator
    network_generator = ProviderNetworkGenerator(config, seed)
    
    # Generate provider network
    network = network_generator.generate(provider_count, facility_count)
    
    logger.info(f"Generated provider network with {len(network.get('providers', []))} providers, {len(network.get('facilities', []))} facilities, and {len(network.get('relationships', []))} relationships")
    
    return network


def generate_pharmacy_benefit(config: Dict, members: List[Dict], seed: int = None) -> Dict[str, Any]:
    """
    Generate synthetic pharmacy benefit.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate pharmacy claims with.
        seed: Random seed (overrides config).
        
    Returns:
        Dictionary containing the generated pharmacy benefit data.
    """
    # Get medication and claim counts from config
    pharmacy_config = config.get('pharmacy_benefit_config', {})
    medication_count = pharmacy_config.get('medication_count', 200)
    claim_count_config = pharmacy_config.get('claims_per_member', {
        'min': 0,
        'max': 10,
        'mean': 3
    })
    
    # Calculate total claims to generate
    mean_claims_per_member = claim_count_config.get('mean', 3)
    total_claims = int(len(members) * mean_claims_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating pharmacy benefit with {medication_count} medications and approximately {total_claims} claims with seed {seed}")
    
    # Create pharmacy benefit generator
    pharmacy_generator = PharmacyBenefitGenerator(config, seed)
    
    # Generate pharmacy benefit
    pharmacy_benefit = pharmacy_generator.generate(medication_count, total_claims, members)
    
    logger.info(f"Generated pharmacy benefit with {len(pharmacy_benefit.get('medications', []))} medications, 1 formulary, and {len(pharmacy_benefit.get('pharmacy_claims', []))} pharmacy claims")
    
    return pharmacy_benefit


def generate_authorization_rules(config: Dict, members: List[Dict], seed: int = None) -> Dict[str, Any]:
    """
    Generate synthetic authorization rules and decisions.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate authorization decisions with.
        seed: Random seed (overrides config).
        
    Returns:
        Dictionary containing the generated authorization rules and decisions.
    """
    # Get rule and decision counts from config
    rules_config = config.get('authorization_rules_config', {})
    rule_count = rules_config.get('rule_count', 50)
    decision_count_config = rules_config.get('decisions_per_member', {
        'min': 0,
        'max': 3,
        'mean': 1
    })
    
    # Calculate total decisions to generate
    mean_decisions_per_member = decision_count_config.get('mean', 1)
    total_decisions = int(len(members) * mean_decisions_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating {rule_count} authorization rules and approximately {total_decisions} decisions with seed {seed}")
    
    # Create authorization rules engine
    rules_engine = AuthorizationRulesEngine(config, seed)
    
    # Generate authorization rules and decisions
    auth_rules_data = rules_engine.generate(rule_count, total_decisions, members)
    
    logger.info(f"Generated {len(auth_rules_data.get('rules', []))} authorization rules and {len(auth_rules_data.get('decisions', []))} authorization decisions")
    
    return auth_rules_data


def validate_data_consistency(config: Dict, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data consistency across different domains.
    
    Args:
        config: Configuration dictionary.
        data: Dictionary containing data from different domains.
        
    Returns:
        Dictionary containing validation results.
    """
    logger.info("Validating data consistency")
    
    # Create data consistency validator
    validator = DataConsistencyValidator(config)
    
    # Validate member data
    member_validation = validator.validate_member_data(data.get('members', []))
    
    # Validate claims data
    claims_validation = validator.validate_claims_data(data.get('claims', []), data.get('members', []))
    
    # Validate enhanced data models
    enhanced_validation = validator.validate_enhanced_data_models(data, data.get('members', []))
    
    # Validate cross-domain consistency
    cross_domain_validation = validator.validate_cross_domain_consistency(data)
    
    # Combine validation results
    validation_results = {
        'member_validation': member_validation,
        'claims_validation': claims_validation,
        'enhanced_validation': enhanced_validation,
        'cross_domain_validation': cross_domain_validation
    }
    
    # Count total errors and warnings
    total_errors = sum(len(result.get('errors', [])) for result in validation_results.values())
    total_warnings = sum(len(result.get('warnings', [])) for result in validation_results.values())
    
    logger.info(f"Data consistency validation complete: {total_errors} errors, {total_warnings} warnings")
    
    return validation_results


def save_enhanced_data(data: Dict[str, Any], data_type: str, output_dir: str, skip_raw: bool = False) -> None:
    """
    Save generated enhanced data to JSON files.
    
    Args:
        data: Dictionary containing enhanced data.
        data_type: Type of data (care_episodes, sdoh_assessments, etc.).
        output_dir: Output directory.
        skip_raw: Whether to skip saving raw data.
    """
    if not data:
        logger.warning(f"No {data_type} data to save")
        return
    
    if not skip_raw:
        # Save raw data
        raw_output_path = get_output_path(os.path.join(output_dir, 'raw'), f'{data_type}.json')
        with open(raw_output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {data_type} to {raw_output_path}")
    
    # Save processed data (for enhanced data, we save the same data to processed)
    processed_output_path = get_output_path(os.path.join(output_dir, 'processed'), f'{data_type}.json')
    with open(processed_output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {data_type} to {processed_output_path}")


def generate_enhanced_data_models(config: Dict, member_dicts: List[Dict], output_dir: str, 
                                 skip_raw: bool = False, seed: int = None) -> Dict[str, Any]:
    """
    Generate and save enhanced data models (Phase 7).
    
    Args:
        config: Configuration dictionary.
        member_dicts: List of member dictionaries.
        output_dir: Output directory.
        skip_raw: Whether to skip saving raw data.
        seed: Random seed (overrides config).
        
    Returns:
        Dictionary containing all generated enhanced data.
    """
    logger.info("Generating enhanced data models (Phase 7)")
    
    # Generate care episodes
    care_episodes = generate_care_episodes(config, member_dicts, seed)
    care_episode_dicts = [episode.to_dict() for episode in care_episodes]
    save_enhanced_data(care_episode_dicts, 'care_episodes', output_dir, skip_raw)
    
    # Generate SDOH assessments
    sdoh_assessments = generate_sdoh_assessments(config, member_dicts, seed)
    sdoh_assessment_dicts = [assessment.to_dict() for assessment in sdoh_assessments]
    save_enhanced_data(sdoh_assessment_dicts, 'sdoh_assessments', output_dir, skip_raw)
    
    # Generate risk assessments
    risk_assessments = generate_risk_assessments(config, member_dicts, seed)
    risk_assessment_dicts = [assessment.to_dict() for assessment in risk_assessments]
    save_enhanced_data(risk_assessment_dicts, 'risk_assessments', output_dir, skip_raw)
    
    # Generate provider network
    provider_network = generate_provider_network(config, seed)
    save_enhanced_data(provider_network, 'provider_network', output_dir, skip_raw)
    
    # Generate pharmacy benefit
    pharmacy_benefit = generate_pharmacy_benefit(config, member_dicts, seed)
    save_enhanced_data(pharmacy_benefit, 'pharmacy_benefit', output_dir, skip_raw)
    
    # Generate authorization rules
    auth_rules_data = generate_authorization_rules(config, member_dicts, seed)
    save_enhanced_data(auth_rules_data, 'authorization_rules', output_dir, skip_raw)
    
    # Combine all data for validation
    all_data = {
        'members': member_dicts,
        'care_episodes': care_episode_dicts,
        'sdoh_assessments': sdoh_assessment_dicts,
        'risk_assessments': risk_assessment_dicts,
        'provider_network': provider_network,
        'pharmacy_benefit': pharmacy_benefit,
        'authorization_rules': auth_rules_data
    }
    
    # Validate data consistency
    validation_results = validate_data_consistency(config, all_data)
    save_enhanced_data(validation_results, 'validation_results', output_dir, skip_raw)
    
    logger.info("Enhanced data model generation completed successfully")
    
    return all_data