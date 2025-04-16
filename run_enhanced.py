"""
Healthcare data generation script for the synthetic healthcare data generator.

This script generates realistic, interconnected synthetic healthcare data with high quality,
variability, and demographic-appropriate health conditions for testing and development purposes.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_generation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import generators
from src.generators.member_generator import MemberGenerator
from src.generators.claim_generator import ClaimGenerator
from src.generators.authorization_generator import AuthorizationGenerator
from src.generators.eob_generator import EOBGenerator
from src.generators.clinical_note_generator import ClinicalNoteGenerator
from src.generators.communication_generator import CommunicationGenerator
from src.generators.care_plan_generator import CarePlanGenerator

# Import processors
from src.processors.member_processor import MemberProcessor
from src.processors.insurance_processor import InsuranceProcessor
from src.processors.narrative_processor import NarrativeProcessor

# Import utilities
from src.utils.file_utils import load_config, get_output_path
from src.utils.validation_utils import validate_dataset, check_data_distribution


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate enhanced synthetic healthcare data')
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


def generate_members(config: Dict, count: int = None, seed: int = None):
    """
    Generate high-quality synthetic member data with realistic attributes.
    
    Args:
        config: Configuration dictionary.
        count: Number of members to generate (overrides config).
        seed: Random seed (overrides config).
        
    Returns:
        List of generated Member objects with realistic attributes.
    """
    # Get member count from arguments or config
    if count is None:
        count = config.get('data_generation', {}).get('member_count', 100)
    
    # Get seed from arguments or config
    if seed is None:
        seed = config.get('data_generation', {}).get('seed', 42)
    
    logger.info(f"Generating {count} members with high quality and realism (seed: {seed})")
    
    # Create member generator
    member_generator = MemberGenerator(config, seed)
    
    # Generate members
    members = member_generator.generate(count)
    
    logger.info(f"Generated {len(members)} members with high quality and realism")
    
    return members


def save_members(members, output_dir, skip_raw=False):
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


def process_members(members, config, output_dir):
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


def generate_statistics(members, output_dir):
    """
    Generate statistics on the generated data.
    
    Args:
        members: List of Member objects to analyze.
        output_dir: Output directory.
    """
    logger.info("Generating statistics on the enhanced data")
    
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
        if isinstance(dist, dict):
            logger.info(f"{category.capitalize()} distribution:")
            # Check if the values in the dictionary are dictionaries themselves
            if dist and isinstance(next(iter(dist.values())), dict):
                # For nested dictionaries like risk_score_ranges
                logger.info(f"  {category} contains nested data - see statistics.json for details")
            else:
                # For regular dictionaries
                sorted_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:5]
                for key, count in sorted_items:
                    percentage = (count / total_members) * 100
                    logger.info(f"  {key}: {count} ({percentage:.1f}%)")


def main():
    """Main entry point for the high-quality data generation script."""
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create output directories if they don't exist
    os.makedirs(os.path.join(args.output, 'raw'), exist_ok=True)
    os.makedirs(os.path.join(args.output, 'processed'), exist_ok=True)
    
    # Generate high-quality members with realistic attributes
    members = generate_members(config, args.count, args.seed)
    
    # Save members
    save_members(members, args.output, args.skip_raw)
    
    # Process members if requested
    if args.process:
        members = process_members(members, config, args.output)
    
    # Generate statistics if requested
    if args.stats:
        generate_statistics(members, args.output)
    
    # Generate claims and other data using the high-quality members
    member_dicts = [member.to_dict() for member in members]
    
    # Generate claims
    claim_generator = ClaimGenerator(config, args.seed)
    claims = claim_generator.generate(len(members) * 3, member_dicts)
    logger.info(f"Generated {len(claims)} claims")
    
    # Save claims
    claim_dicts = [claim.to_dict() for claim in claims]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'claims.json')
        with open(raw_output_path, 'w') as f:
            json.dump(claim_dicts, f, indent=2)
        logger.info(f"Saved {len(claims)} claims to {raw_output_path}")
    
    # Generate authorizations
    auth_generator = AuthorizationGenerator(config, args.seed)
    authorizations = auth_generator.generate(len(members), member_dicts)
    logger.info(f"Generated {len(authorizations)} authorizations")
    
    # Save authorizations
    auth_dicts = [auth.to_dict() for auth in authorizations]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'authorizations.json')
        with open(raw_output_path, 'w') as f:
            json.dump(auth_dicts, f, indent=2)
        logger.info(f"Saved {len(authorizations)} authorizations to {raw_output_path}")
    
    # Generate EOBs
    eob_generator = EOBGenerator(config, args.seed)
    eobs = eob_generator.generate(claims)
    logger.info(f"Generated {len(eobs)} EOBs")
    
    # Save EOBs
    eob_dicts = [eob.to_dict() for eob in eobs]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'eobs.json')
        with open(raw_output_path, 'w') as f:
            json.dump(eob_dicts, f, indent=2)
        logger.info(f"Saved {len(eobs)} EOBs to {raw_output_path}")
    
    # Generate clinical notes
    note_generator = ClinicalNoteGenerator(config, args.seed)
    notes = note_generator.generate(member_dicts)
    logger.info(f"Generated {len(notes)} clinical notes")
    
    # Save clinical notes
    note_dicts = [note.to_dict() for note in notes]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'clinical_notes.json')
        with open(raw_output_path, 'w') as f:
            json.dump(note_dicts, f, indent=2)
        logger.info(f"Saved {len(notes)} clinical notes to {raw_output_path}")
    
    # Generate communications
    comm_generator = CommunicationGenerator(config, args.seed)
    communications = comm_generator.generate(member_dicts, claim_dicts, auth_dicts)
    logger.info(f"Generated {len(communications)} communications")
    
    # Save communications
    comm_dicts = [comm.to_dict() for comm in communications]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'communications.json')
        with open(raw_output_path, 'w') as f:
            json.dump(comm_dicts, f, indent=2)
        logger.info(f"Saved {len(communications)} communications to {raw_output_path}")
    
    # Generate care plans
    care_plan_generator = CarePlanGenerator(config, args.seed)
    care_plans = care_plan_generator.generate(member_dicts)
    logger.info(f"Generated {len(care_plans)} care plans")
    
    # Save care plans
    care_plan_dicts = [plan.to_dict() for plan in care_plans]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'care_plans.json')
        with open(raw_output_path, 'w') as f:
            json.dump(care_plan_dicts, f, indent=2)
        logger.info(f"Saved {len(care_plans)} care plans to {raw_output_path}")
    
    logger.info("High-quality data generation complete")


if __name__ == "__main__":
    main()