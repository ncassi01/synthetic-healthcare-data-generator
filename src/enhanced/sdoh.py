"""
Social Determinants of Health (SDOH) Assessment Generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic SDOH assessments,
which capture various social and environmental factors that affect health outcomes.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from src.utils.file_utils import load_config


class SDOHAssessment:
    """
    Represents a Social Determinants of Health (SDOH) assessment.
    
    An SDOH assessment typically includes:
    - Economic stability (employment, income, expenses, debt, medical bills)
    - Education access and quality
    - Healthcare access and quality
    - Neighborhood and built environment
    - Social and community context
    - Food security
    - Transportation access
    - Housing stability
    """
    
    def __init__(self, member_id: str, assessment_date: datetime, provider_id: Optional[str] = None):
        """
        Initialize an SDOH assessment.
        
        Args:
            member_id: ID of the member associated with this assessment
            assessment_date: Date of the assessment
            provider_id: ID of the provider who conducted the assessment (optional)
        """
        self.id = f"SDOH{uuid.uuid4().hex[:8].upper()}"
        self.member_id = member_id
        self.assessment_date = assessment_date
        self.provider_id = provider_id
        self.domains = {}
        self.risk_factors = []
        self.interventions = []
        self.referrals = []
        self.overall_risk_level = None
        
    def add_domain_assessment(self, domain: str, score: int, notes: Optional[str] = None) -> None:
        """
        Add an assessment for a specific SDOH domain.
        
        Args:
            domain: SDOH domain (e.g., "economic_stability", "education", etc.)
            score: Numeric score for the domain (typically 0-5, where higher is better)
            notes: Optional notes about the domain assessment
        """
        self.domains[domain] = {
            "score": score,
            "notes": notes
        }
        
    def add_risk_factor(self, category: str, description: str, severity: str) -> None:
        """
        Add a risk factor identified in the assessment.
        
        Args:
            category: Category of the risk factor
            description: Description of the risk factor
            severity: Severity of the risk factor (low, moderate, high)
        """
        self.risk_factors.append({
            "category": category,
            "description": description,
            "severity": severity
        })
        
    def add_intervention(self, type: str, description: str, status: str) -> None:
        """
        Add an intervention recommended based on the assessment.
        
        Args:
            type: Type of intervention
            description: Description of the intervention
            status: Status of the intervention (recommended, in-progress, completed)
        """
        self.interventions.append({
            "type": type,
            "description": description,
            "status": status,
            "date_recommended": self.assessment_date.isoformat()
        })
        
    def add_referral(self, service_type: str, organization: str, status: str) -> None:
        """
        Add a referral to a community resource or service.
        
        Args:
            service_type: Type of service
            organization: Organization providing the service
            status: Status of the referral (pending, completed, declined)
        """
        self.referrals.append({
            "service_type": service_type,
            "organization": organization,
            "status": status,
            "date_referred": self.assessment_date.isoformat()
        })
        
    def calculate_overall_risk(self) -> None:
        """
        Calculate the overall SDOH risk level based on domain scores.
        """
        if not self.domains:
            self.overall_risk_level = "unknown"
            return
        
        # Calculate average score across all domains
        avg_score = sum(domain["score"] for domain in self.domains.values()) / len(self.domains)
        
        # Determine risk level based on average score
        if avg_score >= 4:
            self.overall_risk_level = "low"
        elif avg_score >= 2.5:
            self.overall_risk_level = "moderate"
        else:
            self.overall_risk_level = "high"
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the SDOH assessment to a dictionary.
        
        Returns:
            Dictionary representation of the SDOH assessment
        """
        # Calculate overall risk if not already done
        if self.overall_risk_level is None:
            self.calculate_overall_risk()
            
        return {
            "id": self.id,
            "member_id": self.member_id,
            "assessment_date": self.assessment_date.isoformat(),
            "provider_id": self.provider_id,
            "domains": self.domains,
            "risk_factors": self.risk_factors,
            "interventions": self.interventions,
            "referrals": self.referrals,
            "overall_risk_level": self.overall_risk_level
        }


class SDOHAssessmentGenerator:
    """
    Generator for synthetic SDOH assessments.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the SDOH assessment generator.
        
        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config
        self.sdoh_config = config.get("sdoh_config", {})
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load reference data
        self.sdoh_domains = self.sdoh_config.get("domains", [
            "economic_stability",
            "education",
            "healthcare_access",
            "neighborhood",
            "social_context",
            "food_security",
            "transportation",
            "housing"
        ])
        
        self.risk_factor_categories = self.sdoh_config.get("risk_factor_categories", [
            "financial",
            "educational",
            "healthcare",
            "environmental",
            "social",
            "nutritional",
            "mobility",
            "housing"
        ])
        
        self.intervention_types = self.sdoh_config.get("intervention_types", [
            "financial_assistance",
            "education_resources",
            "healthcare_navigation",
            "community_resources",
            "social_support",
            "food_assistance",
            "transportation_assistance",
            "housing_assistance"
        ])
        
        self.referral_services = self.sdoh_config.get("referral_services", [
            "food_bank",
            "housing_assistance",
            "job_training",
            "educational_program",
            "healthcare_navigation",
            "transportation_service",
            "financial_counseling",
            "social_services"
        ])
        
        self.referral_organizations = self.sdoh_config.get("referral_organizations", [
            "Community Action Agency",
            "United Way",
            "Salvation Army",
            "Local Food Bank",
            "Housing Authority",
            "Workforce Development",
            "Adult Education Center",
            "Community Health Center"
        ])
        
    def generate(self, count: int, members: List[Dict[str, Any]]) -> List[SDOHAssessment]:
        """
        Generate synthetic SDOH assessments.
        
        Args:
            count: Number of SDOH assessments to generate
            members: List of member dictionaries to associate assessments with
            
        Returns:
            List of generated SDOHAssessment objects
        """
        assessments = []
        
        # Ensure we have members to work with
        if not members:
            return assessments
        
        # Generate SDOH assessments
        for _ in range(count):
            # Select a random member
            member = random.choice(members)
            member_id = member.get("id")
            
            # Determine assessment date
            assessment_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            # Create the SDOH assessment
            assessment = SDOHAssessment(member_id, assessment_date, f"PRV{random.randint(10000, 99999)}")
            
            # Add domain assessments
            for domain in self.sdoh_domains:
                # Generate a score (0-5, where higher is better)
                score = random.randint(0, 5)
                
                # Generate notes based on the score
                notes = self._generate_domain_notes(domain, score)
                
                # Add the domain assessment
                assessment.add_domain_assessment(domain, score, notes)
            
            # Add risk factors
            risk_factor_count = random.randint(0, 5)
            for _ in range(risk_factor_count):
                category = random.choice(self.risk_factor_categories)
                description = self._generate_risk_factor_description(category)
                severity = random.choice(["low", "moderate", "high"])
                
                assessment.add_risk_factor(category, description, severity)
            
            # Add interventions
            intervention_count = random.randint(0, 3)
            for _ in range(intervention_count):
                type = random.choice(self.intervention_types)
                description = self._generate_intervention_description(type)
                status = random.choice(["recommended", "in-progress", "completed"])
                
                assessment.add_intervention(type, description, status)
            
            # Add referrals
            referral_count = random.randint(0, 2)
            for _ in range(referral_count):
                service_type = random.choice(self.referral_services)
                organization = random.choice(self.referral_organizations)
                status = random.choice(["pending", "completed", "declined"])
                
                assessment.add_referral(service_type, organization, status)
            
            # Calculate overall risk
            assessment.calculate_overall_risk()
            
            assessments.append(assessment)
        
        return assessments
    
    def _generate_domain_notes(self, domain: str, score: int) -> str:
        """
        Generate notes for a domain assessment based on the score.
        
        Args:
            domain: SDOH domain
            score: Numeric score for the domain
            
        Returns:
            Notes for the domain assessment
        """
        # Define note templates for each domain and score range
        domain_notes = {
            "economic_stability": {
                "low": "Patient reports significant financial hardship. Unemployed or underemployed. Difficulty paying for basic needs.",
                "medium": "Patient has some financial concerns. Employment is stable but income is limited. Occasionally struggles with expenses.",
                "high": "Patient reports stable financial situation. Employed with adequate income. No significant financial concerns."
            },
            "education": {
                "low": "Limited education. Did not complete high school. Limited health literacy.",
                "medium": "Completed high school. Some post-secondary education. Moderate health literacy.",
                "high": "College educated. Good health literacy. No educational barriers identified."
            },
            "healthcare_access": {
                "low": "Significant barriers to healthcare access. Uninsured or underinsured. Difficulty accessing providers.",
                "medium": "Some barriers to healthcare access. Insurance coverage with high out-of-pocket costs. Limited provider options.",
                "high": "Good healthcare access. Comprehensive insurance coverage. Regular access to providers."
            },
            "neighborhood": {
                "low": "Unsafe neighborhood. Limited access to resources. Environmental concerns (pollution, etc.).",
                "medium": "Moderately safe neighborhood. Some access to resources. Minor environmental concerns.",
                "high": "Safe neighborhood. Good access to resources. No significant environmental concerns."
            },
            "social_context": {
                "low": "Limited social support. Social isolation. Limited community engagement.",
                "medium": "Some social support. Moderate community engagement. Some social connections.",
                "high": "Strong social support network. Active community engagement. Numerous social connections."
            },
            "food_security": {
                "low": "Food insecurity. Limited access to nutritious food. May skip meals due to financial constraints.",
                "medium": "Occasional food insecurity. Access to food but may lack nutritious options. Budget constraints affect food choices.",
                "high": "Food secure. Regular access to nutritious food. No significant concerns about food access."
            },
            "transportation": {
                "low": "No reliable transportation. Difficulty attending appointments. Limited mobility.",
                "medium": "Some transportation challenges. Relies on public transportation or others for rides. Occasional missed appointments.",
                "high": "Reliable transportation. No significant barriers to attending appointments or accessing services."
            },
            "housing": {
                "low": "Unstable housing. Homelessness or at risk of homelessness. Unsafe or inadequate housing conditions.",
                "medium": "Housing is stable but may have some concerns (cost burden, maintenance issues, etc.).",
                "high": "Stable, safe housing. No significant housing concerns identified."
            }
        }
        
        # Determine score range
        if score <= 1:
            range_key = "low"
        elif score <= 3:
            range_key = "medium"
        else:
            range_key = "high"
        
        # Return the appropriate note
        return domain_notes.get(domain, {}).get(range_key, f"Score: {score}/5")
    
    def _generate_risk_factor_description(self, category: str) -> str:
        """
        Generate a description for a risk factor.
        
        Args:
            category: Category of the risk factor
            
        Returns:
            Description of the risk factor
        """
        risk_factor_descriptions = {
            "financial": [
                "Unemployed for more than 6 months",
                "Income below federal poverty level",
                "Medical debt exceeding $5,000",
                "Unable to afford medications",
                "Recently filed for bankruptcy"
            ],
            "educational": [
                "Did not complete high school",
                "Limited English proficiency",
                "Low health literacy",
                "Difficulty understanding medical instructions",
                "Unable to read prescription labels"
            ],
            "healthcare": [
                "No regular primary care provider",
                "Uninsured or underinsured",
                "History of missed appointments",
                "Delayed seeking care due to cost",
                "Limited access to specialists"
            ],
            "environmental": [
                "Exposure to environmental hazards",
                "Unsafe neighborhood with high crime rate",
                "Limited access to parks or recreation",
                "Exposure to secondhand smoke",
                "Poor air or water quality in neighborhood"
            ],
            "social": [
                "Lives alone with limited social contacts",
                "Recent loss of spouse or partner",
                "No emergency contacts identified",
                "Reports feeling isolated or lonely",
                "Limited community engagement"
            ],
            "nutritional": [
                "Limited access to grocery stores",
                "Unable to afford nutritious food",
                "Relies on food pantries",
                "Skips meals due to financial constraints",
                "Limited knowledge of nutrition"
            ],
            "mobility": [
                "No reliable transportation",
                "Relies on public transportation",
                "Unable to drive due to medical condition",
                "Lives in area with limited public transportation",
                "Difficulty affording transportation costs"
            ],
            "housing": [
                "Currently homeless",
                "At risk of eviction",
                "Housing costs exceed 50% of income",
                "Unsafe or inadequate housing conditions",
                "Frequent moves in past year"
            ]
        }
        
        # Return a random description from the category
        return random.choice(risk_factor_descriptions.get(category, ["Risk factor not specified"]))
    
    def _generate_intervention_description(self, type: str) -> str:
        """
        Generate a description for an intervention.
        
        Args:
            type: Type of intervention
            
        Returns:
            Description of the intervention
        """
        intervention_descriptions = {
            "financial_assistance": [
                "Referral to financial assistance program for medication costs",
                "Application for utility assistance program",
                "Referral to job placement services",
                "Connection with medical bill advocacy program",
                "Assistance with applying for public benefits"
            ],
            "education_resources": [
                "Enrollment in GED program",
                "Referral to adult literacy program",
                "Provision of health education materials",
                "Connection with ESL classes",
                "Referral to vocational training program"
            ],
            "healthcare_navigation": [
                "Assignment of care navigator",
                "Assistance with insurance enrollment",
                "Connection with patient assistance programs",
                "Scheduling of follow-up appointments",
                "Coordination of transportation to medical appointments"
            ],
            "community_resources": [
                "Connection with community support groups",
                "Referral to senior center programs",
                "Information about community recreation programs",
                "Connection with volunteer opportunities",
                "Referral to religious or spiritual support"
            ],
            "social_support": [
                "Referral to social worker",
                "Connection with peer support program",
                "Referral to counseling services",
                "Arrangement for regular check-in calls",
                "Connection with community visitor program"
            ],
            "food_assistance": [
                "Referral to food bank",
                "Application for SNAP benefits",
                "Connection with meal delivery service",
                "Referral to community garden program",
                "Provision of grocery gift cards"
            ],
            "transportation_assistance": [
                "Arrangement for medical transportation service",
                "Provision of bus passes",
                "Connection with volunteer driver program",
                "Information about ride-sharing discount programs",
                "Referral to mobility assessment"
            ],
            "housing_assistance": [
                "Referral to housing assistance program",
                "Application for rental assistance",
                "Connection with emergency shelter",
                "Referral to home modification program",
                "Assistance with housing search"
            ]
        }
        
        # Return a random description from the type
        return random.choice(intervention_descriptions.get(type, ["Intervention not specified"]))