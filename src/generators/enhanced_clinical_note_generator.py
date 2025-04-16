"""
Enhanced clinical note generator with provider-specific writing styles.

This module extends the base clinical note generator to add provider-specific
writing styles, making the generated notes more realistic and varied.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from src.generators.clinical_note_generator import ClinicalNoteGenerator
from src.models.narrative import ClinicalNote, NoteType


class EnhancedClinicalNoteGenerator(ClinicalNoteGenerator):
    """
    Enhanced generator for synthetic clinical notes with provider-specific writing styles.
    
    This class extends the base ClinicalNoteGenerator to add provider-specific writing
    styles, making the generated notes more realistic and varied.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the enhanced clinical note generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        
        # Initialize provider profiles
        self._initialize_provider_profiles()
        
        # Track provider styles for consistency
        self.provider_styles = {}
    
    def _initialize_provider_profiles(self):
        """Initialize different provider writing style profiles."""
        self.provider_profiles = {
            "concise": {
                "sentence_length": "short",
                "terminology": "standard",
                "structure": "bullet_points",
                "detail_level": "minimal",
                "abbreviation_frequency": "high"
            },
            "detailed": {
                "sentence_length": "long",
                "terminology": "academic",
                "structure": "narrative",
                "detail_level": "extensive",
                "abbreviation_frequency": "low"
            },
            "balanced": {
                "sentence_length": "medium",
                "terminology": "mixed",
                "structure": "mixed",
                "detail_level": "moderate",
                "abbreviation_frequency": "moderate"
            }
        }
        
        # Add provider-specific phrases and templates
        self.provider_specific_phrases = {
            "concise": {
                "assessment_intros": ["Impression:", "A/P:", "Assessment:"],
                "plan_intros": ["Plan:", "Will:", "Next steps:"],
                "common_phrases": ["as noted", "as above", "continue", "follow up prn"],
                "transitions": ["then", "also", "additionally"],
                "abbreviations": {
                    "history of present illness": "HPI",
                    "review of systems": "ROS",
                    "physical examination": "PE",
                    "assessment and plan": "A/P",
                    "follow up": "f/u",
                    "as needed": "prn",
                    "three times a day": "TID",
                    "twice a day": "BID",
                    "once a day": "QD",
                    "every day": "QD",
                    "every hour": "q1h",
                    "every 4 hours": "q4h",
                    "every 6 hours": "q6h",
                    "every 8 hours": "q8h",
                    "every 12 hours": "q12h",
                    "before meals": "AC",
                    "after meals": "PC",
                    "nothing by mouth": "NPO",
                    "shortness of breath": "SOB",
                    "hypertension": "HTN",
                    "diabetes mellitus": "DM",
                    "coronary artery disease": "CAD",
                    "chronic obstructive pulmonary disease": "COPD",
                    "urinary tract infection": "UTI",
                    "upper respiratory infection": "URI",
                    "gastroesophageal reflux disease": "GERD"
                }
            },
            "detailed": {
                "assessment_intros": ["Assessment and Plan:", "Clinical Assessment:", "Diagnostic Impression:"],
                "plan_intros": ["Therapeutic Plan:", "Management Strategy:", "Treatment Recommendations:"],
                "common_phrases": ["it is my clinical opinion that", "upon careful consideration", "the patient would benefit from", "it is recommended that"],
                "transitions": ["furthermore", "moreover", "in addition", "consequently", "therefore"],
                "abbreviations": {}  # Detailed providers use fewer abbreviations
            },
            "balanced": {
                "assessment_intros": ["Assessment:", "Impression:", "Clinical Picture:"],
                "plan_intros": ["Plan:", "Recommendations:", "Management:"],
                "common_phrases": ["consider", "recommend", "suggest", "appears to be", "likely"],
                "transitions": ["also", "additionally", "further", "moreover"],
                "abbreviations": {
                    "history of present illness": "HPI",
                    "review of systems": "ROS",
                    "physical examination": "PE",
                    "hypertension": "HTN",
                    "diabetes mellitus": "DM",
                    "coronary artery disease": "CAD",
                    "chronic obstructive pulmonary disease": "COPD"
                }
            }
        }
        
        # Add provider-specific section formats
        self.provider_section_formats = {
            "concise": {
                "subjective": "{chief_complaint}. {brief_history}",
                "objective": "VS: {vital_signs_brief}\n\n{exam_findings_brief}",
                "assessment": "{diagnosis}. {brief_status}",
                "plan": "1. {treatment_brief}\n2. {medication_brief}\n3. {followup_brief}"
            },
            "detailed": {
                "subjective": "The patient is a {age}-year-old {gender} who presents today for evaluation of {chief_complaint}. {detailed_history}",
                "objective": "VITAL SIGNS:\n{vital_signs_detailed}\n\nPHYSICAL EXAMINATION:\n{exam_findings_detailed}",
                "assessment": "ASSESSMENT:\n{diagnosis}: {detailed_status}. {detailed_reasoning}",
                "plan": "PLAN:\n1. {treatment_detailed}\n2. {medication_detailed}\n3. {followup_detailed}\n4. {education_detailed}"
            },
            "balanced": {
                "subjective": "Patient is a {age}-year-old {gender} presenting with {chief_complaint}. {history}",
                "objective": "Vital Signs: {vital_signs}\n\nPhysical Exam: {exam_findings}",
                "assessment": "Assessment: {diagnosis}. {status}",
                "plan": "Plan:\n- {treatment}\n- {medication}\n- {followup}"
            }
        }
    
    def _get_provider_style(self, provider_id):
        """
        Get a consistent style for a provider.
        
        Args:
            provider_id: The provider's ID.
            
        Returns:
            A consistent style for this provider.
        """
        if provider_id not in self.provider_styles:
            self.provider_styles[provider_id] = random.choice(list(self.provider_profiles.keys()))
        
        return self.provider_styles[provider_id]
    
    def _apply_abbreviations(self, text, provider_style):
        """
        Apply provider-specific abbreviations to text.
        
        Args:
            text: The text to modify.
            provider_style: The provider's style.
            
        Returns:
            Text with appropriate abbreviations applied.
        """
        if provider_style not in self.provider_specific_phrases:
            return text
            
        abbreviations = self.provider_specific_phrases[provider_style].get("abbreviations", {})
        
        # Skip if no abbreviations for this style or empty text
        if not abbreviations or not text:
            return text
            
        # Apply abbreviations (case-insensitive)
        modified_text = text
        for full_text, abbrev in abbreviations.items():
            # Use word boundaries to avoid partial word replacements
            # Only replace with a certain probability based on style
            if provider_style == "concise" and random.random() < 0.8:
                modified_text = modified_text.replace(f" {full_text} ", f" {abbrev} ")
            elif provider_style == "balanced" and random.random() < 0.5:
                modified_text = modified_text.replace(f" {full_text} ", f" {abbrev} ")
        
        return modified_text
    
    def _generate_notes_for_member(self, member: Dict, num_notes: int) -> List[ClinicalNote]:
        """
        Generate a specified number of clinical notes for a member with provider-specific styles.
        
        Args:
            member: Member dictionary to generate notes for.
            num_notes: Number of notes to generate.
            
        Returns:
            List of generated clinical notes.
        """
        notes = []
        
        # Get member details
        member_id = member["id"]
        age = member["age"]
        gender = member["demographics"]["gender"]
        conditions = member.get("conditions", [])
        medications = member.get("medications", [])
        procedures = member.get("procedures", [])
        
        # Generate dates for the notes (within the last year)
        today = datetime.now()
        date_range = 365  # days
        
        # Create a set of provider IDs to use for this member
        # This simulates a member seeing a consistent set of providers
        num_providers = min(num_notes, random.randint(1, 3))
        member_providers = [f"PROV{random.randint(10000, 99999)}" for _ in range(num_providers)]
        
        for _ in range(num_notes):
            # Generate a random date within the last year
            days_ago = random.randint(0, date_range)
            note_date = today - timedelta(days=days_ago)
            
            # Select a random note type
            note_type = random.choice(list(NoteType))
            
            # Select a provider from the member's provider set
            provider_id = random.choice(member_providers)
            
            # Get the provider's consistent style
            provider_style = self._get_provider_style(provider_id)
            
            # Generate the note content with the provider's style
            chief_complaint = self._generate_chief_complaint(conditions, medications)
            subjective = self._generate_subjective(age, gender, conditions, chief_complaint, provider_style)
            objective = self._generate_objective(conditions, provider_style)
            assessment = self._generate_assessment(conditions, provider_style)
            plan = self._generate_plan(conditions, medications, provider_style)
            
            # Create diagnosis and procedure codes
            diagnosis_codes = self._generate_diagnosis_codes(conditions)
            procedure_codes = self._generate_procedure_codes(procedures)
            
            # Create the clinical note
            note = ClinicalNote(
                id=f"NOTE{uuid.uuid4().hex[:8]}",
                member_id=member_id,
                provider_id=provider_id,
                note_type=note_type,
                date_of_service=note_date,
                chief_complaint=chief_complaint,
                subjective=subjective,
                objective=objective,
                assessment=assessment,
                plan=plan,
                diagnosis_codes=diagnosis_codes,
                procedure_codes=procedure_codes,
                medication_references=medications
            )
            
            notes.append(note)
        
        return notes
    
    def _generate_subjective(self, age: int, gender: str, conditions: List[str], chief_complaint: str, provider_style: str = "balanced") -> str:
        """
        Generate the subjective section of the note with provider-specific style.
        
        Args:
            age: Age of the member.
            gender: Gender of the member.
            conditions: List of member conditions.
            chief_complaint: Chief complaint for this visit.
            provider_style: The provider's writing style.
            
        Returns:
            Subjective section text with appropriate style.
        """
        # Get the base subjective text from the parent class
        base_subjective = super()._generate_subjective(age, gender, conditions, chief_complaint)
        
        # Apply style-specific modifications
        if provider_style == "concise":
            # Shorten sentences, use more abbreviations
            subjective = base_subjective.split(". ")
            if len(subjective) > 2:
                # Keep only the first 1-2 sentences for concise style
                subjective = subjective[:random.randint(1, 2)]
            subjective = ". ".join(subjective)
            
            # Apply abbreviations
            subjective = self._apply_abbreviations(subjective, provider_style)
            
            # Add style-specific phrases
            common_phrases = self.provider_specific_phrases["concise"]["common_phrases"]
            if random.random() < 0.3 and common_phrases:
                subjective += f" {random.choice(common_phrases)}."
                
        elif provider_style == "detailed":
            # Add more detail and formal language
            subjective = base_subjective
            
            # Add style-specific phrases and transitions
            common_phrases = self.provider_specific_phrases["detailed"]["common_phrases"]
            transitions = self.provider_specific_phrases["detailed"]["transitions"]
            
            if random.random() < 0.4 and common_phrases:
                # Add a detailed phrase
                additional_detail = f" {random.choice(transitions)}, {random.choice(common_phrases)} the patient's symptoms warrant thorough evaluation."
                subjective += additional_detail
                
            # Add more formal medical terminology
            subjective = subjective.replace("pain", "discomfort")
            subjective = subjective.replace("problems", "issues")
            subjective = subjective.replace("better", "improved")
            subjective = subjective.replace("worse", "exacerbated")
            
        else:  # balanced
            # Make minor modifications for balanced style
            subjective = base_subjective
            
            # Apply some abbreviations but not as many as concise
            subjective = self._apply_abbreviations(subjective, provider_style)
            
            # Occasionally add a balanced phrase
            common_phrases = self.provider_specific_phrases["balanced"]["common_phrases"]
            if random.random() < 0.2 and common_phrases:
                subjective += f" I {random.choice(common_phrases)} continued monitoring."
        
        return subjective
    
    def _generate_objective(self, conditions: List[str], provider_style: str = "balanced") -> str:
        """
        Generate the objective section of the note with provider-specific style.
        
        Args:
            conditions: List of member conditions.
            provider_style: The provider's writing style.
            
        Returns:
            Objective section text with appropriate style.
        """
        # Get the base objective text from the parent class
        base_objective = super()._generate_objective(conditions)
        
        # Apply style-specific modifications
        if provider_style == "concise":
            # Make it more concise with abbreviations and bullet points
            lines = base_objective.split("\n")
            modified_lines = []
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Convert section headers
                if "Vital Signs" in line or "VITAL SIGNS" in line:
                    modified_lines.append("VS:")
                elif "Physical Examination" in line or "PHYSICAL EXAMINATION" in line:
                    modified_lines.append("PE:")
                elif "General" in line:
                    modified_lines.append("Gen:")
                else:
                    # Apply abbreviations to regular lines
                    modified_line = self._apply_abbreviations(line, provider_style)
                    modified_lines.append(modified_line)
            
            objective = "\n".join(modified_lines)
            
        elif provider_style == "detailed":
            # Make it more detailed and structured
            lines = base_objective.split("\n")
            modified_lines = []
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Convert section headers to uppercase
                if "Vital Signs" in line:
                    modified_lines.append("VITAL SIGNS:")
                elif "Physical Examination" in line:
                    modified_lines.append("PHYSICAL EXAMINATION:")
                elif "General" in line:
                    modified_lines.append("GENERAL APPEARANCE:")
                else:
                    # Add more detail to findings
                    if ":" in line and random.random() < 0.3:
                        system, finding = line.split(":", 1)
                        if "normal" in finding.lower() or "unremarkable" in finding.lower():
                            finding = finding.strip()
                            detailed_findings = [
                                f"{finding} with no evidence of pathology",
                                f"{finding} with no concerning features",
                                f"{finding} with no significant abnormalities identified"
                            ]
                            line = f"{system}: {random.choice(detailed_findings)}"
                    modified_lines.append(line)
            
            objective = "\n".join(modified_lines)
            
        else:  # balanced
            # Make minor modifications for balanced style
            objective = base_objective
            
            # Apply some abbreviations but not as many as concise
            objective = self._apply_abbreviations(objective, provider_style)
        
        return objective
    
    def _generate_assessment(self, conditions: List[str], provider_style: str = "balanced") -> str:
        """
        Generate the assessment section of the note with provider-specific style.
        
        Args:
            conditions: List of member conditions.
            provider_style: The provider's writing style.
            
        Returns:
            Assessment section text with appropriate style.
        """
        # Get the base assessment text from the parent class
        base_assessment = super()._generate_assessment(conditions)
        
        # Apply style-specific modifications
        if provider_style == "concise":
            # Make it more concise with abbreviations
            assessment = base_assessment
            
            # Replace the assessment intro with a style-specific one
            assessment_intros = self.provider_specific_phrases["concise"]["assessment_intros"]
            for intro in ["Assessment:", "Impression:", "Assessment and Plan:", "Diagnoses:"]:
                if assessment.startswith(intro):
                    assessment = assessment.replace(intro, random.choice(assessment_intros), 1)
                    break
            
            # Apply abbreviations
            assessment = self._apply_abbreviations(assessment, provider_style)
            
            # Shorten by removing some detail
            if ". " in assessment:
                parts = assessment.split(". ")
                if len(parts) > 1:
                    assessment = parts[0] + "."
            
        elif provider_style == "detailed":
            # Make it more detailed and formal
            assessment = base_assessment
            
            # Replace the assessment intro with a style-specific one
            assessment_intros = self.provider_specific_phrases["detailed"]["assessment_intros"]
            for intro in ["Assessment:", "Impression:", "Assessment and Plan:", "Diagnoses:"]:
                if assessment.startswith(intro):
                    assessment = assessment.replace(intro, random.choice(assessment_intros), 1)
                    break
            
            # Add more detail if it's a simple assessment
            if len(assessment.split()) < 15 and conditions:
                condition = random.choice(conditions)
                detailed_additions = [
                    f" The patient's {condition} appears to be responding appropriately to the current management strategy.",
                    f" Based on today's evaluation, the {condition} is stable without evidence of progression.",
                    f" Clinical presentation is consistent with {condition} of moderate severity requiring ongoing management."
                ]
                assessment += random.choice(detailed_additions)
            
        else:  # balanced
            # Make minor modifications for balanced style
            assessment = base_assessment
            
            # Replace the assessment intro with a style-specific one
            assessment_intros = self.provider_specific_phrases["balanced"]["assessment_intros"]
            for intro in ["Assessment:", "Impression:", "Assessment and Plan:", "Diagnoses:"]:
                if assessment.startswith(intro):
                    assessment = assessment.replace(intro, random.choice(assessment_intros), 1)
                    break
            
            # Apply some abbreviations but not as many as concise
            assessment = self._apply_abbreviations(assessment, provider_style)
        
        return assessment
    
    def _generate_plan(self, conditions: List[str], medications: List[str], provider_style: str = "balanced") -> str:
        """
        Generate the plan section of the note with provider-specific style.
        
        Args:
            conditions: List of member conditions.
            medications: List of member medications.
            provider_style: The provider's writing style.
            
        Returns:
            Plan section text with appropriate style.
        """
        # Get the base plan text from the parent class
        base_plan = super()._generate_plan(conditions, medications)
        
        # Apply style-specific modifications
        if provider_style == "concise":
            # Make it more concise with abbreviations and numbered format
            plan = base_plan
            
            # Replace the plan intro with a style-specific one
            plan_intros = self.provider_specific_phrases["concise"]["plan_intros"]
            for intro in ["Plan:", "Recommendations:", "Management:"]:
                if plan.startswith(intro):
                    plan = plan.replace(intro, random.choice(plan_intros), 1)
                    break
            
            # Apply abbreviations
            plan = self._apply_abbreviations(plan, provider_style)
            
            # Ensure it's in a numbered format
            if not any(line.strip().startswith(str(i)) for i in range(1, 10) for line in plan.split("\n")):
                # Convert to numbered format
                items = [item.strip() for item in plan.split(".") if item.strip()]
                if items:
                    plan = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
            
        elif provider_style == "detailed":
            # Make it more detailed and structured
            plan = base_plan
            
            # Replace the plan intro with a style-specific one
            plan_intros = self.provider_specific_phrases["detailed"]["plan_intros"]
            for intro in ["Plan:", "Recommendations:", "Management:"]:
                if plan.startswith(intro):
                    plan = plan.replace(intro, random.choice(plan_intros), 1)
                    break
            
            # Add more detail to the plan
            if not plan.startswith("1.") and not plan.startswith("PLAN:"):
                plan = "PLAN:\n" + plan
            
            # Add patient education section if not present
            if "education" not in plan.lower() and "instruct" not in plan.lower():
                education_items = [
                    "Patient education provided regarding medication side effects and when to seek medical attention.",
                    "Comprehensive education provided on disease management and lifestyle modifications.",
                    "Detailed instructions given to patient regarding home monitoring and symptom management."
                ]
                plan += f"\n\nPATIENT EDUCATION: {random.choice(education_items)}"
            
        else:  # balanced
            # Make minor modifications for balanced style
            plan = base_plan
            
            # Replace the plan intro with a style-specific one
            plan_intros = self.provider_specific_phrases["balanced"]["plan_intros"]
            for intro in ["Plan:", "Recommendations:", "Management:"]:
                if plan.startswith(intro):
                    plan = plan.replace(intro, random.choice(plan_intros), 1)
                    break
            
            # Apply some abbreviations but not as many as concise
            plan = self._apply_abbreviations(plan, provider_style)
            
            # Ensure it has a clear structure
            if not any(line.strip().startswith("-") for line in plan.split("\n")) and not any(line.strip().startswith(str(i)) for i in range(1, 10) for line in plan.split("\n")):
                # Convert to bulleted format
                items = [item.strip() for item in plan.split(".") if item.strip()]
                if items:
                    plan = "\n".join(f"- {item}" for item in items)
        
        return plan