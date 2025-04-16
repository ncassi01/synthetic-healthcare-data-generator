"""
Care plan generator for the synthetic healthcare data generator.

This module generates synthetic care plans based on member data.
"""

import json
import logging
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from faker import Faker

from src.generators.base_generator import BaseGenerator
from src.models.narrative import CarePlan, CarePlanGoal, CarePlanIntervention, CarePlanType


class CarePlanGenerator(BaseGenerator):
    """Generator for synthetic care plans."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the care plan generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            self.faker.seed_instance(seed)
        
        # Load templates and condition-specific care plans
        self.templates = self._load_templates()
        self.condition_care_plans = self._load_condition_care_plans()
    
    def _load_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load care plan templates from the configuration.
        
        Returns:
            Dictionary of templates for different care plan types.
        """
        templates = {}
        
        # Default templates if not provided in config
        default_templates = {
            "treatment_plan": {
                "title": [
                    "Treatment Plan for {condition}",
                    "Medical Management Plan: {condition}",
                    "Therapeutic Approach for {condition}",
                    "Clinical Care Plan: {condition}"
                ],
                "description": [
                    "Comprehensive treatment plan for managing {condition} in {age}-year-old {gender}. Focus on {focus_area} with {approach}.",
                    "Medical management strategy for {condition}, addressing {focus_area} through {approach}. Plan includes monitoring of {monitoring_area}.",
                    "Therapeutic approach for {condition} management, emphasizing {focus_area} and {approach}. Regular assessment of {monitoring_area}."
                ]
            },
            "care_management": {
                "title": [
                    "Care Management Program: {condition}",
                    "Ongoing Care Plan for {condition}",
                    "Chronic Care Management: {condition}",
                    "Long-term Care Strategy: {condition}"
                ],
                "description": [
                    "Ongoing care management program for {condition}, focusing on {focus_area} and {approach}. Regular monitoring of {monitoring_area} with adjustments as needed.",
                    "Comprehensive care management for {age}-year-old {gender} with {condition}. Emphasis on {focus_area} through {approach} with periodic reassessment.",
                    "Long-term care strategy for {condition} management, addressing {focus_area} with {approach}. Includes regular evaluation of {monitoring_area}."
                ]
            },
            "discharge_plan": {
                "title": [
                    "Hospital Discharge Plan",
                    "Post-Hospitalization Care Plan",
                    "Transition of Care Plan",
                    "Post-Acute Care Strategy"
                ],
                "description": [
                    "Discharge plan following hospitalization for {condition}. Focuses on {focus_area} through {approach} with follow-up care coordination.",
                    "Post-hospitalization care plan for {age}-year-old {gender} after treatment for {condition}. Emphasis on {focus_area} and {approach}.",
                    "Transition of care strategy following inpatient stay for {condition}. Addresses {focus_area} with {approach} and scheduled follow-up appointments."
                ]
            },
            "chronic_condition": {
                "title": [
                    "Chronic Condition Management: {condition}",
                    "Long-term Disease Management Plan",
                    "Ongoing Care Strategy for {condition}",
                    "Chronic Disease Care Plan"
                ],
                "description": [
                    "Long-term management plan for chronic {condition} in {age}-year-old {gender}. Focuses on {focus_area} through {approach} with regular monitoring.",
                    "Comprehensive chronic disease management for {condition}, addressing {focus_area} with {approach}. Includes periodic assessment of {monitoring_area}.",
                    "Ongoing care strategy for chronic {condition}, emphasizing {focus_area} and {approach}. Regular evaluation of {monitoring_area} with plan adjustments as needed."
                ]
            },
            "preventive_care": {
                "title": [
                    "Preventive Care Plan",
                    "Health Maintenance Strategy",
                    "Wellness and Prevention Plan",
                    "Preventive Health Program"
                ],
                "description": [
                    "Preventive care plan for {age}-year-old {gender} with {condition_risk}. Focuses on {focus_area} through {approach} to prevent complications.",
                    "Comprehensive health maintenance strategy addressing {condition_risk}. Emphasis on {focus_area} and {approach} with regular screening.",
                    "Wellness and prevention plan for {age}-year-old {gender}, focusing on {focus_area} through {approach}. Includes screening for {condition_risk}."
                ]
            },
            "behavioral_health": {
                "title": [
                    "Behavioral Health Treatment Plan",
                    "Mental Health Care Strategy",
                    "Psychological Support Plan",
                    "Behavioral Intervention Program"
                ],
                "description": [
                    "Behavioral health plan for {age}-year-old {gender} with {condition}. Focuses on {focus_area} through {approach} with regular assessment.",
                    "Mental health care strategy addressing {condition}, emphasizing {focus_area} and {approach}. Includes ongoing evaluation of {monitoring_area}.",
                    "Psychological support plan for managing {condition}, focusing on {focus_area} through {approach}. Regular monitoring of {monitoring_area}."
                ]
            },
            "rehabilitation": {
                "title": [
                    "Rehabilitation Program: {condition}",
                    "Recovery and Rehabilitation Plan",
                    "Functional Restoration Strategy",
                    "Rehabilitative Care Plan"
                ],
                "description": [
                    "Rehabilitation program for {age}-year-old {gender} following {condition}. Focuses on {focus_area} through {approach} with progressive goals.",
                    "Comprehensive recovery plan addressing functional limitations from {condition}. Emphasis on {focus_area} and {approach} with regular reassessment.",
                    "Rehabilitative strategy for {condition}, focusing on {focus_area} through {approach}. Includes periodic evaluation of {monitoring_area} and functional progress."
                ]
            }
        }
        
        # Use templates from config if available, otherwise use defaults
        care_plan_templates = self.config.get("care_plan_templates", default_templates)
        
        for plan_type, sections in care_plan_templates.items():
            templates[plan_type] = sections
        
        return templates
    
    def _load_condition_care_plans(self) -> Dict[str, Dict[str, Any]]:
        """
        Load condition-specific care plan elements.
        
        Returns:
            Dictionary mapping conditions to care plan elements.
        """
        # Default condition care plans if not provided in config
        default_condition_plans = {
            "diabetes": {
                "focus_areas": ["glycemic control", "lifestyle modification", "complication prevention", "medication management"],
                "approaches": ["medication adjustment", "dietary counseling", "regular monitoring", "education and self-management"],
                "monitoring_areas": ["blood glucose levels", "HbA1c", "kidney function", "cardiovascular risk factors"],
                "goals": [
                    {"description": "Maintain HbA1c below 7.0%", "priority": "high"},
                    {"description": "Check blood glucose daily", "priority": "high"},
                    {"description": "Achieve/maintain healthy weight", "priority": "medium"},
                    {"description": "Complete annual eye examination", "priority": "medium"},
                    {"description": "Perform daily foot inspection", "priority": "medium"}
                ],
                "interventions": [
                    {"description": "Medication management", "type": "medication", "frequency": "daily", "instructions": "Take medications as prescribed"},
                    {"description": "Blood glucose monitoring", "type": "monitoring", "frequency": "daily", "instructions": "Check blood glucose 2-4 times daily"},
                    {"description": "Diabetic diet", "type": "education", "instructions": "Follow carbohydrate-controlled meal plan"},
                    {"description": "Regular exercise", "type": "education", "frequency": "at least 150 minutes per week", "instructions": "Moderate-intensity aerobic activity"},
                    {"description": "Foot care", "type": "education", "frequency": "daily", "instructions": "Inspect feet daily for cuts, blisters, or redness"}
                ]
            },
            "hypertension": {
                "focus_areas": ["blood pressure control", "cardiovascular risk reduction", "lifestyle modification", "medication adherence"],
                "approaches": ["medication management", "dietary counseling", "regular monitoring", "stress management"],
                "monitoring_areas": ["blood pressure readings", "cardiovascular risk factors", "medication side effects", "end-organ damage"],
                "goals": [
                    {"description": "Maintain blood pressure below 130/80 mmHg", "priority": "high"},
                    {"description": "Reduce sodium intake", "priority": "medium"},
                    {"description": "Achieve/maintain healthy weight", "priority": "medium"},
                    {"description": "Engage in regular physical activity", "priority": "medium"}
                ],
                "interventions": [
                    {"description": "Antihypertensive medication", "type": "medication", "frequency": "daily", "instructions": "Take medications as prescribed"},
                    {"description": "Blood pressure monitoring", "type": "monitoring", "frequency": "daily", "instructions": "Check blood pressure daily and record"},
                    {"description": "DASH diet", "type": "education", "instructions": "Follow low-sodium, high-potassium diet"},
                    {"description": "Regular exercise", "type": "education", "frequency": "at least 150 minutes per week", "instructions": "Moderate-intensity aerobic activity"},
                    {"description": "Stress management", "type": "education", "frequency": "daily", "instructions": "Practice relaxation techniques"}
                ]
            },
            "asthma": {
                "focus_areas": ["symptom control", "trigger avoidance", "lung function maintenance", "exacerbation prevention"],
                "approaches": ["medication management", "environmental control", "action plan development", "education and self-management"],
                "monitoring_areas": ["symptom frequency", "rescue inhaler use", "peak flow readings", "exacerbation frequency"],
                "goals": [
                    {"description": "Minimize daytime symptoms", "priority": "high"},
                    {"description": "Prevent nighttime awakenings", "priority": "high"},
                    {"description": "Maintain normal activity levels", "priority": "medium"},
                    {"description": "Minimize rescue inhaler use", "priority": "medium"},
                    {"description": "Prevent exacerbations requiring oral steroids", "priority": "high"}
                ],
                "interventions": [
                    {"description": "Controller medication", "type": "medication", "frequency": "daily", "instructions": "Use inhaled corticosteroid as prescribed"},
                    {"description": "Rescue inhaler", "type": "medication", "frequency": "as needed", "instructions": "Use for acute symptoms"},
                    {"description": "Peak flow monitoring", "type": "monitoring", "frequency": "daily", "instructions": "Check peak flow each morning"},
                    {"description": "Trigger avoidance", "type": "education", "instructions": "Identify and avoid personal asthma triggers"},
                    {"description": "Asthma action plan", "type": "education", "instructions": "Follow written plan based on symptoms and peak flow"}
                ]
            },
            "depression": {
                "focus_areas": ["symptom management", "functional improvement", "relapse prevention", "support system development"],
                "approaches": ["medication management", "psychotherapy", "lifestyle modification", "social support enhancement"],
                "monitoring_areas": ["mood symptoms", "suicidal ideation", "functional status", "treatment adherence"],
                "goals": [
                    {"description": "Reduce depressive symptoms", "priority": "high"},
                    {"description": "Improve sleep patterns", "priority": "medium"},
                    {"description": "Increase social engagement", "priority": "medium"},
                    {"description": "Return to normal daily activities", "priority": "medium"},
                    {"description": "Develop coping strategies", "priority": "high"}
                ],
                "interventions": [
                    {"description": "Antidepressant medication", "type": "medication", "frequency": "daily", "instructions": "Take as prescribed, continue even when feeling better"},
                    {"description": "Psychotherapy", "type": "referral", "frequency": "weekly", "instructions": "Attend cognitive behavioral therapy sessions"},
                    {"description": "Physical activity", "type": "education", "frequency": "daily", "instructions": "30 minutes of moderate exercise"},
                    {"description": "Sleep hygiene", "type": "education", "instructions": "Maintain regular sleep schedule and bedtime routine"},
                    {"description": "Social support", "type": "education", "instructions": "Engage with support network regularly"}
                ]
            },
            "congestive heart failure": {
                "focus_areas": ["fluid management", "cardiac function optimization", "symptom control", "complication prevention"],
                "approaches": ["medication management", "dietary counseling", "activity modification", "regular monitoring"],
                "monitoring_areas": ["fluid status", "weight", "symptom burden", "medication side effects"],
                "goals": [
                    {"description": "Maintain stable weight", "priority": "high"},
                    {"description": "Minimize edema", "priority": "high"},
                    {"description": "Improve exercise tolerance", "priority": "medium"},
                    {"description": "Reduce hospitalizations", "priority": "high"},
                    {"description": "Manage symptoms of dyspnea and fatigue", "priority": "medium"}
                ],
                "interventions": [
                    {"description": "Heart failure medications", "type": "medication", "frequency": "daily", "instructions": "Take as prescribed"},
                    {"description": "Daily weight monitoring", "type": "monitoring", "frequency": "daily", "instructions": "Weigh each morning, report gain of 2+ pounds in a day"},
                    {"description": "Sodium restriction", "type": "education", "instructions": "Limit sodium intake to 2000mg daily"},
                    {"description": "Fluid restriction", "type": "education", "instructions": "Limit fluid intake as directed"},
                    {"description": "Activity pacing", "type": "education", "instructions": "Balance activity with rest periods"}
                ]
            },
            "chronic obstructive pulmonary disease": {
                "focus_areas": ["respiratory function optimization", "exacerbation prevention", "symptom management", "functional capacity improvement"],
                "approaches": ["medication management", "pulmonary rehabilitation", "oxygen therapy", "smoking cessation"],
                "monitoring_areas": ["respiratory symptoms", "oxygen saturation", "exercise tolerance", "exacerbation frequency"],
                "goals": [
                    {"description": "Reduce dyspnea with activities", "priority": "high"},
                    {"description": "Prevent exacerbations", "priority": "high"},
                    {"description": "Maintain oxygen saturation above 90%", "priority": "high"},
                    {"description": "Improve exercise tolerance", "priority": "medium"},
                    {"description": "Maintain independence in activities of daily living", "priority": "medium"}
                ],
                "interventions": [
                    {"description": "Bronchodilator therapy", "type": "medication", "frequency": "as prescribed", "instructions": "Use inhalers as directed"},
                    {"description": "Oxygen therapy", "type": "equipment", "frequency": "as needed", "instructions": "Use supplemental oxygen as prescribed"},
                    {"description": "Pulmonary rehabilitation", "type": "referral", "frequency": "2-3 times weekly", "instructions": "Attend all scheduled sessions"},
                    {"description": "Breathing techniques", "type": "education", "instructions": "Practice pursed-lip and diaphragmatic breathing"},
                    {"description": "Exacerbation action plan", "type": "education", "instructions": "Follow written plan at first sign of exacerbation"}
                ]
            }
        }
        
        # Use condition care plans from config if available, otherwise use defaults
        return self.config.get("condition_care_plans", default_condition_plans)
    
    def generate(self, members: List[Dict], count: Optional[int] = None) -> List[CarePlan]:
        """
        Generate synthetic care plans based on member data.
        
        Args:
            members: List of member dictionaries to generate care plans for.
            count: Optional number of care plans to generate. If not provided,
                   will generate based on config settings.
                   
        Returns:
            List of generated care plans.
        """
        if not members:
            self.logger.warning("No members provided for care plan generation")
            return []
        
        care_plans = []
        plans_per_member = self.config.get("care_plans_per_member", {"min": 1, "max": 3})
        
        for member in members:
            # Determine how many care plans to generate for this member
            num_plans = random.randint(plans_per_member["min"], plans_per_member["max"])
            
            # Generate care plans for this member
            member_plans = self._generate_plans_for_member(member, num_plans)
            care_plans.extend(member_plans)
        
        # If count is specified, randomly select that many care plans
        if count is not None and count < len(care_plans):
            care_plans = random.sample(care_plans, count)
        
        return care_plans
    
    def _generate_plans_for_member(self, member: Dict, num_plans: int) -> List[CarePlan]:
        """
        Generate a specified number of care plans for a member.
        
        Args:
            member: Member dictionary to generate care plans for.
            num_plans: Number of care plans to generate.
            
        Returns:
            List of generated care plans.
        """
        plans = []
        
        # Get member details
        member_id = member["id"]
        age = member["age"]
        gender = member["demographics"]["gender"]
        conditions = member.get("conditions", [])
        
        # Generate dates for the care plans (within the last year)
        today = datetime.now()
        date_range = 365  # days
        
        # If no conditions, add some common ones for care plan generation
        if not conditions:
            common_conditions = ["hypertension", "diabetes", "asthma", "depression", "chronic pain"]
            conditions = random.sample(common_conditions, min(2, len(common_conditions)))
        
        # Generate provider ID (in a real system, this would come from a provider database)
        provider_id = f"PROV{random.randint(10000, 99999)}"
        
        # Ensure we don't try to create more care plans than available conditions
        num_plans = min(num_plans, len(conditions))
        
        # Select conditions to create care plans for
        selected_conditions = random.sample(conditions, num_plans)
        
        for condition in selected_conditions:
            # Select a random care plan type
            care_plan_type = random.choice(list(CarePlanType))
            
            # Generate a random date within the last year for creation
            days_ago = random.randint(0, date_range)
            created_date = today - timedelta(days=days_ago)
            
            # Start date is usually the same as created date
            start_date = created_date
            
            # End date is sometimes set (for completed plans) or None (for active plans)
            end_date = None
            if random.random() < 0.3:  # 30% chance of having an end date
                end_days = random.randint(30, 180)  # 1-6 months duration
                end_date = start_date + timedelta(days=end_days)
                status = "completed" if end_date < today else "active"
            else:
                status = "active"
            
            # Generate the care plan content
            plan_data = self._generate_care_plan_content(care_plan_type, condition, age, gender)
            
            # Create goals
            goals = self._generate_goals(condition, care_plan_type, start_date)
            
            # Create interventions
            interventions = self._generate_interventions(condition, care_plan_type)
            
            # Create the care plan
            plan = CarePlan(
                id=f"PLAN{uuid.uuid4().hex[:8]}",
                member_id=member_id,
                provider_id=provider_id,
                care_plan_type=care_plan_type,
                title=plan_data["title"],
                description=plan_data["description"],
                created_date=created_date,
                start_date=start_date,
                end_date=end_date,
                status=status,
                goals=goals,
                interventions=interventions,
                conditions_addressed=[condition]
            )
            
            plans.append(plan)
        
        return plans
    
    def _generate_care_plan_content(self, care_plan_type: CarePlanType, condition: str, 
                                   age: int, gender: str) -> Dict[str, str]:
        """
        Generate title and description for a care plan.
        
        Args:
            care_plan_type: Type of care plan.
            condition: Health condition being addressed.
            age: Age of the member.
            gender: Gender of the member.
            
        Returns:
            Dictionary with title and description.
        """
        plan_data = {
            "title": "",
            "description": ""
        }
        
        # Get templates for this care plan type
        type_key = care_plan_type.value
        if type_key in self.templates:
            # Get title template
            title_templates = self.templates[type_key].get("title", ["Care Plan for {condition}"])
            title_template = random.choice(title_templates)
            
            # Get description template
            description_templates = self.templates[type_key].get("description", ["Care plan for managing {condition}."])
            description_template = random.choice(description_templates)
            
            # Get condition-specific elements if available
            condition_elements = self.condition_care_plans.get(condition.lower(), {})
            focus_areas = condition_elements.get("focus_areas", ["symptom management", "treatment adherence", "lifestyle modification"])
            approaches = condition_elements.get("approaches", ["medication management", "regular monitoring", "education"])
            monitoring_areas = condition_elements.get("monitoring_areas", ["symptoms", "treatment response", "functional status"])
            
            # Format templates with variables
            title = title_template.replace("{condition}", condition)
            
            description = description_template.replace("{condition}", condition)
            description = description.replace("{age}", str(age))
            description = description.replace("{gender}", gender)
            description = description.replace("{focus_area}", random.choice(focus_areas))
            description = description.replace("{approach}", random.choice(approaches))
            description = description.replace("{monitoring_area}", random.choice(monitoring_areas))
            
            # For preventive care plans, add condition risk
            if care_plan_type == CarePlanType.PREVENTIVE_CARE:
                condition_risk = f"risk factors for {condition}"
                description = description.replace("{condition_risk}", condition_risk)
            
            plan_data["title"] = title
            plan_data["description"] = description
        else:
            # Fallback if no templates are available
            plan_data["title"] = f"Care Plan for {condition}"
            plan_data["description"] = f"Care plan for managing {condition} in {age}-year-old {gender}."
        
        return plan_data
    
    def _generate_goals(self, condition: str, care_plan_type: CarePlanType, 
                       start_date: datetime) -> List[CarePlanGoal]:
        """
        Generate goals for a care plan.
        
        Args:
            condition: Health condition being addressed.
            care_plan_type: Type of care plan.
            start_date: Start date of the care plan.
            
        Returns:
            List of care plan goals.
        """
        goals = []
        
        # Get condition-specific goals if available
        condition_elements = self.condition_care_plans.get(condition.lower(), {})
        condition_goals = condition_elements.get("goals", [])
        
        # If condition-specific goals are available, use them
        if condition_goals:
            # Determine how many goals to include (2-5)
            num_goals = min(random.randint(2, 5), len(condition_goals))
            selected_goals = random.sample(condition_goals, num_goals)
            
            for goal_data in selected_goals:
                # Generate target date (1-6 months from start date)
                target_days = random.randint(30, 180)
                target_date = start_date + timedelta(days=target_days)
                
                # Determine status (active, completed, cancelled)
                status_weights = {"active": 0.7, "completed": 0.2, "cancelled": 0.1}
                status = random.choices(list(status_weights.keys()), 
                                       weights=list(status_weights.values()), 
                                       k=1)[0]
                
                goal = CarePlanGoal(
                    description=goal_data["description"],
                    target_date=target_date,
                    status=status,
                    priority=goal_data.get("priority", "medium")
                )
                
                goals.append(goal)
        else:
            # Generate generic goals if no condition-specific goals are available
            generic_goals = [
                "Improve symptom management",
                "Increase medication adherence",
                "Enhance self-management skills",
                "Reduce risk factors",
                "Improve quality of life",
                "Prevent complications",
                "Increase physical activity",
                "Improve nutrition",
                "Enhance coping strategies",
                "Reduce healthcare utilization"
            ]
            
            # Determine how many goals to include (2-4)
            num_goals = random.randint(2, 4)
            selected_goals = random.sample(generic_goals, num_goals)
            
            for description in selected_goals:
                # Generate target date (1-6 months from start date)
                target_days = random.randint(30, 180)
                target_date = start_date + timedelta(days=target_days)
                
                # Determine status (active, completed, cancelled)
                status_weights = {"active": 0.7, "completed": 0.2, "cancelled": 0.1}
                status = random.choices(list(status_weights.keys()), 
                                       weights=list(status_weights.values()), 
                                       k=1)[0]
                
                # Determine priority (high, medium, low)
                priority_weights = {"high": 0.3, "medium": 0.5, "low": 0.2}
                priority = random.choices(list(priority_weights.keys()), 
                                         weights=list(priority_weights.values()), 
                                         k=1)[0]
                
                goal = CarePlanGoal(
                    description=description,
                    target_date=target_date,
                    status=status,
                    priority=priority
                )
                
                goals.append(goal)
        
        return goals
    
    def _generate_interventions(self, condition: str, care_plan_type: CarePlanType) -> List[CarePlanIntervention]:
        """
        Generate interventions for a care plan.
        
        Args:
            condition: Health condition being addressed.
            care_plan_type: Type of care plan.
            
        Returns:
            List of care plan interventions.
        """
        interventions = []
        
        # Get condition-specific interventions if available
        condition_elements = self.condition_care_plans.get(condition.lower(), {})
        condition_interventions = condition_elements.get("interventions", [])
        
        # If condition-specific interventions are available, use them
        if condition_interventions:
            # Determine how many interventions to include (2-5)
            num_interventions = min(random.randint(2, 5), len(condition_interventions))
            selected_interventions = random.sample(condition_interventions, num_interventions)
            
            for intervention_data in selected_interventions:
                intervention = CarePlanIntervention(
                    description=intervention_data["description"],
                    type=intervention_data.get("type", "education"),
                    frequency=intervention_data.get("frequency"),
                    duration=intervention_data.get("duration"),
                    instructions=intervention_data.get("instructions")
                )
                
                interventions.append(intervention)
        else:
            # Generate generic interventions if no condition-specific interventions are available
            intervention_types = {
                "medication": [
                    "Medication management",
                    "Prescription adjustment",
                    "Medication review",
                    "New medication trial"
                ],
                "procedure": [
                    "Diagnostic testing",
                    "Therapeutic procedure",
                    "Preventive procedure",
                    "Monitoring procedure"
                ],
                "referral": [
                    "Specialist consultation",
                    "Therapy referral",
                    "Support group referral",
                    "Community resource referral"
                ],
                "education": [
                    "Disease management education",
                    "Lifestyle modification counseling",
                    "Self-management training",
                    "Nutritional counseling"
                ],
                "monitoring": [
                    "Symptom monitoring",
                    "Vital sign tracking",
                    "Laboratory monitoring",
                    "Functional assessment"
                ]
            }
            
            # Determine how many interventions to include (2-4)
            num_interventions = random.randint(2, 4)
            
            # Select intervention types to include
            selected_types = random.sample(list(intervention_types.keys()), 
                                          min(num_interventions, len(intervention_types)))
            
            for intervention_type in selected_types:
                # Select a description for this intervention type
                description = random.choice(intervention_types[intervention_type])
                
                # Generate frequency if applicable
                frequency = None
                if intervention_type in ["medication", "monitoring"]:
                    frequencies = ["daily", "twice daily", "weekly", "monthly", "as needed"]
                    frequency = random.choice(frequencies)
                
                # Generate duration if applicable
                duration = None
                if intervention_type in ["medication", "referral"]:
                    durations = ["30 days", "90 days", "6 months", "ongoing", "until next assessment"]
                    duration = random.choice(durations)
                
                # Generate instructions if applicable
                instructions = None
                if random.random() < 0.7:  # 70% chance of having instructions
                    instruction_templates = [
                        "Follow prescribed regimen",
                        "Report any side effects",
                        "Document results in journal",
                        "Contact provider if symptoms worsen",
                        "Schedule follow-up appointment after completion"
                    ]
                    instructions = random.choice(instruction_templates)
                
                intervention = CarePlanIntervention(
                    description=description,
                    type=intervention_type,
                    frequency=frequency,
                    duration=duration,
                    instructions=instructions
                )
                
                interventions.append(intervention)
        
        return interventions