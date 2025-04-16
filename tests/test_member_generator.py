"""
Tests for the member generator.
"""

import json
import os
import tempfile
import unittest
from datetime import date

import pytest

from src.generators.member_generator import MemberGenerator
from src.models.member import Member
from src.utils.validation_utils import validate_member


class TestMemberGenerator(unittest.TestCase):
    """Test cases for the MemberGenerator class."""
    
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
                },
                'location': {
                    'country': 'US',
                    'state_distribution': {
                        'CA': 0.12,
                        'TX': 0.09,
                        'NY': 0.06,
                    }
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
                },
                'coverage_start_date': {
                    'min_year': 2020,
                    'max_year': 2025
                }
            },
            'clinical_config': {
                'condition_count': {
                    'min': 0,
                    'max': 10,
                    'mean': 3,
                    'std_dev': 2
                },
                'medication_count': {
                    'min': 0,
                    'max': 15,
                    'mean': 2,
                    'std_dev': 3
                },
                'procedure_count': {
                    'min': 0,
                    'max': 5,
                    'mean': 1,
                    'std_dev': 1
                }
            }
        }
        self.generator = MemberGenerator(self.config, seed=42)
    
    def test_generate_single_member(self):
        """Test generating a single member."""
        members = self.generator.generate(1)
        
        # Check that we got one member
        self.assertEqual(len(members), 1)
        
        # Check that the member is a Member object
        self.assertIsInstance(members[0], Member)
        
        # Check that the member has the expected attributes
        member = members[0]
        self.assertTrue(member.id.startswith('MEM'))
        self.assertIsNotNone(member.first_name)
        self.assertIsNotNone(member.last_name)
        self.assertIsInstance(member.demographics.date_of_birth, date)
        self.assertIn(member.demographics.gender, ['male', 'female', 'other'])
        self.assertIsNotNone(member.address.street)
        self.assertIsNotNone(member.address.city)
        self.assertIsNotNone(member.address.state)
        self.assertIsNotNone(member.address.zip_code)
        self.assertIsNotNone(member.contact.email)
        self.assertIsNotNone(member.contact.phone)
        self.assertIsNotNone(member.insurance.plan_type)
        self.assertIsNotNone(member.insurance.metal_level)
        self.assertIsNotNone(member.insurance.member_id)
        self.assertIsInstance(member.insurance.coverage_start_date, date)
    
    def test_generate_multiple_members(self):
        """Test generating multiple members."""
        count = 10
        members = self.generator.generate(count)
        
        # Check that we got the expected number of members
        self.assertEqual(len(members), count)
        
        # Check that all members are Member objects
        for member in members:
            self.assertIsInstance(member, Member)
        
        # Check that all members have unique IDs
        member_ids = [member.id for member in members]
        self.assertEqual(len(member_ids), len(set(member_ids)))
    
    def test_member_validation(self):
        """Test that generated members pass validation."""
        members = self.generator.generate(5)
        
        for member in members:
            errors = validate_member(member)
            self.assertEqual(errors, [], f"Validation errors for member {member.id}: {errors}")
    
    def test_to_dict_serialization(self):
        """Test that members can be serialized to dictionaries."""
        members = self.generator.generate(3)
        
        for member in members:
            member_dict = member.to_dict()
            
            # Check that the dictionary has the expected keys
            self.assertIn('id', member_dict)
            self.assertIn('first_name', member_dict)
            self.assertIn('last_name', member_dict)
            self.assertIn('demographics', member_dict)
            self.assertIn('address', member_dict)
            self.assertIn('contact', member_dict)
            self.assertIn('insurance', member_dict)
            
            # Check that the dictionary can be serialized to JSON
            json_str = json.dumps(member_dict)
            self.assertIsInstance(json_str, str)
    
    def test_save_to_json(self):
        """Test saving members to a JSON file."""
        members = self.generator.generate(5)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save members to JSON
            self.generator.save_to_json(members, temp_path)
            
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check that the file contains valid JSON
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            # Check that we got the expected number of members
            self.assertEqual(len(data), 5)
            
            # Check that the data has the expected structure
            for item in data:
                self.assertIn('id', item)
                self.assertIn('first_name', item)
                self.assertIn('last_name', item)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == '__main__':
    unittest.main()