"""
Risk Assessment Generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic risk assessments,
which evaluate various types of risks for members, including clinical,
financial, and care management risks.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from src.utils.file_utils import load_config


class RiskAssessment:
    """
    Represents a comprehensive risk assessment for a member.
    
    A risk assessment typically includes:
    - Clinical risk factors and scores
    - Financial risk factors and scores
    - Care management risk factors and scores
    - Overall risk scores and stratification
    - Risk trends over time
    - Recommended interventions based on risk
    """
    
    def __init__(self, member_id: str, assessment_date: datetime):
        """
        Initialize a risk assessment.
        
        Args:
            member_id: ID of the member associated with this assessment
            assessment_date: Date of the assessment
        """
        self.id = f"RA{uuid.uuid4().hex[:8].upper()}"
        self.member_id = member_id
        self.assessment_date = assessment_date
        self.clinical_risk = {}
        self.financial_risk = {}
        self.care_management_risk = {}
        self.overall_risk = {}
        self.risk_trends = []
        self.recommended_interventions = []
        
    def set_clinical_risk(self, score: float, level: str, factors: List[Dict[str, Any]]) -> None:
        """
        Set the clinical risk assessment.
        
        Args:
            score: Numeric risk score (typically 0-100)
            level: Risk level (low, moderate, high)
            factors: List of risk factors contributing to the score
        """
        self.clinical_risk = {
            "score": score,
            "level": level,
            "factors": factors
        }
        
    def set_financial_risk(self, score: float, level: str, factors: List[Dict[str, Any]]) -> None:
        """
        Set the financial risk assessment.
        
        Args:
            score: Numeric risk score (typically 0-100)
            level: Risk level (low, moderate, high)
            factors: List of risk factors contributing to the score
        """
        self.financial_risk = {
            "score": score,
            "level": level,
            "factors": factors
        }
        
    def set_care_management_risk(self, score: float, level: str, factors: List[Dict[str, Any]]) -> None:
        """
        Set the care management risk assessment.
        
        Args:
            score: Numeric risk score (typically 0-100)
            level: Risk level (low, moderate, high)
            factors: List of risk factors contributing to the score
        """
        self.care_management_risk = {
            "score": score,
            "level": level,
            "factors": factors
        }
        
    def calculate_overall_risk(self) -> None:
        """
        Calculate the overall risk based on clinical, financial, and care management risks.
        """
        # Ensure all risk components are present
        if not (self.clinical_risk and self.financial_risk and self.care_management_risk):
            return
        
        # Calculate weighted average of risk scores
        clinical_weight = 0.5
        financial_weight = 0.2
        care_management_weight = 0.3
        
        overall_score = (
            self.clinical_risk.get("score", 0) * clinical_weight +
            self.financial_risk.get("score", 0) * financial_weight +
            self.care_management_risk.get("score", 0) * care_management_weight
        )
        
        # Determine overall risk level
        if overall_score >= 70:
            overall_level = "high"
        elif overall_score >= 40:
            overall_level = "moderate"
        else:
            overall_level = "low"
        
        # Set overall risk
        self.overall_risk = {
            "score": overall_score,
            "level": overall_level,
            "stratification": self._get_stratification(overall_score),
            "weights": {
                "clinical": clinical_weight,
                "financial": financial_weight,
                "care_management": care_management_weight
            }
        }
        
    def add_risk_trend(self, date: datetime, score: float, level: str) -> None:
        """
        Add a historical risk trend point.
        
        Args:
            date: Date of the historical assessment
            score: Overall risk score at that date
            level: Risk level at that date
        """
        self.risk_trends.append({
            "date": date.isoformat(),
            "score": score,
            "level": level
        })
        
    def add_recommended_intervention(self, category: str, description: str, priority: str) -> None:
        """
        Add a recommended intervention based on the risk assessment.
        
        Args:
            category: Category of the intervention
            description: Description of the intervention
            priority: Priority of the intervention (high, medium, low)
        """
        self.recommended_interventions.append({
            "category": category,
            "description": description,
            "priority": priority,
            "status": "recommended",
            "date_recommended": self.assessment_date.isoformat()
        })
        
    def _get_stratification(self, score: float) -> str:
        """
        Get the risk stratification tier based on the overall score.
        
        Args:
            score: Overall risk score
            
        Returns:
            Risk stratification tier
        """
        if score >= 85:
            return "tier_1"  # Highest risk
        elif score >= 70:
            return "tier_2"
        elif score >= 55:
            return "tier_3"
        elif score >= 40:
            return "tier_4"
        elif score >= 25:
            return "tier_5"
        else:
            return "tier_6"  # Lowest risk
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the risk assessment to a dictionary.
        
        Returns:
            Dictionary representation of the risk assessment
        """
        # Calculate overall risk if not already done
        if not self.overall_risk:
            self.calculate_overall_risk()
            
        return {
            "id": self.id,
            "member_id": self.member_id,
            "assessment_date": self.assessment_date.isoformat(),
            "clinical_risk": self.clinical_risk,
            "financial_risk": self.financial_risk,
            "care_management_risk": self.care_management_risk,
            "overall_risk": self.overall_risk,
            "risk_trends": self.risk_trends,
            "recommended_interventions": self.recommended_interventions
        }


class RiskAssessmentGenerator:
    """
    Generator for synthetic risk assessments.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the risk assessment generator.
        
        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config
        self.risk_config = config.get("risk_assessment_config", {})
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load reference data
        self.clinical_risk_factors = self.risk_config.get("clinical_risk_factors", [
            "chronic_conditions",
            "medication_adherence",
            "hospital_admissions",
            "emergency_visits",
            "comorbidities",
            "functional_status",
            "age_related_risks",
            "preventive_care_gaps"
        ])
        
        self.financial_risk_factors = self.risk_config.get("financial_risk_factors", [
            "high_cost_claims",
            "out_of_network_usage",
            "premium_payment_history",
            "benefit_utilization",
            "cost_sharing_burden",
            "pharmacy_costs",
            "specialist_utilization",
            "procedure_costs"
        ])
        
        self.care_management_risk_factors = self.risk_config.get("care_management_risk_factors", [
            "care_coordination_needs",
            "social_determinants",
            "behavioral_health_needs",
            "caregiver_support",
            "health_literacy",
            "self_management_ability",
            "engagement_level",
            "care_plan_adherence"
        ])
        
        self.intervention_categories = self.risk_config.get("intervention_categories", [
            "care_coordination",
            "disease_management",
            "medication_management",
            "behavioral_health",
            "social_support",
            "preventive_care",
            "self_management",
            "specialty_care"
        ])
        
    def generate(self, count: int, members: List[Dict[str, Any]]) -> List[RiskAssessment]:
        """
        Generate synthetic risk assessments.
        
        Args:
            count: Number of risk assessments to generate
            members: List of member dictionaries to associate assessments with
            
        Returns:
            List of generated RiskAssessment objects
        """
        assessments = []
        
        # Ensure we have members to work with
        if not members:
            return assessments
        
        # Generate risk assessments
        for _ in range(count):
            # Select a random member
            member = random.choice(members)
            member_id = member.get("id")
            
            # Determine assessment date
            assessment_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            # Create the risk assessment
            assessment = RiskAssessment(member_id, assessment_date)
            
            # Set clinical risk
            clinical_score = random.uniform(0, 100)
            clinical_level = self._get_risk_level(clinical_score)
            clinical_factors = self._generate_risk_factors(self.clinical_risk_factors, 3, 5)
            assessment.set_clinical_risk(clinical_score, clinical_level, clinical_factors)
            
            # Set financial risk
            financial_score = random.uniform(0, 100)
            financial_level = self._get_risk_level(financial_score)
            financial_factors = self._generate_risk_factors(self.financial_risk_factors, 2, 4)
            assessment.set_financial_risk(financial_score, financial_level, financial_factors)
            
            # Set care management risk
            care_score = random.uniform(0, 100)
            care_level = self._get_risk_level(care_score)
            care_factors = self._generate_risk_factors(self.care_management_risk_factors, 2, 5)
            assessment.set_care_management_risk(care_score, care_level, care_factors)
            
            # Calculate overall risk
            assessment.calculate_overall_risk()
            
            # Add risk trends (historical data points)
            trend_count = random.randint(3, 6)
            for i in range(trend_count):
                trend_date = assessment_date - timedelta(days=(i + 1) * 30)  # Monthly trend points
                trend_score = random.uniform(0, 100)
                trend_level = self._get_risk_level(trend_score)
                assessment.add_risk_trend(trend_date, trend_score, trend_level)
            
            # Add recommended interventions
            intervention_count = random.randint(2, 5)
            for _ in range(intervention_count):
                category = random.choice(self.intervention_categories)
                description = self._generate_intervention_description(category)
                priority = random.choice(["high", "medium", "low"])
                assessment.add_recommended_intervention(category, description, priority)
            
            assessments.append(assessment)
        
        return assessments
    
    def _get_risk_level(self, score: float) -> str:
        """
        Get the risk level based on a score.
        
        Args:
            score: Risk score
            
        Returns:
            Risk level (low, moderate, high)
        """
        if score >= 70:
            return "high"
        elif score >= 40:
            return "moderate"
        else:
            return "low"
    
    def _generate_risk_factors(self, factor_types: List[str], min_count: int, max_count: int) -> List[Dict[str, Any]]:
        """
        Generate a list of risk factors.
        
        Args:
            factor_types: List of factor types to choose from
            min_count: Minimum number of factors to generate
            max_count: Maximum number of factors to generate
            
        Returns:
            List of risk factors
        """
        factors = []
        
        # Determine how many factors to generate
        count = random.randint(min_count, max_count)
        
        # Select random factor types
        selected_types = random.sample(factor_types, min(count, len(factor_types)))
        
        # Generate factors
        for factor_type in selected_types:
            factor = {
                "type": factor_type,
                "description": self._generate_factor_description(factor_type),
                "impact": random.choice(["low", "moderate", "high"]),
                "modifiable": random.choice([True, False])
            }
            factors.append(factor)
        
        return factors
    
    def _generate_factor_description(self, factor_type: str) -> str:
        """
        Generate a description for a risk factor.
        
        Args:
            factor_type: Type of risk factor
            
        Returns:
            Description of the risk factor
        """
        factor_descriptions = {
            # Clinical risk factors
            "chronic_conditions": [
                "Multiple chronic conditions requiring complex management",
                "Poorly controlled diabetes with HbA1c > 9.0",
                "Heart failure with recent exacerbation",
                "COPD with frequent exacerbations",
                "Chronic kidney disease stage 3 or higher"
            ],
            "medication_adherence": [
                "Poor adherence to prescribed medications",
                "Multiple medication changes in past 3 months",
                "Complex medication regimen with > 10 medications",
                "History of adverse drug reactions",
                "Difficulty affording medications"
            ],
            "hospital_admissions": [
                "Multiple hospital admissions in past 6 months",
                "Recent 30-day readmission",
                "Extended hospital stay > 7 days",
                "Frequent observation stays",
                "Multiple admissions for same condition"
            ],
            "emergency_visits": [
                "Multiple ED visits in past 6 months",
                "ED visits for conditions manageable in primary care",
                "After-hours ED utilization",
                "ED visits resulting in admission",
                "ED visits for pain management"
            ],
            "comorbidities": [
                "Multiple comorbidities affecting treatment",
                "Behavioral health and physical health comorbidities",
                "Comorbidities with conflicting treatment recommendations",
                "Rare disease comorbidity requiring specialist care",
                "Comorbidities affecting medication selection"
            ],
            "functional_status": [
                "Declining functional status",
                "Requires assistance with ADLs",
                "Recent falls",
                "Mobility limitations",
                "Cognitive impairment"
            ],
            "age_related_risks": [
                "Advanced age with frailty",
                "Age-related medication risks",
                "Age-appropriate screenings not completed",
                "Age-related cognitive changes",
                "Geriatric syndromes present"
            ],
            "preventive_care_gaps": [
                "Multiple preventive care gaps",
                "Overdue for cancer screenings",
                "Immunization gaps",
                "No recent wellness visit",
                "Chronic disease monitoring gaps"
            ],
            
            # Financial risk factors
            "high_cost_claims": [
                "Recent high-cost claim > $50,000",
                "Projected high-cost procedures planned",
                "Specialty medication costs",
                "Multiple high-cost imaging studies",
                "Transplant evaluation or recent transplant"
            ],
            "out_of_network_usage": [
                "Frequent out-of-network utilization",
                "Out-of-network emergency services",
                "Specialty care sought outside network",
                "Out-of-network lab or imaging services",
                "Travel-related out-of-network care"
            ],
            "premium_payment_history": [
                "History of premium payment delays",
                "Recent request for premium assistance",
                "Premium payment grace period utilization",
                "Risk of coverage lapse due to payment issues",
                "Payment plan arrangement in place"
            ],
            "benefit_utilization": [
                "High utilization of covered benefits",
                "Approaching benefit maximums",
                "Frequent service authorization requests",
                "Multiple benefit exceptions requested",
                "Unusual benefit utilization patterns"
            ],
            "cost_sharing_burden": [
                "High deductible plan with limited resources",
                "Accumulated significant out-of-pocket costs",
                "Cost-sharing burden > 5% of income",
                "Requests for financial assistance",
                "Deferred care due to cost concerns"
            ],
            "pharmacy_costs": [
                "High monthly pharmacy costs",
                "Specialty medication requirements",
                "Multiple brand-name medications",
                "Limited generic substitution options",
                "Compound medication requirements"
            ],
            "specialist_utilization": [
                "Multiple specialists involved in care",
                "Frequent specialist visits",
                "Specialist-to-specialist referrals",
                "Duplicative specialist services",
                "Specialist care coordination challenges"
            ],
            "procedure_costs": [
                "Planned high-cost procedures",
                "Multiple procedures scheduled",
                "Repeated procedures for same condition",
                "Experimental or investigational procedures",
                "Complex procedure with extended recovery"
            ],
            
            # Care management risk factors
            "care_coordination_needs": [
                "Multiple providers requiring coordination",
                "Transitions of care challenges",
                "Complex care plan with multiple components",
                "Fragmented care across systems",
                "Lack of designated care coordinator"
            ],
            "social_determinants": [
                "Housing instability affecting care",
                "Transportation barriers to appointments",
                "Food insecurity impacting health",
                "Limited social support network",
                "Financial barriers to care adherence"
            ],
            "behavioral_health_needs": [
                "Untreated or undertreated mental health condition",
                "Substance use disorder affecting care",
                "Behavioral health and physical health integration needs",
                "Limited access to behavioral health services",
                "Medication adherence affected by behavioral health"
            ],
            "caregiver_support": [
                "Limited or no caregiver support",
                "Caregiver strain or burnout",
                "Caregiver health issues",
                "Complex care needs exceeding caregiver capacity",
                "Caregiver knowledge gaps"
            ],
            "health_literacy": [
                "Limited health literacy affecting self-care",
                "Difficulty understanding treatment instructions",
                "Language barriers to care",
                "Limited digital literacy for telehealth",
                "Complex care regimen with limited understanding"
            ],
            "self_management_ability": [
                "Limited self-management skills",
                "Difficulty monitoring health conditions",
                "Challenges with medication self-administration",
                "Limited problem-solving abilities for symptoms",
                "Inability to recognize warning signs"
            ],
            "engagement_level": [
                "Low engagement in care planning",
                "Missed appointments",
                "Limited response to outreach attempts",
                "Passive participation in treatment decisions",
                "Resistance to recommended interventions"
            ],
            "care_plan_adherence": [
                "Poor adherence to care plan recommendations",
                "Selective adherence to components of care plan",
                "Difficulty implementing lifestyle recommendations",
                "Inconsistent follow-through with referrals",
                "Limited understanding of care plan importance"
            ]
        }
        
        # Return a random description from the factor type
        return random.choice(factor_descriptions.get(factor_type, ["Risk factor not specified"]))
    
    def _generate_intervention_description(self, category: str) -> str:
        """
        Generate a description for an intervention.
        
        Args:
            category: Category of intervention
            
        Returns:
            Description of the intervention
        """
        intervention_descriptions = {
            "care_coordination": [
                "Assign dedicated care manager",
                "Implement cross-provider care coordination",
                "Schedule care coordination conference",
                "Develop comprehensive care coordination plan",
                "Establish communication protocol across providers"
            ],
            "disease_management": [
                "Enroll in diabetes management program",
                "Implement heart failure monitoring protocol",
                "Provide COPD action plan",
                "Establish chronic pain management strategy",
                "Develop personalized disease management goals"
            ],
            "medication_management": [
                "Conduct comprehensive medication review",
                "Implement medication adherence program",
                "Simplify medication regimen",
                "Provide medication management tools",
                "Schedule pharmacist consultation"
            ],
            "behavioral_health": [
                "Refer to behavioral health services",
                "Screen for depression and anxiety",
                "Implement integrated behavioral health support",
                "Provide substance use disorder resources",
                "Establish behavioral health follow-up protocol"
            ],
            "social_support": [
                "Connect with community support resources",
                "Refer to social work services",
                "Provide transportation assistance",
                "Connect with food security resources",
                "Arrange for home support services"
            ],
            "preventive_care": [
                "Schedule overdue preventive screenings",
                "Provide immunization catch-up plan",
                "Implement preventive care reminder system",
                "Conduct health risk assessment",
                "Develop personalized prevention plan"
            ],
            "self_management": [
                "Provide condition-specific education",
                "Implement teach-back method for instructions",
                "Provide self-monitoring tools and education",
                "Connect with peer support program",
                "Develop personalized self-management goals"
            ],
            "specialty_care": [
                "Expedite specialist referral",
                "Coordinate multiple specialty appointments",
                "Arrange for specialist care manager",
                "Implement specialist care plan integration",
                "Provide specialist pre-visit preparation"
            ]
        }
        
        # Return a random description from the category
        return random.choice(intervention_descriptions.get(category, ["Intervention not specified"]))