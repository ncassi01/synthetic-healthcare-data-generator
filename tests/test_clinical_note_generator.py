"""
Tests for the clinical note generator.

This module contains tests for the clinical note generator.
"""

import json
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generators.clinical_note_generator import ClinicalNoteGenerator
from src.models.narrative import ClinicalNote, NoteType


class TestClinicalNoteGenerator(unittest.TestCase):
    """Tests for the clinical note generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "clinical_note_config": {
                "notes_per_member": {
                    "min": 1,
                    "max": 3
                },
                "clinical_note_templates": {
                    "chief_complaint": [
                        "Test chief complaint for {condition}"
                    ],
                    "subjective": [
                        "Test subjective for {age}-year-old {gender} with {conditions}"
                    ],
                    "assessment": [
                        "Test assessment for {diagnosis}"
                    ],
                    "plan": [
                        "Test plan: {treatment_plan}"
                    ]
                }
            }
        }
        
        self.members = [
            {
                "id": "MEM001",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "age": 45,
                "demographics": {
                    "gender": "male",
                    "date_of_birth": "1980-01-15"
                },
                "conditions": ["diabetes", "hypertension"],
                "medications": ["metformin", "lisinopril"],
                "procedures": ["blood test", "eye exam"]
            },
            {
                "id": "MEM002",
                "first_name": "Jane",
                "last_name": "Smith",
                "full_name": "Jane Smith",
                "age": 35,
                "demographics": {
                    "gender": "female",
                    "date_of_birth": "1990-05-20"
                },
                "conditions": ["asthma", "allergies"],
                "medications": ["albuterol", "cetirizine"],
                "procedures": ["pulmonary function test", "allergy testing"]
            }
        ]
        
        # Create generator with fixed seed for reproducibility
        self.generator = ClinicalNoteGenerator(self.config, seed=42)
    
    def test_generator_initialization(self):
        """Test that the generator initializes correctly."""
        self.assertIsInstance(self.generator, ClinicalNoteGenerator)
        self.assertEqual(self.generator.seed, 42)
        self.assertEqual(self.generator.config, self.config)
    
    def test_generate_notes(self):
        """Test generating clinical notes."""
        notes = self.generator.generate(self.members)
        
        # Check that notes were generated
        self.assertGreater(len(notes), 0)
        
        # Check that all notes are of the correct type
        for note in notes:
            self.assertIsInstance(note, ClinicalNote)
            
            # Check that required fields are present and non-empty
            self.assertIsNotNone(note.id)
            self.assertIn(note.member_id, ["MEM001", "MEM002"])
            self.assertIsNotNone(note.provider_id)
            self.assertIsInstance(note.note_type, NoteType)
            self.assertIsInstance(note.date_of_service, datetime)
            self.assertGreater(len(note.chief_complaint), 0)
            self.assertGreater(len(note.subjective), 0)
            self.assertGreater(len(note.objective), 0)
            self.assertGreater(len(note.assessment), 0)
            self.assertGreater(len(note.plan), 0)
    
    def test_generate_with_count(self):
        """Test generating a specific number of notes."""
        count = 5
        notes = self.generator.generate(self.members, count=count)
        
        # Check that the correct number of notes were generated
        self.assertEqual(len(notes), count)
    
    def test_serialization(self):
        """Test that generated notes can be serialized to JSON."""
        notes = self.generator.generate(self.members, count=2)
        
        # Convert notes to dictionaries
        note_dicts = [note.to_dict() for note in notes]
        
        # Serialize to JSON
        json_str = json.dumps(note_dicts)
        
        # Deserialize from JSON
        deserialized = json.loads(json_str)
        
        # Check that deserialization worked
        self.assertEqual(len(deserialized), 2)
        self.assertEqual(deserialized[0]["id"], notes[0].id)
        self.assertEqual(deserialized[1]["id"], notes[1].id)
    
    def test_generate_chief_complaint(self):
        """Test generating a chief complaint."""
        conditions = ["diabetes", "hypertension"]
        medications = ["metformin", "lisinopril"]
        
        chief_complaint = self.generator._generate_chief_complaint(conditions, medications)
        
        # Check that the chief complaint is non-empty
        self.assertGreater(len(chief_complaint), 0)
        
        # Check that it contains one of the conditions
        self.assertTrue(any(condition in chief_complaint for condition in conditions))
    
    def test_generate_subjective(self):
        """Test generating a subjective section."""
        age = 45
        gender = "male"
        conditions = ["diabetes", "hypertension"]
        chief_complaint = "Diabetes follow-up"
        
        subjective = self.generator._generate_subjective(age, gender, conditions, chief_complaint)
        
        # Check that the subjective section is non-empty
        self.assertGreater(len(subjective), 0)
        
        # Check that it contains the age, gender, and at least one condition
        self.assertIn(str(age), subjective)
        self.assertIn(gender, subjective)
        self.assertTrue(any(condition in subjective for condition in conditions))
    
    def test_generate_objective(self):
        """Test generating an objective section."""
        conditions = ["diabetes", "hypertension"]
        
        objective = self.generator._generate_objective(conditions)
        
        # Check that the objective section is non-empty
        self.assertGreater(len(objective), 0)
        
        # Check that it contains vital signs and physical exam findings
        self.assertIn("Vital Signs:", objective)
        self.assertIn("Physical Examination:", objective)
    
    def test_generate_assessment(self):
        """Test generating an assessment section."""
        conditions = ["diabetes", "hypertension"]
        
        assessment = self.generator._generate_assessment(conditions)
        
        # Check that the assessment section is non-empty
        self.assertGreater(len(assessment), 0)
        
        # Check that it contains at least one condition
        self.assertTrue(any(condition in assessment for condition in conditions))
    
    def test_generate_plan(self):
        """Test generating a plan section."""
        conditions = ["diabetes", "hypertension"]
        medications = ["metformin", "lisinopril"]
        
        plan = self.generator._generate_plan(conditions, medications)
        
        # Check that the plan section is non-empty
        self.assertGreater(len(plan), 0)
    
    def test_generate_diagnosis_codes(self):
        """Test generating diagnosis codes."""
        conditions = ["diabetes", "hypertension", "asthma"]
        
        codes = self.generator._generate_diagnosis_codes(conditions)
        
        # Check that codes were generated
        self.assertGreater(len(codes), 0)
        
        # Check that the number of codes is at most the number of conditions
        self.assertLessEqual(len(codes), len(conditions))
        
        # Check that the codes have the expected format (letter followed by numbers and a decimal)
        for code in codes:
            self.assertRegex(code, r'^[A-Z]\d+\.\d+$')
    
    def test_generate_procedure_codes(self):
        """Test generating procedure codes."""
        procedures = ["blood test", "eye exam", "pulmonary function test"]
        
        codes = self.generator._generate_procedure_codes(procedures)
        
        # Check that codes were generated
        self.assertGreater(len(codes), 0)
        
        # Check that the number of codes is at most the number of procedures
        self.assertLessEqual(len(codes), len(procedures))
        
        # Check that the codes have the expected format (5-digit number)
        for code in codes:
            self.assertRegex(code, r'^\d{5}$')
    
    def test_save_to_json(self):
        """Test saving generated notes to a JSON file."""
        notes = self.generator.generate(self.members, count=2)
        
        # Create a temporary output path
        output_path = "test_notes.json"
        
        try:
            # Save notes to JSON
            self.generator.save_to_json(notes, output_path)
            
            # Check that the file was created
            self.assertTrue(os.path.exists(output_path))
            
            # Read the file and check its contents
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # Check that the correct number of notes were saved
            self.assertEqual(len(data), 2)
            
            # Check that the notes have the expected IDs
            self.assertEqual(data[0]["id"], notes[0].id)
            self.assertEqual(data[1]["id"], notes[1].id)
            
        finally:
            # Clean up the test file
            if os.path.exists(output_path):
                os.remove(output_path)


if __name__ == '__main__':
    unittest.main()