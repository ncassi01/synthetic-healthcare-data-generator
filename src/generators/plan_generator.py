"""
Plan Coverage generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic insurance plan coverage data.
"""

import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
import os
import sys

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from faker import Faker

from src.generators.base_generator import BaseGenerator
from src.models.insurance import PlanCoverage, BenefitCoverage, ServiceType


class PlanGenerator(BaseGenerator):
    """Generator for synthetic insurance plan coverage data."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the plan generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract plan configuration
        self.plan_config = config.get('plan_config', {})
        self.insurance_config = config.get('insurance_config', {})
        
        # Plan name prefixes and suffixes
        self.plan_prefixes = [
            "Essential", "Premium", "Select", "Choice", "Advantage", 
            "Preferred", "Elite", "Value", "Standard", "Basic",
            "Comprehensive", "Complete", "Total", "Core", "Prime"
        ]
        
        self.plan_suffixes = [
            "Plan", "Coverage", "Care", "Health", "Shield", 
            "Protect", "Secure", "Guard", "Plus", "Pro",
            "Max", "Ultra", "Premier", "Select", "Choice"
        ]
    
    def generate(self, count: int) -> List[PlanCoverage]:
        """
        Generate synthetic plan coverage data.
        
        Args:
            count: Number of plans to generate.
            
        Returns:
            List of generated PlanCoverage objects.
        """
        self.logger.info(f"Generating {count} insurance plans")
        plans = []
        
        # Get plan types and metal levels from config
        plan_types = self.insurance_config.get('plan_types', {
            "HMO": 0.3,
            "PPO": 0.4,
            "EPO": 0.1,
            "POS": 0.1,
            "HDHP": 0.1
        })
        
        metal_levels = self.insurance_config.get('metal_levels', {
            "Bronze": 0.2,
            "Silver": 0.4,
            "Gold": 0.3,
            "Platinum": 0.1
        })
        
        # Generate plans for each combination of plan type and metal level
        for plan_type in plan_types:
            for metal_level in metal_levels:
                # Generate multiple plans for each combination
                plans_per_combo = max(1, int(count * plan_types[plan_type] * metal_levels[metal_level]))
                
                for i in range(plans_per_combo):
                    plan = self._generate_plan(len(plans), plan_type, metal_level)
                    plans.append(plan)
        
        # Ensure we generate the requested number of plans
        while len(plans) < count:
            plan_type = random.choices(list(plan_types.keys()), weights=list(plan_types.values()), k=1)[0]
            metal_level = random.choices(list(metal_levels.keys()), weights=list(metal_levels.values()), k=1)[0]
            plan = self._generate_plan(len(plans), plan_type, metal_level)
            plans.append(plan)
        
        # Trim to exact count if we generated too many
        if len(plans) > count:
            plans = plans[:count]
            
        self.logger.info(f"Generated {len(plans)} insurance plans")
        return plans
    
    def _generate_plan(self, index: int, plan_type: str, metal_level: str) -> PlanCoverage:
        """
        Generate a single synthetic insurance plan.
        
        Args:
            index: Index of the plan (used for ID generation).
            plan_type: Type of plan (HMO, PPO, etc.).
            metal_level: Metal level of the plan (Bronze, Silver, etc.).
            
        Returns:
            A synthetic PlanCoverage object.
        """
        # Generate plan ID
        plan_id = f"PLN{index:08d}"
        
        # Generate plan name
        plan_prefix = random.choice(self.plan_prefixes)
        plan_suffix = random.choice(self.plan_suffixes)
        plan_name = f"{plan_prefix} {plan_type} {metal_level} {plan_suffix}"
        
        # Generate plan year
        current_year = date.today().year
        plan_year = random.randint(current_year, current_year + 1)
        
        # Generate deductible and out-of-pocket max based on metal level
        deductible_individual, deductible_family, oop_max_individual, oop_max_family = self._generate_cost_sharing(metal_level)
        
        # Generate benefit coverages for different service types
        benefit_coverages = self._generate_benefit_coverages(plan_type, metal_level)
        
        # Generate formulary tiers
        formulary_tiers = self._generate_formulary_tiers(metal_level)
        
        # Create and return plan
        return PlanCoverage(
            id=plan_id,
            plan_name=plan_name,
            plan_type=plan_type,
            metal_level=metal_level,
            year=plan_year,
            deductible_individual=deductible_individual,
            deductible_family=deductible_family,
            out_of_pocket_max_individual=oop_max_individual,
            out_of_pocket_max_family=oop_max_family,
            benefit_coverages=benefit_coverages,
            formulary_tiers=formulary_tiers
        )
    
    def _generate_cost_sharing(self, metal_level: str) -> tuple:
        """
        Generate deductible and out-of-pocket maximum based on metal level.
        
        Args:
            metal_level: Metal level of the plan (Bronze, Silver, etc.).
            
        Returns:
            Tuple of (deductible_individual, deductible_family, oop_max_individual, oop_max_family).
        """
        # Base amounts by metal level
        base_deductible = {
            "Bronze": 6000,
            "Silver": 4000,
            "Gold": 2000,
            "Platinum": 1000
        }.get(metal_level, 4000)
        
        base_oop_max = {
            "Bronze": 8000,
            "Silver": 6000,
            "Gold": 4000,
            "Platinum": 2000
        }.get(metal_level, 6000)
        
        # Add some variation
        deductible_individual = base_deductible + random.randint(-500, 500)
        oop_max_individual = base_oop_max + random.randint(-500, 500)
        
        # Ensure oop_max is greater than deductible
        if oop_max_individual <= deductible_individual:
            oop_max_individual = deductible_individual + 1000
        
        # Family amounts are typically 2x individual amounts
        deductible_family = deductible_individual * 2
        oop_max_family = oop_max_individual * 2
        
        return deductible_individual, deductible_family, oop_max_individual, oop_max_family
    
    def _generate_benefit_coverages(self, plan_type: str, metal_level: str) -> Dict[str, BenefitCoverage]:
        """
        Generate benefit coverages for different service types.
        
        Args:
            plan_type: Type of plan (HMO, PPO, etc.).
            metal_level: Metal level of the plan (Bronze, Silver, etc.).
            
        Returns:
            Dictionary of service types to BenefitCoverage objects.
        """
        benefit_coverages = {}
        
        # Define service types to generate coverages for
        service_types = [
            ServiceType.OFFICE_VISIT,
            ServiceType.PREVENTIVE_CARE,
            ServiceType.SPECIALIST_VISIT,
            ServiceType.EMERGENCY,
            ServiceType.URGENT_CARE,
            ServiceType.INPATIENT,
            ServiceType.OUTPATIENT,
            ServiceType.DIAGNOSTIC,
            ServiceType.LABORATORY,
            ServiceType.IMAGING,
            ServiceType.PHARMACY,
            ServiceType.THERAPY,
            ServiceType.MENTAL_HEALTH,
            ServiceType.DENTAL,
            ServiceType.VISION
        ]
        
        # Generate coverage for each service type
        for service_type in service_types:
            benefit_coverage = self._generate_benefit_coverage(service_type, plan_type, metal_level)
            benefit_coverages[service_type.value] = benefit_coverage
        
        return benefit_coverages
    
    def _generate_benefit_coverage(self, service_type: ServiceType, plan_type: str, metal_level: str) -> BenefitCoverage:
        """
        Generate benefit coverage for a specific service type.
        
        Args:
            service_type: Type of service.
            plan_type: Type of plan (HMO, PPO, etc.).
            metal_level: Metal level of the plan (Bronze, Silver, etc.).
            
        Returns:
            A BenefitCoverage object.
        """
        # Determine if service requires authorization
        requires_authorization = False
        if service_type in [
            ServiceType.INPATIENT, 
            ServiceType.IMAGING, 
            ServiceType.MENTAL_HEALTH,
            ServiceType.THERAPY
        ]:
            requires_authorization = random.random() < 0.8
        elif service_type in [
            ServiceType.OUTPATIENT,
            ServiceType.SPECIALIST_VISIT
        ]:
            requires_authorization = random.random() < 0.3
        
        # Determine if deductible applies
        deductible_applies = True
        if service_type == ServiceType.PREVENTIVE_CARE:
            deductible_applies = False
        elif plan_type == "HDHP":
            deductible_applies = True
        else:
            deductible_applies = random.random() < 0.7
        
        # Determine if coinsurance applies
        coinsurance_applies = True
        if service_type == ServiceType.PREVENTIVE_CARE:
            coinsurance_applies = False
        elif plan_type in ["HMO", "EPO"]:
            coinsurance_applies = random.random() < 0.5
        else:
            coinsurance_applies = random.random() < 0.8
        
        # Determine if copay applies
        copay_applies = True
        if service_type == ServiceType.PREVENTIVE_CARE:
            copay_applies = False
        elif plan_type == "HDHP":
            copay_applies = False
        elif coinsurance_applies:
            copay_applies = random.random() < 0.3  # Less likely to have both copay and coinsurance
        else:
            copay_applies = random.random() < 0.9
        
        # Generate copay amount
        copay_amount = 0.0
        if copay_applies:
            base_copay = {
                ServiceType.OFFICE_VISIT: 30,
                ServiceType.PREVENTIVE_CARE: 0,
                ServiceType.SPECIALIST_VISIT: 50,
                ServiceType.EMERGENCY: 250,
                ServiceType.URGENT_CARE: 75,
                ServiceType.INPATIENT: 500,
                ServiceType.OUTPATIENT: 250,
                ServiceType.DIAGNOSTIC: 50,
                ServiceType.LABORATORY: 25,
                ServiceType.IMAGING: 100,
                ServiceType.PHARMACY: 15,
                ServiceType.THERAPY: 40,
                ServiceType.MENTAL_HEALTH: 40,
                ServiceType.DENTAL: 50,
                ServiceType.VISION: 30
            }.get(service_type, 50)
            
            # Adjust copay based on metal level
            multiplier = {
                "Bronze": 1.5,
                "Silver": 1.0,
                "Gold": 0.7,
                "Platinum": 0.5
            }.get(metal_level, 1.0)
            
            copay_amount = round(base_copay * multiplier, 2)
        
        # Generate coinsurance rate
        coinsurance_rate = 0.0
        if coinsurance_applies:
            base_rate = {
                "Bronze": 0.4,
                "Silver": 0.3,
                "Gold": 0.2,
                "Platinum": 0.1
            }.get(metal_level, 0.3)
            
            # Add some variation
            coinsurance_rate = round(base_rate + random.uniform(-0.05, 0.05), 2)
            coinsurance_rate = max(0.05, min(0.5, coinsurance_rate))  # Ensure reasonable range
        
        # Calculate coverage percentage (inverse of coinsurance)
        coverage_percentage = round(1.0 - coinsurance_rate, 2) if coinsurance_applies else 1.0
        
        # Generate coverage limits for certain service types
        coverage_limits = None
        if service_type in [ServiceType.THERAPY, ServiceType.MENTAL_HEALTH, ServiceType.DENTAL, ServiceType.VISION]:
            coverage_limits = {
                "visits_per_year": random.randint(20, 60),
                "max_benefit": random.randint(1000, 5000) * 100
            }
        
        # Create and return benefit coverage
        return BenefitCoverage(
            service_type=service_type,
            requires_authorization=requires_authorization,
            deductible_applies=deductible_applies,
            coinsurance_applies=coinsurance_applies,
            copay_applies=copay_applies,
            copay_amount=copay_amount,
            coinsurance_rate=coinsurance_rate,
            coverage_percentage=coverage_percentage,
            coverage_limits=coverage_limits
        )
    
    def _generate_formulary_tiers(self, metal_level: str) -> Dict[str, Dict]:
        """
        Generate formulary tiers for prescription drugs.
        
        Args:
            metal_level: Metal level of the plan (Bronze, Silver, etc.).
            
        Returns:
            Dictionary of formulary tiers.
        """
        # Base copay amounts by metal level
        base_copays = {
            "Bronze": {"tier1": 20, "tier2": 50, "tier3": 100, "tier4": 250},
            "Silver": {"tier1": 15, "tier2": 40, "tier3": 80, "tier4": 200},
            "Gold": {"tier1": 10, "tier2": 30, "tier3": 60, "tier4": 150},
            "Platinum": {"tier1": 5, "tier2": 20, "tier3": 40, "tier4": 100}
        }.get(metal_level, {"tier1": 15, "tier2": 40, "tier3": 80, "tier4": 200})
        
        # Add some variation
        tier1_copay = max(0, base_copays["tier1"] + random.randint(-5, 5))
        tier2_copay = max(tier1_copay + 5, base_copays["tier2"] + random.randint(-10, 10))
        tier3_copay = max(tier2_copay + 10, base_copays["tier3"] + random.randint(-20, 20))
        tier4_copay = max(tier3_copay + 20, base_copays["tier4"] + random.randint(-50, 50))
        
        # Create formulary tiers
        formulary_tiers = {
            "tier1": {
                "name": "Preferred Generic",
                "description": "Low-cost generic medications",
                "copay": tier1_copay,
                "coinsurance": 0.0
            },
            "tier2": {
                "name": "Non-Preferred Generic",
                "description": "Higher-cost generic medications",
                "copay": tier2_copay,
                "coinsurance": 0.0
            },
            "tier3": {
                "name": "Preferred Brand",
                "description": "Brand-name medications with lower costs",
                "copay": tier3_copay,
                "coinsurance": 0.0
            },
            "tier4": {
                "name": "Non-Preferred Brand/Specialty",
                "description": "Higher-cost brand-name and specialty medications",
                "copay": tier4_copay,
                "coinsurance": 0.0
            }
        }
        
        return formulary_tiers