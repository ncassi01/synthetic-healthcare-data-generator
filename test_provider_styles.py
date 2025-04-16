"""
Test script to demonstrate provider-specific writing styles.

This script generates clinical notes for the same patient data using different provider styles
to showcase the differences in writing styles.
"""

import json
import os
import random
import sys
from datetime import datetime

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.generators.enhanced_clinical_note_generator import EnhancedClinicalNoteGenerator
from src.models.member import Member

# Set up a seed for reproducibility
SEED = 42
random.seed(SEED)

# Create a simple configuration
config = {
    "clinical_note_config": {
        "notes_per_member": {
            "min": 1,
            "max": 1
        }
    }
}

def create_test_member():
    """Create a test member with realistic conditions and medications."""
    return {
        "id": "MEM00000001",
        "first_name": "John",
        "last_name": "Doe",
        "age": 65,
        "demographics": {
            "gender": "male",
            "date_of_birth": "1960-05-15",
            "race": "White",
            "ethnicity": "Non-Hispanic",
            "language": "en",
            "marital_status": "Married"
        },
        "conditions": [
            "Hypertension",
            "Type 2 Diabetes",
            "Hyperlipidemia"
        ],
        "medications": [
            "Lisinopril",
            "Metformin",
            "Atorvastatin"
        ],
        "procedures": [
            "Annual Physical",
            "Lipid Panel",
            "HbA1c Test"
        ]
    }

def main():
    """Generate clinical notes with different provider styles and display them."""
    # Create a test member
    member = create_test_member()
    
    # Create the enhanced clinical note generator
    generator = EnhancedClinicalNoteGenerator(config, SEED)
    
    # Override the provider styles dictionary to force specific styles
    generator.provider_styles = {
        "PROV10001": "concise",
        "PROV10002": "detailed",
        "PROV10003": "balanced"
    }
    
    # Generate notes with each provider style
    notes = []
    
    for provider_id, style in generator.provider_styles.items():
        # Create a copy of the member to avoid modifying the original
        member_copy = member.copy()
        
        # Generate a note with this provider
        note_date = datetime.now()
        
        # Generate the note content with the provider's style
        chief_complaint = generator._generate_chief_complaint(member["conditions"], member["medications"])
        subjective = generator._generate_subjective(member["age"], member["demographics"]["gender"], 
                                                  member["conditions"], chief_complaint, style)
        objective = generator._generate_objective(member["conditions"], style)
        assessment = generator._generate_assessment(member["conditions"], style)
        plan = generator._generate_plan(member["conditions"], member["medications"], style)
        
        # Create a dictionary to represent the note
        note = {
            "provider_id": provider_id,
            "provider_style": style,
            "chief_complaint": chief_complaint,
            "subjective": subjective,
            "objective": objective,
            "assessment": assessment,
            "plan": plan
        }
        
        notes.append(note)
    
    # Display the notes
    print("\n" + "="*80)
    print("PROVIDER STYLE COMPARISON FOR THE SAME PATIENT")
    print("="*80)
    
    for note in notes:
        print(f"\n\nPROVIDER: {note['provider_id']} (Style: {note['provider_style'].upper()})")
        print("-"*80)
        print(f"CHIEF COMPLAINT: {note['chief_complaint']}")
        print("\nSUBJECTIVE:")
        print(note['subjective'])
        print("\nOBJECTIVE:")
        print(note['objective'])
        print("\nASSESSMENT:")
        print(note['assessment'])
        print("\nPLAN:")
        print(note['plan'])
        print("-"*80)
    
    # Save the notes to a file for reference
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "provider_style_comparison.json"), "w") as f:
        json.dump(notes, f, indent=2)
    
    print(f"\nNotes saved to {os.path.join(output_dir, 'provider_style_comparison.json')}")

if __name__ == "__main__":
    main()