"""
Tests for the member processor.
"""

import json
import os
import tempfile
import unittest
from datetime import date

import pytest

from src.generators.member_generator import MemberGenerator
from src.models.member import Member, Demographics, Address, Contact, Insurance
from src.processors.member_processor import MemberProcessor
from src.utils.validation_utils import validate_member


class TestMemberProcessor(unittest.TestCase):
    """Test cases for the MemberProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'member_config': {
                'age_distribution': {
                    'min_age': 0,
                    'max_age': 100,
                    'mean_age': 45,
                    'std_dev': 20
                },
                'gender_distribution': {
                    'male': 0.48,
                    'female': 0.51,
                    'other': 0.01
                }
            },
            'insurance_config': {
                'plan_types': {
                    'HMO': 0.3,
                    'PPO': 0.4,
                    'EPO': 0.1,
                    'POS': 0.1,
                    'HDHP': 0.1
                },
                'metal_levels': {
                    'Bronze': 0.2,
                    'Silver': 0.4,
                    'Gold': 0.3,
                    'Platinum': 0.1
                }
            },
            'clinical_config': {
                'condition_count': {
                    'min': 0,
                    'max': 10,
                    'mean': 3,
                    'std_dev': 2
                }
            },
            'processor_config': {
                'enabled': True
            },
            'enrichment_config': {
                'enrich_conditions': True,
                'enrich_medications': True,
                'enrich_procedures': True,
                'add_risk_scores': True,
                'add_care_gaps': True
            }
        }
        
        # Create a member generator for test data
        self.generator = MemberGenerator(self.config, seed=42)
        
        # Create a member processor
        self.processor = MemberProcessor(self.config)
        
        # Generate some test members
        self.test_members = self.generator.generate(5)
    
    def test_process_single_member(self):
        """Test processing a single member."""
        # Process a single member
        processed_members = self.processor.process([self.test_members[0]])
        
        # Check that we got one member back
        self.assertEqual(len(processed_members), 1)
        
        # Check that the member is a Member object
        self.assertIsInstance(processed_members[0], Member)
        
        # Check that the member has the new attributes
        member = processed_members[0]
        self.assertTrue(hasattr(member, 'risk_scores'))
        self.assertTrue(hasattr(member, 'care_gaps'))
        
        # Check that the risk scores are present and valid
        self.assertIsInstance(member.risk_scores, dict)
        self.assertIn('clinical_risk', member.risk_scores)
        self.assertIn('readmission_risk', member.risk_scores)
        self.assertIn('medication_adherence', member.risk_scores)
        
        # Check that the risk scores are in the valid range (0-1)
        for score_type, score_value in member.risk_scores.items():
            self.assertGreaterEqual(score_value, 0.0)
            self.assertLessEqual(score_value, 1.0)
        
        # Check that the care gaps are present and valid
        self.assertIsInstance(member.care_gaps, list)
        
        # If there are care gaps, check their structure
        if member.care_gaps:
            for gap in member.care_gaps:
                self.assertIsInstance(gap, dict)
                self.assertIn('type', gap)
                self.assertIn('description', gap)
                self.assertIn('priority', gap)
                self.assertIn(gap['priority'], ['low', 'medium', 'high'])
    
    def test_process_multiple_members(self):
        """Test processing multiple members."""
        # Process all test members
        processed_members = self.processor.process(self.test_members)
        
        # Check that we got the expected number of members back
        self.assertEqual(len(processed_members), len(self.test_members))
        
        # Check that all members are Member objects
        for member in processed_members:
            self.assertIsInstance(member, Member)
            
            # Check that all members have the new attributes
            self.assertTrue(hasattr(member, 'risk_scores'))
            self.assertTrue(hasattr(member, 'care_gaps'))
    
    def test_member_validation_after_processing(self):
        """Test that processed members pass validation."""
        # Process all test members
        processed_members = self.processor.process(self.test_members)
        
        # Validate each processed member
        for member in processed_members:
            errors = validate_member(member)
            self.assertEqual(errors, [], f"Validation errors for member {member.id}: {errors}")
    
    def test_to_dict_serialization_after_processing(self):
        """Test that processed members can be serialized to dictionaries."""
        # Process all test members
        processed_members = self.processor.process(self.test_members)
        
        for member in processed_members:
            member_dict = member.to_dict()
            
            # Check that the dictionary has the expected keys
            self.assertIn('id', member_dict)
            self.assertIn('risk_scores', member_dict)
            self.assertIn('care_gaps', member_dict)
            
            # Check that the dictionary can be serialized to JSON
            json_str = json.dumps(member_dict)
            self.assertIsInstance(json_str, str)
    
    def test_condition_medication_consistency(self):
        """Test that conditions and medications are consistent after processing."""
        # Create a member with a medication but no corresponding condition
        member = Member(
            id="MEM00000001",
            first_name="John",
            last_name="Doe",
            demographics=Demographics(
                date_of_birth=date(1980, 1, 1),
                gender="male"
            ),
            address=Address(
                street="123 Main St",
                city="Anytown",
                state="CA",
                zip_code="12345"
            ),
            contact=Contact(
                email="john.doe@example.com",
                phone="555-123-4567"
            ),
            insurance=Insurance(
                plan_type="PPO",
                metal_level="Gold",
                member_id="INS00000001",
                coverage_start_date=date(2020, 1, 1)
            ),
            medications=["Lisinopril"]  # Hypertension medication
        )
        
        # Process the member
        processed_members = self.processor.process([member])
        processed_member = processed_members[0]
        
        # Check that the corresponding condition was added
        self.assertIn("Hypertension", processed_member.conditions)
    
    def test_age_related_enrichment(self):
        """Test that age-related enrichment works correctly."""
        # Create an elderly member
        elderly_member = Member(
            id="MEM00000002",
            first_name="Jane",
            last_name="Smith",
            demographics=Demographics(
                date_of_birth=date(1940, 1, 1),  # 85 years old
                gender="female"
            ),
            address=Address(
                street="456 Oak St",
                city="Anytown",
                state="CA",
                zip_code="12345"
            ),
            contact=Contact(
                email="jane.smith@example.com",
                phone="555-987-6543"
            ),
            insurance=Insurance(
                plan_type="Medicare",
                metal_level="Gold",
                member_id="INS00000002",
                coverage_start_date=date(2020, 1, 1)
            )
        )
        
        # Process the member
        processed_members = self.processor.process([elderly_member])
        processed_member = processed_members[0]
        
        # Check that age-appropriate conditions and procedures were added
        age_related_conditions = ["Osteoarthritis", "Hypertension", "Hyperlipidemia"]
        age_related_procedures = ["Breast Cancer Screening"]
        
        # At least one age-related condition should be present
        self.assertTrue(any(cond in processed_member.conditions for cond in age_related_conditions))
        
        # Age and gender appropriate screening should be present
        self.assertTrue(any(proc in processed_member.procedures for proc in age_related_procedures))
    
    def test_risk_score_calculation(self):
        """Test that risk scores are calculated correctly."""
        # Create members with different risk profiles
        low_risk_member = Member(
            id="MEM00000003",
            first_name="Alice",
            last_name="Johnson",
            demographics=Demographics(
                date_of_birth=date(2000, 1, 1),  # Young
                gender="female"
            ),
            address=Address(
                street="789 Pine St",
                city="Anytown",
                state="CA",
                zip_code="12345"
            ),
            contact=Contact(
                email="alice.johnson@example.com",
                phone="555-111-2222"
            ),
            insurance=Insurance(
                plan_type="PPO",
                metal_level="Bronze",
                member_id="INS00000003",
                coverage_start_date=date(2020, 1, 1)
            ),
            conditions=[]  # No conditions
        )
        
        high_risk_member = Member(
            id="MEM00000004",
            first_name="Bob",
            last_name="Williams",
            demographics=Demographics(
                date_of_birth=date(1950, 1, 1),  # Older
                gender="male"
            ),
            address=Address(
                street="101 Elm St",
                city="Anytown",
                state="CA",
                zip_code="12345"
            ),
            contact=Contact(
                email="bob.williams@example.com",
                phone="555-333-4444"
            ),
            insurance=Insurance(
                plan_type="PPO",
                metal_level="Gold",
                member_id="INS00000004",
                coverage_start_date=date(2020, 1, 1)
            ),
            conditions=["Hypertension", "Type 2 Diabetes", "Hyperlipidemia"]  # Multiple conditions
        )
        
        # Process the members
        processed_members = self.processor.process([low_risk_member, high_risk_member])
        processed_low_risk = processed_members[0]
        processed_high_risk = processed_members[1]
        
        # Check that the high risk member has higher clinical and readmission risk
        self.assertLess(
            processed_low_risk.risk_scores['clinical_risk'],
            processed_high_risk.risk_scores['clinical_risk']
        )
        self.assertLess(
            processed_low_risk.risk_scores['readmission_risk'],
            processed_high_risk.risk_scores['readmission_risk']
        )
        
        # Check that the low risk member has higher medication adherence
        self.assertGreater(
            processed_low_risk.risk_scores['medication_adherence'],
            processed_high_risk.risk_scores['medication_adherence']
        )


if __name__ == '__main__':
    unittest.main()