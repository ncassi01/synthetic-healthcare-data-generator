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
from datetime import datetime
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
from src.generators.enhanced_clinical_note_generator import EnhancedClinicalNoteGenerator
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
    parser = argparse.ArgumentParser(description='Generate high-quality synthetic healthcare data')
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


def generate_statistics(members, claims, authorizations, clinical_notes, output_dir):
    """
    Generate comprehensive statistics on the generated data.
    
    Args:
        members: List of Member objects to analyze.
        claims: List of Claim objects to analyze.
        authorizations: List of Authorization objects to analyze.
        clinical_notes: List of ClinicalNote objects to analyze.
        output_dir: Output directory.
    """
    logger.info("Generating comprehensive statistics on the data")
    
    # Check data distribution
    distributions = check_data_distribution(members)
    
    # Add counts
    total_members = len(members)
    total_claims = len(claims)
    total_authorizations = len(authorizations)
    total_clinical_notes = len(clinical_notes)
    
    distributions['member_count'] = total_members
    distributions['claim_count'] = total_claims
    distributions['authorization_count'] = total_authorizations
    distributions['clinical_note_count'] = total_clinical_notes
    
    # Add claims by month
    claims_by_month = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_counts = {month: 0 for month in months}
    
    for claim in claims:
        if isinstance(claim, dict):
            date_of_service = claim.get('date_of_service')
        else:
            date_of_service = claim.date_of_service if hasattr(claim, 'date_of_service') else None
            
        if date_of_service:
            try:
                if isinstance(date_of_service, str):
                    date_obj = datetime.strptime(date_of_service, '%Y-%m-%d')
                else:
                    date_obj = date_of_service
                month = months[date_obj.month - 1]
                month_counts[month] += 1
            except (ValueError, IndexError):
                pass
    
    claims_by_month = [{"month": month, "count": count} for month, count in month_counts.items()]
    distributions['claims_by_month'] = claims_by_month
    
    # Add claim status distribution
    claim_status_counts = {}
    for claim in claims:
        if isinstance(claim, dict):
            status = claim.get('status', 'Unknown')
        else:
            status = claim.status if hasattr(claim, 'status') else 'Unknown'
        claim_status_counts[status] = claim_status_counts.get(status, 0) + 1
    
    claim_status_distribution = [
        {'status': status, 'count': count}
        for status, count in claim_status_counts.items()
    ]
    distributions['claim_status_distribution'] = claim_status_distribution
    
    # Add top diagnoses
    diagnosis_counts = {}
    for claim in claims:
        if isinstance(claim, dict):
            diagnosis_codes = claim.get('diagnosis_codes', [])
        else:
            diagnosis_codes = claim.diagnosis_codes if hasattr(claim, 'diagnosis_codes') else []
        
        for code in diagnosis_codes:
            diagnosis_counts[code] = diagnosis_counts.get(code, 0) + 1
    
    # Sort by count and take top 10
    top_diagnoses = []
    for code, count in sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        description = ""
        if code == "I10":
            description = "Essential hypertension"
        elif code == "E11.9":
            description = "Type 2 diabetes mellitus without complications"
        elif code == "E78.5":
            description = "Hyperlipidemia, unspecified"
        elif code == "J45.909":
            description = "Unspecified asthma, uncomplicated"
        elif code == "F32.9":
            description = "Major depressive disorder, single episode, unspecified"
        elif code == "F41.9":
            description = "Anxiety disorder, unspecified"
        elif code == "K21.9":
            description = "Gastro-esophageal reflux disease without esophagitis"
        elif code == "E03.9":
            description = "Hypothyroidism, unspecified"
        elif code == "M19.90":
            description = "Unspecified osteoarthritis, unspecified site"
        elif code == "M54.5":
            description = "Low back pain"
        else:
            description = f"Diagnosis code {code}"
            
        top_diagnoses.append({
            'code': code,
            'count': count,
            'description': description
        })
    
    distributions['top_diagnoses'] = top_diagnoses
    
    # Add authorization types
    auth_type_counts = {}
    for auth in authorizations:
        if isinstance(auth, dict):
            service_lines = auth.get('service_lines', [])
        else:
            service_lines = auth.service_lines if hasattr(auth, 'service_lines') else []
        
        if service_lines:
            for service_line in service_lines:
                if isinstance(service_line, dict):
                    service_type = service_line.get('service_type', 'Unknown')
                else:
                    service_type = service_line.service_type if hasattr(service_line, 'service_type') else 'Unknown'
                auth_type_counts[service_type] = auth_type_counts.get(service_type, 0) + 1
        else:
            # Fallback to top-level type if it exists
            if isinstance(auth, dict):
                auth_type = auth.get('type', 'Unknown')
            else:
                auth_type = auth.type if hasattr(auth, 'type') else 'Unknown'
            auth_type_counts[auth_type] = auth_type_counts.get(auth_type, 0) + 1
    
    authorization_types = [
        {'type': auth_type, 'count': count}
        for auth_type, count in auth_type_counts.items()
    ]
    distributions['authorization_types'] = authorization_types
    
    # Add member age distribution
    age_ranges = {
        '0-17': 0,
        '18-34': 0,
        '35-50': 0,
        '51-64': 0,
        '65+': 0
    }
    
    for member in members:
        if isinstance(member, dict):
            age = member.get('age', 0)
        else:
            age = member.age if hasattr(member, 'age') else 0
        
        if age < 18:
            age_ranges['0-17'] += 1
        elif age < 35:
            age_ranges['18-34'] += 1
        elif age < 51:
            age_ranges['35-50'] += 1
        elif age < 65:
            age_ranges['51-64'] += 1
        else:
            age_ranges['65+'] += 1
    
    member_age_distribution = [
        {'range': age_range, 'count': count}
        for age_range, count in age_ranges.items()
    ]
    distributions['member_age_distribution'] = member_age_distribution
    
    # Save statistics
    stats_output_path = get_output_path(output_dir, 'statistics.json')
    with open(stats_output_path, 'w') as f:
        json.dump(distributions, f, indent=2)
    
    logger.info(f"Saved comprehensive statistics to {stats_output_path}")
    
    # Log some basic statistics
    logger.info(f"Total members: {total_members}")
    logger.info(f"Total claims: {total_claims}")
    logger.info(f"Total authorizations: {total_authorizations}")
    logger.info(f"Total clinical notes: {total_clinical_notes}")
    
    for category, dist in distributions.items():
        if isinstance(dist, dict) and category not in ['claims_by_month', 'claim_status_distribution', 'top_diagnoses', 'authorization_types', 'member_age_distribution']:
            logger.info(f"{category.capitalize()} distribution:")
            # Check if the values in the dictionary are dictionaries themselves
            if dist and isinstance(next(iter(dist.values())), dict):
                # For nested dictionaries like risk_score_ranges
                logger.info(f"  {category} contains nested data - see statistics.json for details")
            else:
                # For regular dictionaries
                sorted_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:5]
                for key, count in sorted_items:
                    percentage = (count / total_members) * 100 if total_members > 0 else 0
                    logger.info(f"  {key}: {count} ({percentage:.1f}%)")


def process_insurance_data(data, data_type, config, output_dir):
    """
    Process and enrich insurance data.
    
    Args:
        data: List of insurance objects to process.
        data_type: Type of insurance data (claims, authorizations, eobs).
        config: Configuration dictionary.
        output_dir: Output directory.
        
    Returns:
        List of processed insurance objects.
    """
    logger.info(f"Processing {len(data)} {data_type}")
    
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

def process_narrative_data(data, data_type, config, output_dir):
    """
    Process and enrich narrative data.
    
    Args:
        data: List of narrative objects to process.
        data_type: Type of narrative data (clinical_notes, communications, care_plans).
        config: Configuration dictionary.
        output_dir: Output directory.
        
    Returns:
        List of processed narrative objects.
    """
    logger.info(f"Processing {len(data)} {data_type}")
    
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
    
    # Generate and save statistics if applicable
    if data_type in ['clinical_notes', 'communications', 'care_plans']:
        stats = narrative_processor.get_statistics()
        if stats and data_type in stats:
            stats_output_path = get_output_path(os.path.join(output_dir, 'processed'), f'{data_type}_stats.json')
            with open(stats_output_path, 'w') as f:
                json.dump(stats[data_type], f, indent=2)
            logger.info(f"Saved {data_type} statistics to {stats_output_path}")
    
    return processed_data

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
        # Move statistics generation to the end to include all data types
        pass
    
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
    
    # Process claims if requested
    if args.process:
        process_insurance_data(claims, 'claims', config, args.output)
    
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
    
    # Process authorizations if requested
    if args.process:
        process_insurance_data(authorizations, 'authorizations', config, args.output)
    
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
    
    # Process EOBs if requested
    if args.process:
        process_insurance_data(eobs, 'eobs', config, args.output)
    
    # Generate clinical notes with provider-specific writing styles
    note_generator = EnhancedClinicalNoteGenerator(config, args.seed)
    notes = note_generator.generate(member_dicts)
    logger.info(f"Generated {len(notes)} clinical notes with provider-specific writing styles")
    
    # Save clinical notes
    note_dicts = [note.to_dict() for note in notes]
    if not args.skip_raw:
        raw_output_path = get_output_path(os.path.join(args.output, 'raw'), 'clinical_notes.json')
        with open(raw_output_path, 'w') as f:
            json.dump(note_dicts, f, indent=2)
        logger.info(f"Saved {len(notes)} enhanced clinical notes with provider-specific styles to {raw_output_path}")
    
    # Process clinical notes if requested
    if args.process:
        process_narrative_data(notes, 'clinical_notes', config, args.output)
    
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
    
    # Process communications if requested
    if args.process:
        process_narrative_data(communications, 'communications', config, args.output)
    
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
    
    # Process care plans if requested
    if args.process:
        process_narrative_data(care_plans, 'care_plans', config, args.output)
    
    # Generate comprehensive statistics if requested
    if args.stats:
        # Import datetime for date parsing
        from datetime import datetime
        generate_statistics(members, claims, authorizations, notes, args.output)
    
    logger.info("High-quality data generation complete")


if __name__ == "__main__":
    main()