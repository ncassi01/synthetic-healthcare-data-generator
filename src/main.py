"""
Main entry point for the synthetic healthcare data generator.

This module provides the main functionality to generate synthetic healthcare data.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Any, Union

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generators.member_generator import MemberGenerator
from src.generators.claim_generator import ClaimGenerator
from src.generators.authorization_generator import AuthorizationGenerator
from src.generators.eob_generator import EOBGenerator
from src.generators.plan_generator import PlanGenerator
from src.generators.clinical_note_generator import ClinicalNoteGenerator
from src.generators.communication_generator import CommunicationGenerator
from src.generators.care_plan_generator import CarePlanGenerator
from src.generators.authorization_rationale_generator import AuthorizationRationaleGenerator

# Import unstructured data generators (Phase 6)
from src.unstructured.patient_generated import PatientGeneratedHealthDataGenerator
from src.unstructured.provider_communications import ProviderCommunicationsGenerator
from src.unstructured.insurance_communications import InsuranceCommunicationsGenerator
from src.unstructured.mental_health import MentalHealthNarrativesGenerator
from src.unstructured.telehealth import TelehealthDocumentationGenerator

from src.models.member import Member
from src.models.insurance import Claim, PriorAuthorization, ExplanationOfBenefit, PlanCoverage
from src.models.narrative import ClinicalNote, CommunicationRecord, CarePlan, AuthorizationRationale

from src.processors.member_processor import MemberProcessor
from src.processors.insurance_processor import InsuranceProcessor
from src.processors.narrative_processor import NarrativeProcessor

from src.utils.file_utils import load_config, get_output_path
from src.utils.validation_utils import validate_dataset, check_data_distribution


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate synthetic healthcare data')
    parser.add_argument('--config', type=str, default='config/config.json',
                        help='Path to configuration file')
    parser.add_argument('--output', type=str, default='output',
                        help='Output directory')
    parser.add_argument('--count', type=int, default=None,
                        help='Number of members to generate (overrides config)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed (overrides config)')
    parser.add_argument('--validate', action='store_true',
                        help='Validate generated data')
    parser.add_argument('--stats', action='store_true',
                        help='Generate statistics on the data')
    parser.add_argument('--process', action='store_true',
                        help='Process and enrich generated data')
    parser.add_argument('--skip-raw', action='store_true',
                        help='Skip saving raw data (only save processed data)')
    return parser.parse_args()


def generate_members(config: Dict, count: int = None, seed: int = None) -> List[Member]:
    """
    Generate synthetic member data.
    
    Args:
        config: Configuration dictionary.
        count: Number of members to generate (overrides config).
        seed: Random seed (overrides config).
        
    Returns:
        List of generated Member objects.
    """
    # Get member count from arguments or config
    if count is None:
        count = config.get('data_generation', {}).get('member_count', 100)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating {count} members with seed {seed}")
    
    # Create member generator
    member_generator = MemberGenerator(config, seed)
    
    # Generate members
    members = member_generator.generate(count)
    
    logger.info(f"Generated {len(members)} members")
    
    return members


def save_members(members: List[Member], output_dir: str, skip_raw: bool = False) -> None:
    """
    Save generated member data to JSON files.
    
    Args:
        members: List of Member objects to save.
        output_dir: Output directory.
        skip_raw: Whether to skip saving raw data.
    """
    # Convert members to dictionaries
    member_dicts = [member.to_dict() for member in members]
    
    if not skip_raw:
        # Save raw data
        raw_output_path = get_output_path(os.path.join(output_dir, 'raw'), 'members.json')
        with open(raw_output_path, 'w') as f:
            json.dump(member_dicts, f, indent=2)
        
        logger.info(f"Saved {len(members)} members to {raw_output_path}")


def process_members(members: List[Member], config: Dict, output_dir: str) -> List[Member]:
    """
    Process and enrich member data.
    
    Args:
        members: List of Member objects to process.
        config: Configuration dictionary.
        output_dir: Output directory.
        
    Returns:
        List of processed Member objects.
    """
    logger.info("Processing and enriching member data")
    
    # Create member processor
    member_processor = MemberProcessor(config)
    
    # Process members
    processed_members = member_processor.process(members)
    
    logger.info(f"Processed {len(processed_members)} members")
    
    # Convert processed members to dictionaries
    processed_member_dicts = [member.to_dict() for member in processed_members]
    
    # Save processed data
    processed_output_path = get_output_path(os.path.join(output_dir, 'processed'), 'members.json')
    with open(processed_output_path, 'w') as f:
        json.dump(processed_member_dicts, f, indent=2)
    
    logger.info(f"Saved {len(processed_members)} processed members to {processed_output_path}")
    
    return processed_members


def generate_statistics(members: List[Member], output_dir: str) -> None:
    """
    Generate statistics on the generated data.
    
    Args:
        members: List of Member objects to analyze.
        output_dir: Output directory.
    """
    logger.info("Generating statistics on the data")
    
    # Check data distribution
    distributions = check_data_distribution(members)
    
    # Save statistics
    stats_output_path = get_output_path(output_dir, 'statistics.json')
    with open(stats_output_path, 'w') as f:
        json.dump(distributions, f, indent=2)
    
    logger.info(f"Saved statistics to {stats_output_path}")
    
    # Log some basic statistics
    total_members = len(members)
    logger.info(f"Total members: {total_members}")
    
    for category, dist in distributions.items():
        if category == 'age_groups' or category.startswith('risk_score_ranges'):
            # These are already dictionaries, so we can log them directly
            logger.info(f"{category.capitalize()} distribution:")
            for key, count in dist.items():
                if isinstance(count, dict):
                    # This is for nested dictionaries like risk_score_ranges
                    logger.info(f"  {key}:")
                    for subkey, subcount in count.items():
                        percentage = (subcount / total_members) * 100
                        logger.info(f"    {subkey}: {subcount} ({percentage:.1f}%)")
                else:
                    percentage = (count / total_members) * 100
                    logger.info(f"  {key}: {count} ({percentage:.1f}%)")
        else:
            # For other categories, log the top 5 items
            logger.info(f"{category.capitalize()} distribution (top 5):")
            sorted_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:5]
            for key, count in sorted_items:
                percentage = (count / total_members) * 100
                logger.info(f"  {key}: {count} ({percentage:.1f}%)")


def generate_claims(config: Dict, members: List[Dict], seed: int = None) -> List[Claim]:
    """
    Generate synthetic claim data.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate claims with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated Claim objects.
    """
    # Get claim count from config
    claim_config = config.get('claim_config', {})
    claim_count_config = claim_config.get('claim_count_per_member', {
        'min': 0,
        'max': 10,
        'mean': 3,
        'std_dev': 2
    })
    
    # Calculate total claims to generate
    mean_claims_per_member = claim_count_config.get('mean', 3)
    total_claims = int(len(members) * mean_claims_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_claims} claims with seed {seed}")
    
    # Create claim generator
    claim_generator = ClaimGenerator(config, seed)
    
    # Generate claims
    claims = claim_generator.generate(total_claims, members)
    
    logger.info(f"Generated {len(claims)} claims")
    
    return claims


def generate_authorizations(config: Dict, members: List[Dict], seed: int = None) -> List[PriorAuthorization]:
    """
    Generate synthetic prior authorization data.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate authorizations with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated PriorAuthorization objects.
    """
    # Get authorization count from config
    auth_config = config.get('authorization_config', {})
    auth_count_config = auth_config.get('auth_count_per_member', {
        'min': 0,
        'max': 5,
        'mean': 1,
        'std_dev': 1
    })
    
    # Calculate total authorizations to generate
    mean_auths_per_member = auth_count_config.get('mean', 1)
    total_auths = int(len(members) * mean_auths_per_member)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_auths} prior authorizations with seed {seed}")
    
    # Create authorization generator
    auth_generator = AuthorizationGenerator(config, seed)
    
    # Generate authorizations
    authorizations = auth_generator.generate(total_auths, members)
    
    logger.info(f"Generated {len(authorizations)} prior authorizations")
    
    return authorizations


def generate_eobs(config: Dict, claims: List[Claim], seed: int = None) -> List[ExplanationOfBenefit]:
    """
    Generate synthetic EOB data based on claims.
    
    Args:
        config: Configuration dictionary.
        claims: List of Claim objects to generate EOBs for.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated ExplanationOfBenefit objects.
    """
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating EOBs for eligible claims with seed {seed}")
    
    # Create EOB generator
    eob_generator = EOBGenerator(config, seed)
    
    # Generate EOBs
    eobs = eob_generator.generate(claims)
    
    logger.info(f"Generated {len(eobs)} EOBs")
    
    return eobs


def generate_plans(config: Dict, seed: int = None) -> List[PlanCoverage]:
    """
    Generate synthetic plan coverage data.
    
    Args:
        config: Configuration dictionary.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated PlanCoverage objects.
    """
    # Get plan count from config
    plan_config = config.get('plan_config', {})
    plan_count = plan_config.get('plan_count', 20)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating {plan_count} insurance plans with seed {seed}")
    
    # Create plan generator
    plan_generator = PlanGenerator(config, seed)
    
    # Generate plans
    plans = plan_generator.generate(plan_count)
    
    logger.info(f"Generated {len(plans)} insurance plans")
    
    return plans


def save_insurance_data(data: List[Any], data_type: str, output_dir: str, skip_raw: bool = False) -> None:
    """
    Save generated insurance data to JSON files.
    
    Args:
        data: List of insurance objects to save.
        data_type: Type of data (claims, authorizations, eobs, plans).
        output_dir: Output directory.
        skip_raw: Whether to skip saving raw data.
    """
    if not data:
        logger.warning(f"No {data_type} data to save")
        return
    
    # Convert objects to dictionaries
    data_dicts = [item.to_dict() for item in data]
    
    if not skip_raw:
        # Save raw data
        raw_output_path = get_output_path(os.path.join(output_dir, 'raw'), f'{data_type}.json')
        with open(raw_output_path, 'w') as f:
            json.dump(data_dicts, f, indent=2)
        
        logger.info(f"Saved {len(data)} {data_type} to {raw_output_path}")


def process_insurance_data(data: List[Any], data_type: str, config: Dict, output_dir: str) -> List[Any]:
    """
    Process and enrich insurance data.
    
    Args:
        data: List of insurance objects to process.
        data_type: Type of data (claims, authorizations, eobs, plans).
        config: Configuration dictionary.
        output_dir: Output directory.
        
    Returns:
        List of processed insurance objects.
    """
    if not data:
        logger.warning(f"No {data_type} data to process")
        return []
    
    logger.info(f"Processing and enriching {data_type} data")
    
    # Create insurance processor
    insurance_processor = InsuranceProcessor(config)
    
    # Process data
    processed_data = insurance_processor.process(data)
    
    logger.info(f"Processed {len(processed_data)} {data_type}")
    
    # Convert processed data to dictionaries
    processed_data_dicts = [item.to_dict() for item in processed_data]
    
    # Save processed data
    processed_output_path = get_output_path(os.path.join(output_dir, 'processed'), f'{data_type}.json')
    with open(processed_output_path, 'w') as f:
        json.dump(processed_data_dicts, f, indent=2)
    
    logger.info(f"Saved {len(processed_data)} processed {data_type} to {processed_output_path}")
    
    return processed_data


def generate_clinical_notes(config: Dict, members: List[Dict], seed: int = None) -> List[ClinicalNote]:
    """
    Generate synthetic clinical notes based on member data.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to generate notes for.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated ClinicalNote objects.
    """
    # Get clinical note count from config
    note_config = config.get('clinical_note_config', {})
    note_count_config = note_config.get('notes_per_member', {
        'min': 1,
        'max': 5
    })
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating clinical notes with seed {seed}")
    
    # Create clinical note generator
    note_generator = ClinicalNoteGenerator(config, seed)
    
    # Generate clinical notes
    notes = note_generator.generate(members)
    
    logger.info(f"Generated {len(notes)} clinical notes")
    
    return notes


def generate_communications(config: Dict, members: List[Dict], claims: List[Dict] = None,
                           authorizations: List[Dict] = None, seed: int = None) -> List[CommunicationRecord]:
    """
    Generate synthetic communication records based on member data.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to generate communications for.
        claims: Optional list of claim dictionaries to reference in communications.
        authorizations: Optional list of authorization dictionaries to reference.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated CommunicationRecord objects.
    """
    # Get communication count from config
    comm_config = config.get('communication_config', {})
    comm_count_config = comm_config.get('communications_per_member', {
        'min': 2,
        'max': 8
    })
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating communication records with seed {seed}")
    
    # Create communication generator
    comm_generator = CommunicationGenerator(config, seed)
    
    # Generate communications
    communications = comm_generator.generate(members, claims, authorizations)
    
    logger.info(f"Generated {len(communications)} communication records")
    
    return communications


def generate_care_plans(config: Dict, members: List[Dict], seed: int = None) -> List[CarePlan]:
    """
    Generate synthetic care plans based on member data.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to generate care plans for.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated CarePlan objects.
    """
    # Get care plan count from config
    plan_config = config.get('care_plan_config', {})
    plan_count_config = plan_config.get('care_plans_per_member', {
        'min': 1,
        'max': 3
    })
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating care plans with seed {seed}")
    
    # Create care plan generator
    plan_generator = CarePlanGenerator(config, seed)
    
    # Generate care plans
    care_plans = plan_generator.generate(members)
    
    logger.info(f"Generated {len(care_plans)} care plans")
    
    return care_plans


def generate_authorization_rationales(config: Dict, authorizations: List[Dict],
                                     members: List[Dict], seed: int = None) -> List[AuthorizationRationale]:
    """
    Generate synthetic authorization rationales based on authorization data.
    
    Args:
        config: Configuration dictionary.
        authorizations: List of authorization dictionaries to generate rationales for.
        members: List of member dictionaries to reference.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated AuthorizationRationale objects.
    """
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating authorization rationales with seed {seed}")
    
    # Create authorization rationale generator
    rationale_generator = AuthorizationRationaleGenerator(config, seed)
    
    # Generate authorization rationales
    rationales = rationale_generator.generate(authorizations, members)
    
    logger.info(f"Generated {len(rationales)} authorization rationales")
    
    return rationales


def save_narrative_data(data: List[Any], data_type: str, output_dir: str, skip_raw: bool = False) -> None:
    """
    Save generated narrative content data to JSON files.
    
    Args:
        data: List of narrative content objects to save.
        data_type: Type of data (clinical_notes, communications, care_plans, authorization_rationales).
        output_dir: Output directory.
        skip_raw: Whether to skip saving raw data.
    """
    if not data:
        logger.warning(f"No {data_type} data to save")
        return
    
    # Convert objects to dictionaries
    data_dicts = [item.to_dict() for item in data]
    
    if not skip_raw:
        # Save raw data
        raw_output_path = get_output_path(os.path.join(output_dir, 'raw'), f'{data_type}.json')
        with open(raw_output_path, 'w') as f:
            json.dump(data_dicts, f, indent=2)
        
        logger.info(f"Saved {len(data)} {data_type} to {raw_output_path}")


def process_narrative_data(data: List[Any], data_type: str, config: Dict, output_dir: str) -> List[Any]:
    """
    Process and enrich narrative content data.
    
    Args:
        data: List of narrative content objects to process.
        data_type: Type of data (clinical_notes, communications, care_plans, authorization_rationales).
        config: Configuration dictionary.
        output_dir: Output directory.
        
    Returns:
        List of processed narrative content objects.
    """
    if not data:
        logger.warning(f"No {data_type} data to process")
        return []
    
    logger.info(f"Processing and enriching {data_type} data")
    
    # Create narrative processor
    narrative_processor = NarrativeProcessor(config)
    
    # Process data
    processed_data = narrative_processor.process(data)
    
    logger.info(f"Processed {len(processed_data)} {data_type}")
    
    # Convert processed data to dictionaries
    processed_data_dicts = [item.to_dict() for item in processed_data]
    
    # Save processed data
    processed_output_path = get_output_path(os.path.join(output_dir, 'processed'), f'{data_type}.json')
    with open(processed_output_path, 'w') as f:
        json.dump(processed_data_dicts, f, indent=2)
    
    logger.info(f"Saved {len(processed_data)} processed {data_type} to {processed_output_path}")
    
    # Save statistics if available
    stats = narrative_processor.get_statistics()
    if stats:
        stats_output_path = get_output_path(os.path.join(output_dir, 'processed'), f'{data_type}_stats.json')
        with open(stats_output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved {data_type} statistics to {stats_output_path}")
    
    return processed_data


def generate_patient_generated_data(config: Dict, members: List[Dict], seed: int = None) -> List[Dict]:
    """
    Generate synthetic patient-generated health data.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate data with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated patient-generated health data entries.
    """
    # Get count from config
    pgd_config = config.get('patient_generated_data_config', {})
    pgd_count_config = pgd_config.get('entries_per_member', {
        'min': 1,
        'max': 5
    })
    
    # Calculate total entries to generate
    min_entries = pgd_count_config.get('min', 1)
    max_entries = pgd_count_config.get('max', 5)
    avg_entries = (min_entries + max_entries) / 2
    total_entries = int(len(members) * avg_entries)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_entries} patient-generated health data entries with seed {seed}")
    
    # Create generator
    pgd_generator = PatientGeneratedHealthDataGenerator(config, seed)
    
    # Extract member IDs
    member_ids = [member.get('id') for member in members]
    
    # Generate data
    pgd_entries = pgd_generator.generate(total_entries, member_ids)
    
    logger.info(f"Generated {len(pgd_entries)} patient-generated health data entries")
    
    return pgd_entries


def generate_provider_communications(config: Dict, members: List[Dict], seed: int = None) -> List[Dict]:
    """
    Generate synthetic provider-to-provider communications.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate data with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated provider communication entries.
    """
    # Get count from config
    pc_config = config.get('provider_communications_config', {})
    pc_count_config = pc_config.get('entries_per_member', {
        'min': 1,
        'max': 3
    })
    
    # Calculate total entries to generate
    min_entries = pc_count_config.get('min', 1)
    max_entries = pc_count_config.get('max', 3)
    avg_entries = (min_entries + max_entries) / 2
    total_entries = int(len(members) * avg_entries)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_entries} provider communication entries with seed {seed}")
    
    # Create generator
    pc_generator = ProviderCommunicationsGenerator(config, seed)
    
    # Extract member IDs
    member_ids = [member.get('id') for member in members]
    
    # Generate data
    pc_entries = pc_generator.generate(total_entries, member_ids)
    
    logger.info(f"Generated {len(pc_entries)} provider communication entries")
    
    return pc_entries


def generate_insurance_communications(config: Dict, members: List[Dict], seed: int = None) -> List[Dict]:
    """
    Generate synthetic insurance communications.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate data with.
        claims: Optional list of claim dictionaries to reference.
        authorizations: Optional list of authorization dictionaries to reference.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated insurance communication entries.
    """
    # Get count from config
    ic_config = config.get('insurance_communications_config', {})
    ic_count_config = ic_config.get('entries_per_member', {
        'min': 1,
        'max': 3
    })
    
    # Calculate total entries to generate
    min_entries = ic_count_config.get('min', 1)
    max_entries = ic_count_config.get('max', 3)
    avg_entries = (min_entries + max_entries) / 2
    total_entries = int(len(members) * avg_entries)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_entries} insurance communication entries with seed {seed}")
    
    # Create generator
    ic_generator = InsuranceCommunicationsGenerator(config, seed)
    
    # Extract member IDs
    member_ids = [member.get('id') for member in members]
    # Generate data
    # The InsuranceCommunicationsGenerator.generate() method expects provider_ids as a list of strings
    # Generate some provider IDs
    provider_ids = [f"PRV{i:08d}" for i in range(20)]  # Generate 20 providers
    
    # Generate the insurance communications
    ic_entries = ic_generator.generate(total_entries, member_ids, provider_ids)
    
    logger.info(f"Generated {len(ic_entries)} insurance communication entries")
    
    return ic_entries


def generate_mental_health_narratives(config: Dict, members: List[Dict], seed: int = None) -> List[Dict]:
    """
    Generate synthetic mental health narratives.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate data with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated mental health narrative entries.
    """
    # Get count from config
    mh_config = config.get('mental_health_config', {})
    mh_count_config = mh_config.get('entries_per_member', {
        'min': 0,
        'max': 2
    })
    
    # Calculate total entries to generate
    min_entries = mh_count_config.get('min', 0)
    max_entries = mh_count_config.get('max', 2)
    avg_entries = (min_entries + max_entries) / 2
    total_entries = int(len(members) * avg_entries)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_entries} mental health narrative entries with seed {seed}")
    
    # Create generator
    mh_generator = MentalHealthNarrativesGenerator(config, seed)
    
    # Extract member IDs
    member_ids = [member.get('id') for member in members]
    
    # Generate data
    mh_entries = mh_generator.generate(total_entries, member_ids)
    
    logger.info(f"Generated {len(mh_entries)} mental health narrative entries")
    
    return mh_entries


def generate_telehealth_documentation(config: Dict, members: List[Dict], seed: int = None) -> List[Dict]:
    """
    Generate synthetic telehealth documentation.
    
    Args:
        config: Configuration dictionary.
        members: List of member dictionaries to associate data with.
        seed: Random seed (overrides config).
        
    Returns:
        List of generated telehealth documentation entries.
    """
    # Get count from config
    th_config = config.get('telehealth_config', {})
    th_count_config = th_config.get('entries_per_member', {
        'min': 0,
        'max': 3
    })
    
    # Calculate total entries to generate
    min_entries = th_count_config.get('min', 0)
    max_entries = th_count_config.get('max', 3)
    avg_entries = (min_entries + max_entries) / 2
    total_entries = int(len(members) * avg_entries)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating approximately {total_entries} telehealth documentation entries with seed {seed}")
    
    # Create generator
    th_generator = TelehealthDocumentationGenerator(config, seed)
    
    # Extract member IDs
    member_ids = [member.get('id') for member in members]
    
    # Generate data
    th_entries = th_generator.generate(total_entries, member_ids)
    
    logger.info(f"Generated {len(th_entries)} telehealth documentation entries")
    
    return th_entries


def save_unstructured_data(data: List[Dict], data_type: str, output_dir: str, skip_raw: bool = False) -> None:
    """
    Save generated unstructured data to JSON files.
    
    Args:
        data: List of unstructured data entries to save.
        data_type: Type of data (patient_generated, provider_communications, etc.).
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
        
        logger.info(f"Saved {len(data)} {data_type} to {raw_output_path}")
    
    # Save processed data (for unstructured data, we save the same data to processed)
    processed_output_path = get_output_path(os.path.join(output_dir, 'processed'), f'{data_type}.json')
    with open(processed_output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {len(data)} {data_type} to {processed_output_path}")


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Update logging configuration if specified in config
        log_config = config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        logging.getLogger().setLevel(log_level)
        
        if log_config.get('file'):
            file_handler = logging.FileHandler(log_config.get('file'))
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(file_handler)
        
        # Generate members
        members = generate_members(config, args.count, args.seed)
        
        # Validate member data if requested
        if args.validate:
            logger.info("Validating generated member data")
            validation_results = validate_dataset(members)
            
            if validation_results:
                logger.warning(f"Found validation errors in {len(validation_results)} members")
                validation_output_path = get_output_path(args.output, 'validation_errors.json')
                with open(validation_output_path, 'w') as f:
                    json.dump(validation_results, f, indent=2)
                logger.info(f"Saved validation errors to {validation_output_path}")
            else:
                logger.info("No validation errors found")
        
        # Save generated member data
        save_members(members, args.output, args.skip_raw)
        
        # Process and enrich member data if requested
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_members = process_members(members, config, args.output)
            
            # Use processed members for statistics if available
            if args.stats:
                generate_statistics(processed_members, args.output)
                
            # Convert processed members to dictionaries for insurance data generation
            member_dicts = [member.to_dict() for member in processed_members]
        else:
            # Use raw members for statistics if processing is not enabled
            if args.stats:
                generate_statistics(members, args.output)
                
            # Convert raw members to dictionaries for insurance data generation
            member_dicts = [member.to_dict() for member in members]
        
        # Generate insurance data (Phase 3)
        logger.info("Generating insurance data (Phase 3)")
        
        # Generate plan coverage data
        plans = generate_plans(config, args.seed)
        save_insurance_data(plans, 'plans', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_plans = process_insurance_data(plans, 'plans', config, args.output)
        
        # Generate claims
        claims = generate_claims(config, member_dicts, args.seed)
        save_insurance_data(claims, 'claims', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_claims = process_insurance_data(claims, 'claims', config, args.output)
            
            # Generate EOBs based on processed claims
            eobs = generate_eobs(config, processed_claims, args.seed)
            save_insurance_data(eobs, 'eobs', args.output, args.skip_raw)
            
            if args.process or config.get('processor_config', {}).get('enabled', False):
                processed_eobs = process_insurance_data(eobs, 'eobs', config, args.output)
        else:
            # Generate EOBs based on raw claims
            eobs = generate_eobs(config, claims, args.seed)
            save_insurance_data(eobs, 'eobs', args.output, args.skip_raw)
        
        # Generate prior authorizations
        authorizations = generate_authorizations(config, member_dicts, args.seed)
        save_insurance_data(authorizations, 'authorizations', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_authorizations = process_insurance_data(authorizations, 'authorizations', config, args.output)
        
        # Generate narrative content (Phase 4)
        logger.info("Generating narrative content (Phase 4)")
        
        # Generate clinical notes
        clinical_notes = generate_clinical_notes(config, member_dicts, args.seed)
        save_narrative_data(clinical_notes, 'clinical_notes', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_clinical_notes = process_narrative_data(clinical_notes, 'clinical_notes', config, args.output)
        
        # Generate communication records
        claim_dicts = [claim.to_dict() for claim in claims]
        auth_dicts = [auth.to_dict() for auth in authorizations]
        communications = generate_communications(config, member_dicts, claim_dicts, auth_dicts, args.seed)
        save_narrative_data(communications, 'communications', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_communications = process_narrative_data(communications, 'communications', config, args.output)
        
        # Generate care plans
        care_plans = generate_care_plans(config, member_dicts, args.seed)
        save_narrative_data(care_plans, 'care_plans', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_care_plans = process_narrative_data(care_plans, 'care_plans', config, args.output)
        
        # Generate authorization rationales
        auth_rationales = generate_authorization_rationales(config, auth_dicts, member_dicts, args.seed)
        save_narrative_data(auth_rationales, 'authorization_rationales', args.output, args.skip_raw)
        
        if args.process or config.get('processor_config', {}).get('enabled', False):
            processed_auth_rationales = process_narrative_data(auth_rationales, 'authorization_rationales', config, args.output)
        
        # Generate expanded unstructured data (Phase 6)
        logger.info("Generating expanded unstructured data (Phase 6)")
        
        # Generate patient-generated health data
        pgd_entries = generate_patient_generated_data(config, member_dicts, args.seed)
        save_unstructured_data(pgd_entries, 'patient_generated_data', args.output, args.skip_raw)
        
        # Generate provider-to-provider communications
        pc_entries = generate_provider_communications(config, member_dicts, args.seed)
        save_unstructured_data(pc_entries, 'provider_communications', args.output, args.skip_raw)
        
        # Generate insurance communications
        ic_entries = generate_insurance_communications(config, member_dicts, seed=args.seed)
        save_unstructured_data(ic_entries, 'insurance_communications', args.output, args.skip_raw)
        
        # Generate mental health narratives
        mh_entries = generate_mental_health_narratives(config, member_dicts, args.seed)
        save_unstructured_data(mh_entries, 'mental_health_narratives', args.output, args.skip_raw)
        
        # Generate telehealth documentation
        th_entries = generate_telehealth_documentation(config, member_dicts, args.seed)
        save_unstructured_data(th_entries, 'telehealth_documentation', args.output, args.skip_raw)
        
        logger.info("Data generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error generating data: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()