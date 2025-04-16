"""
Tests for the claim generator.

This module contains tests for the claim generator functionality.
"""

import os
import sys
import unittest
from datetime import date, timedelta

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generators.claim_generator import ClaimGenerator
from src.models.insurance import Claim, ClaimStatus, ServiceType


class TestClaimGenerator(unittest.TestCase):
    """Test case for the ClaimGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'claim_config': {
                'status_distribution': {
                    'submitted': 0.05,
                    'pending': 0.1,
                    'in_process': 0.1,
                    'denied': 0.1,
                    'partially_paid': 0.15,
                    'paid': 0.45,
                    'appealed': 0.05
                }
            },
            'service_config': {
                'service_line_count': {
                    'min': 1,
                    'max': 5,
                    'mean': 2,
                    'std_dev': 1
                }
            }
        }
        
        self.members = [
            {
                'id': 'MEM00000001',
                'first_name': 'John',
                'last_name': 'Doe',
                'demographics': {
                    'date_of_birth': '1980-01-01',
                    'gender': 'male'
                },
                'insurance': {
                    'plan_type': 'PPO',
                    'metal_level': 'Gold'
                }
            },
            {
                'id': 'MEM00000002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'demographics': {
                    'date_of_birth': '1985-05-15',
                    'gender': 'female'
                },
                'insurance': {
                    'plan_type': 'HMO',
                    'metal_level': 'Silver'
                }
            }
        ]
        
        self.generator = ClaimGenerator(self.config, seed=42)
    
    def test_generate_claims(self):
        """Test generating claims."""
        # Generate claims
        claims = self.generator.generate(10, self.members)
        
        # Check that we got the expected number of claims
        self.assertEqual(len(claims), 10)
        
        # Check that all claims are of the correct type
        for claim in claims:
            self.assertIsInstance(claim, Claim)
            
            # Check that the claim has a valid ID
            self.assertTrue(claim.id.startswith('CLM'))
            
            # Check that the claim has a valid member ID
            self.assertTrue(claim.member_id in ['MEM00000001', 'MEM00000002'])
            
            # Check that the claim has a valid provider ID
            self.assertTrue(claim.provider_id.startswith('PRV'))
            
            # Check that the claim has valid dates
            self.assertIsInstance(claim.date_of_service, date)
            self.assertIsInstance(claim.date_submitted, date)
            self.assertTrue(claim.date_submitted >= claim.date_of_service)
            
            # Check that the claim has a valid status
            self.assertIn(claim.status, list(ClaimStatus))
            
            # Check that the claim has a valid total billed amount
            self.assertGreater(claim.total_billed, 0)
            
            # Check that the claim has at least one service line
            self.assertGreater(len(claim.service_lines), 0)
            
            # Check that the claim has valid diagnosis codes
            self.assertGreater(len(claim.diagnosis_codes), 0)
            
            # Check financial consistency based on status
            if claim.status == ClaimStatus.PAID:
                self.assertGreater(claim.insurance_paid, 0)
                self.assertEqual(claim.total_billed, claim.insurance_paid + claim.patient_responsibility)
                self.assertIsNotNone(claim.date_processed)
            
            elif claim.status == ClaimStatus.PARTIALLY_PAID:
                self.assertGreater(claim.insurance_paid, 0)
                self.assertLess(claim.insurance_paid, claim.total_billed)
                self.assertEqual(claim.total_billed, claim.insurance_paid + claim.patient_responsibility)
                self.assertIsNotNone(claim.date_processed)
            
            elif claim.status == ClaimStatus.DENIED:
                self.assertEqual(claim.insurance_paid, 0)
                self.assertEqual(claim.patient_responsibility, claim.total_billed)
                self.assertIsNotNone(claim.date_processed)
                self.assertIsNotNone(claim.denial_reason)
    
    def test_generate_service_line(self):
        """Test generating a service line."""
        # Generate a service line
        service_line = self.generator._generate_service_line('medical')
        
        # Check that the service line has a valid service code
        self.assertIsNotNone(service_line.service_code)
        
        # Check that the service line has a valid description
        self.assertIsNotNone(service_line.description)
        
        # Check that the service line has a valid service type
        self.assertIn(service_line.service_type, list(ServiceType))
        
        # Check that the service line has a valid quantity
        self.assertGreater(service_line.quantity, 0)
        
        # Check that the service line has a valid unit price
        self.assertGreater(service_line.unit_price, 0)
        
        # Check that the service line has a valid total price
        self.assertEqual(service_line.total_price, service_line.unit_price * service_line.quantity)
    
    def test_to_dict(self):
        """Test converting a claim to a dictionary."""
        # Generate a claim
        claims = self.generator.generate(1, self.members)
        claim = claims[0]
        
        # Convert to dictionary
        claim_dict = claim.to_dict()
        
        # Check that the dictionary has the expected keys
        expected_keys = [
            'id', 'member_id', 'provider_id', 'date_of_service', 'date_submitted',
            'status', 'total_billed', 'service_lines', 'diagnosis_codes',
            'place_of_service', 'claim_type', 'insurance_paid', 'patient_responsibility'
        ]
        
        for key in expected_keys:
            self.assertIn(key, claim_dict)
        
        # Check that the service lines are also dictionaries
        self.assertIsInstance(claim_dict['service_lines'], list)
        if claim_dict['service_lines']:
            self.assertIsInstance(claim_dict['service_lines'][0], dict)


if __name__ == '__main__':
    unittest.main()