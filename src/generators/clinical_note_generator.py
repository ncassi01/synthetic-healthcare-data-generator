"""
Clinical note generator for the synthetic healthcare data generator.

This module generates synthetic clinical notes based on member data.
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
from src.models.narrative import ClinicalNote, NoteType


class ClinicalNoteGenerator(BaseGenerator):
    """Generator for synthetic clinical notes."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the clinical note generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            self.faker.seed_instance(seed)
        
        # Load templates
        self.templates = self._load_templates()
        
        # Common medical terms
        self.vital_signs = [
            "Blood Pressure: {}/{}",
            "Heart Rate: {} bpm",
            "Respiratory Rate: {} breaths/min",
            "Temperature: {:.1f}°F",
            "Oxygen Saturation: {}%",
            "Weight: {} lbs",
            "Height: {}'{}\"",
            "BMI: {:.1f}"
        ]
        
        self.physical_exam_findings = [
            "HEENT: {}",
            "Cardiovascular: {}",
            "Respiratory: {}",
            "Gastrointestinal: {}",
            "Musculoskeletal: {}",
            "Neurological: {}",
            "Skin: {}",
            "Psychiatric: {}"
        ]
        
        self.normal_findings = [
            "normal",
            "unremarkable",
            "within normal limits",
            "no abnormalities detected",
            "normal examination"
        ]
        
        self.abnormal_findings = {
            "HEENT": [
                "tympanic membrane erythema",
                "pharyngeal erythema",
                "sinus tenderness",
                "conjunctival injection",
                "rhinorrhea"
            ],
            "Cardiovascular": [
                "irregular rhythm",
                "systolic murmur",
                "diastolic murmur",
                "tachycardia",
                "bradycardia",
                "peripheral edema"
            ],
            "Respiratory": [
                "wheezing",
                "crackles",
                "rhonchi",
                "decreased breath sounds",
                "tachypnea",
                "accessory muscle use"
            ],
            "Gastrointestinal": [
                "abdominal tenderness",
                "hepatomegaly",
                "splenomegaly",
                "positive bowel sounds",
                "abdominal distension"
            ],
            "Musculoskeletal": [
                "joint tenderness",
                "decreased range of motion",
                "muscle weakness",
                "joint effusion",
                "muscle atrophy"
            ],
            "Neurological": [
                "decreased sensation",
                "tremor",
                "ataxia",
                "hyperreflexia",
                "hyporeflexia"
            ],
            "Skin": [
                "rash",
                "erythema",
                "lesion",
                "ulceration",
                "ecchymosis"
            ],
            "Psychiatric": [
                "anxious mood",
                "depressed affect",
                "tangential thought process",
                "impaired insight",
                "impaired judgment"
            ]
        }
        
        # Common plan elements
        self.plan_elements = [
            "Continue current medications",
            "Follow up in {} weeks",
            "Obtain {} laboratory tests",
            "Refer to {} specialist",
            "Schedule {} imaging",
            "Start new medication: {}",
            "Adjust dosage of {}",
            "Discontinue {}",
            "Patient education provided regarding {}",
            "Lifestyle modifications discussed"
        ]
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """
        Load clinical note templates from the configuration.
        
        Returns:
            Dictionary of templates for different note types.
        """
        templates = {}
        
        # Default templates if not provided in config
        default_templates = {
            "chief_complaint": [
                "{condition} follow-up",
                "Evaluation of {condition}",
                "New onset {symptom}",
                "Worsening {symptom}",
                "Annual wellness visit",
                "Medication refill for {medication}",
                "Post-hospital follow-up",
                "Pre-operative evaluation",
                "Consultation for {condition}"
            ],
            "subjective": [
                "Patient is a {age}-year-old {gender} with a history of {conditions} presenting for {reason}. {symptom_description}",
                "{age}-year-old {gender} with {conditions} reports {symptom_description}. Patient states {patient_statement}.",
                "Patient returns for follow-up of {conditions}. Since last visit, patient reports {symptom_changes}.",
                "{age}-year-old {gender} presents for evaluation of {symptom_description}. Symptoms began {symptom_onset} and are {symptom_quality}."
            ],
            "assessment": [
                "{diagnosis}. {stability_statement}",
                "Assessment: {diagnosis}. {plan_rationale}",
                "{diagnosis}, {severity}. {complication_risk}",
                "Working diagnosis of {diagnosis} based on {diagnostic_criteria}."
            ],
            "plan": [
                "1. {treatment_plan}\n2. {medication_plan}\n3. {follow_up_plan}",
                "Plan: {treatment_plan}. Will {medication_plan}. Follow up in {timeframe}.",
                "Will proceed with {treatment_plan}. {medication_plan}. {monitoring_plan}.",
                "{treatment_plan}. Continue {current_medications}. {diagnostic_plan}. Return to clinic in {timeframe}."
            ]
        }
        
        # Use templates from config if available, otherwise use defaults
        note_templates = self.config.get("clinical_note_templates", default_templates)
        
        for section, section_templates in note_templates.items():
            templates[section] = section_templates
        
        return templates
    
    def generate(self, members: List[Dict], count: Optional[int] = None) -> List[ClinicalNote]:
        """
        Generate synthetic clinical notes based on member data.
        
        Args:
            members: List of member dictionaries to generate notes for.
            count: Optional number of notes to generate. If not provided,
                   will generate based on config settings.
                   
        Returns:
            List of generated clinical notes.
        """
        if not members:
            self.logger.warning("No members provided for clinical note generation")
            return []
        
        notes = []
        notes_per_member = self.config.get("notes_per_member", {"min": 1, "max": 5})
        
        for member in members:
            # Determine how many notes to generate for this member
            num_notes = random.randint(notes_per_member["min"], notes_per_member["max"])
            
            # Generate notes for this member
            member_notes = self._generate_notes_for_member(member, num_notes)
            notes.extend(member_notes)
        
        # If count is specified, randomly select that many notes
        if count is not None and count < len(notes):
            notes = random.sample(notes, count)
        
        return notes
    
    def _generate_notes_for_member(self, member: Dict, num_notes: int) -> List[ClinicalNote]:
        """
        Generate a specified number of clinical notes for a member.
        
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
        
        for _ in range(num_notes):
            # Generate a random date within the last year
            days_ago = random.randint(0, date_range)
            note_date = today - timedelta(days=days_ago)
            
            # Select a random note type
            note_type = random.choice(list(NoteType))
            
            # Generate provider ID (in a real system, this would come from a provider database)
            provider_id = f"PROV{random.randint(10000, 99999)}"
            
            # Generate the note content
            chief_complaint = self._generate_chief_complaint(conditions, medications)
            subjective = self._generate_subjective(age, gender, conditions, chief_complaint)
            objective = self._generate_objective(conditions)
            assessment = self._generate_assessment(conditions)
            plan = self._generate_plan(conditions, medications)
            
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
    
    def _generate_chief_complaint(self, conditions: List[str], medications: List[str]) -> str:
        """
        Generate a chief complaint based on member conditions or medications.
        Creates more variable and realistic complaints.
        """
        if not conditions and not medications:
            wellness_visits = [
                "Annual wellness visit",
                "Routine health maintenance",
                "Preventive health check",
                "Annual physical examination",
                "Health screening",
                "Routine check-up"
            ]
            return random.choice(wellness_visits)
        
        template = random.choice(self.templates.get("chief_complaint", ["Evaluation of {condition}"]))
        
        if "{condition}" in template and conditions:
            condition = random.choice(conditions)
            # Add duration or severity qualifiers for more realism
            qualifiers = [
                f"{condition} for {random.randint(1, 30)} days",
                f"{condition}, {random.choice(['mild', 'moderate', 'severe'])}",
                f"{condition}, {random.choice(['worsening', 'improving', 'persistent', 'recurrent'])}",
                f"{condition} with {random.choice(['associated symptoms', 'complications', 'concerns'])}"
            ]
            return template.replace("{condition}", random.choice([condition] + qualifiers))
        elif "{medication}" in template and medications:
            medication = random.choice(medications)
            # Add medication-related context
            contexts = [
                f"{medication} refill",
                f"{medication} side effects",
                f"{medication} efficacy review",
                f"{medication} dosage adjustment"
            ]
            return template.replace("{medication}", random.choice(contexts))
        elif "{symptom}" in template:
            symptoms = [
                "pain", "fatigue", "dizziness", "shortness of breath", "headache",
                "nausea", "vomiting", "fever", "cough", "rash", "swelling",
                "numbness", "tingling", "weakness", "palpitations", "chest pain",
                "abdominal pain", "back pain", "joint pain", "muscle aches"
            ]
            symptom = random.choice(symptoms)
            # Add location or quality for more specificity
            if symptom == "pain":
                locations = ["chest", "abdominal", "back", "joint", "head", "neck", "shoulder", "knee", "hip"]
                symptom = f"{random.choice(locations)} {symptom}"
            
            # Add duration or severity
            qualifiers = [
                f"{symptom} for {random.randint(1, 30)} days",
                f"{symptom}, {random.choice(['mild', 'moderate', 'severe'])}",
                f"{symptom}, {random.choice(['worsening', 'improving', 'persistent', 'recurrent'])}"
            ]
            return template.replace("{symptom}", random.choice([symptom] + qualifiers))
        else:
            visit_reasons = [
                "Follow-up visit",
                "Consultation",
                "Health concern",
                "New symptom evaluation",
                "Post-hospital follow-up",
                "Pre-operative assessment"
            ]
            return random.choice(visit_reasons)
    
    def _generate_subjective(self, age: int, gender: str, conditions: List[str], chief_complaint: str) -> str:
        """
        Generate the subjective section of the note with enhanced variability and realism.
        Creates more diverse and realistic patient narratives.
        """
        if not self.templates.get("subjective"):
            # Create varied default templates if none provided
            default_templates = [
                f"Patient is a {age}-year-old {gender} presenting for {chief_complaint}.",
                f"{age}-year-old {gender} here for evaluation of {chief_complaint}.",
                f"I am seeing this {age}-year-old {gender} regarding {chief_complaint}.",
                f"This {age}-year-old {gender} presents today for {chief_complaint}."
            ]
            return random.choice(default_templates)
        
        template = random.choice(self.templates["subjective"])
        
        # Format conditions as a comma-separated list with varied phrasing
        if not conditions:
            conditions_texts = [
                "no significant past medical history",
                "no chronic medical conditions",
                "generally healthy with no major medical issues",
                "no known chronic illnesses"
            ]
            conditions_text = random.choice(conditions_texts)
        else:
            if len(conditions) == 1:
                condition_phrases = [
                    conditions[0],
                    f"a history of {conditions[0]}",
                    f"known {conditions[0]}"
                ]
                conditions_text = random.choice(condition_phrases)
            else:
                # Vary how multiple conditions are presented
                if random.random() < 0.3:  # Sometimes use "significant for" phrasing
                    conditions_text = "past medical history significant for " + ", ".join(conditions)
                elif random.random() < 0.5:  # Sometimes use "including" phrasing
                    conditions_text = "multiple medical conditions including " + ", ".join(conditions[:-1]) + " and " + conditions[-1]
                else:  # Standard comma-separated list
                    conditions_text = ", ".join(conditions[:-1]) + " and " + conditions[-1]
        
        # Generate more varied and realistic symptom descriptions
        symptoms = [
            "pain", "discomfort", "fatigue", "weakness", "dizziness", "nausea",
            "shortness of breath", "palpitations", "numbness", "tingling",
            "swelling", "rash", "itching", "cough", "congestion", "fever"
        ]
        symptom = random.choice(symptoms)
        
        # Add location specificity for certain symptoms
        if symptom in ["pain", "discomfort", "numbness", "tingling", "swelling", "rash", "itching"]:
            locations = [
                "chest", "abdominal", "back", "neck", "head", "arm", "leg",
                "shoulder", "knee", "hip", "ankle", "wrist", "elbow"
            ]
            symptom = f"{random.choice(locations)} {symptom}"
        
        # Generate more varied symptom descriptions
        intensities = ["mild", "moderate", "severe", "significant", "slight", "considerable"]
        patterns = ["constant", "intermittent", "waxing and waning", "episodic", "persistent", "recurring"]
        trends = ["worsening", "improving", "stable", "fluctuating", "progressively worsening"]
        
        symptom_descriptions = [
            f"{symptom} that is {random.choice(intensities)} and {random.choice(patterns)}",
            f"{random.choice(['new onset', 'acute', 'chronic', 'recurrent'])} {symptom}",
            f"{symptom} for {random.choice(['several days', 'about a week', f'{random.randint(1, 30)} days', 'several weeks', 'a few months'])}",
            f"{symptom} described as {random.choice(['sharp', 'dull', 'aching', 'burning', 'throbbing', 'shooting', 'cramping'])}",
            f"{symptom} that {random.choice(['began suddenly', 'developed gradually', 'started after exercise', 'occurs primarily in the morning', 'is worse at night'])}"
        ]
        symptom_description = random.choice(symptom_descriptions)
        
        # Generate more varied patient statements
        patient_statements = [
            f"the {symptom} is worse with {random.choice(['physical activity', 'prolonged sitting', 'standing', 'bending', 'lifting', 'eating', 'stress', 'cold weather', 'humidity'])}",
            f"they have tried {random.choice(['over-the-counter medications', 'rest', 'ice', 'heat', 'massage', 'stretching', 'elevation', 'compression'])} with {random.choice(['significant', 'some', 'minimal', 'temporary', 'little', 'no'])} relief",
            f"this is {random.choice(['similar to', 'different from', 'more severe than', 'less intense than'])} previous episodes",
            f"the symptoms {random.choice(['interfere with sleep', 'limit daily activities', 'affect work performance', 'have caused anxiety', 'have not affected daily function'])}",
            f"they {random.choice(['are concerned about', 'wonder if this could be related to', 'have a family history of', 'recently read about'])} {random.choice(conditions) if conditions else 'a serious condition'}"
        ]
        patient_statement = random.choice(patient_statements)
        
        # Generate more varied symptom changes
        symptom_changes = [
            f"{random.choice(['significant improvement', 'modest improvement', 'slight worsening', 'no appreciable change', 'fluctuating symptoms'])} since last visit",
            f"new symptom of {random.choice(symptoms)} that started {random.choice(['yesterday', 'last week', 'gradually over the past month', 'after starting new medication'])}",
            f"medication {random.choice(['has provided good relief', 'helps somewhat', 'is not helping adequately', 'causes side effects including ' + random.choice(['drowsiness', 'nausea', 'dizziness', 'constipation'])])}",
            f"{random.choice(['better control of', 'ongoing issues with', 'new concerns about'])} {random.choice(conditions) if conditions else 'their health'}"
        ]
        symptom_change = random.choice(symptom_changes)
        
        # Generate more varied symptom onset descriptions
        time_periods = ["days", "weeks", "months"]
        time_quantities = ["few", "couple", "several"]
        
        symptom_onsets = [
            f"{random.randint(1, 30)} days ago",
            f"about {random.randint(1, 11)} {random.choice(['weeks', 'months'])} ago",
            f"{random.choice(time_quantities)} {random.choice(time_periods)} ago",
            f"gradually over the past {random.choice(time_quantities)} {random.choice(time_periods)}",
            f"suddenly {random.choice(['yesterday', 'last night', 'this morning', 'while exercising', 'after eating'])}",
            f"after {random.choice(['starting new medication', 'a recent illness', 'a stressful event', 'physical exertion', 'exposure to allergens'])}"
        ]
        symptom_onset = random.choice(symptom_onsets)
        
        # Generate more varied symptom qualities
        associated_symptoms = [
            "nausea", "vomiting", "fever", "chills", "sweats", "fatigue",
            "loss of appetite", "weight loss", "insomnia", "anxiety",
            "headache", "dizziness", "blurred vision", "shortness of breath"
        ]
        
        exacerbating_factors = [
            "physical activity", "certain movements", "prolonged sitting",
            "standing", "stress", "certain foods", "alcohol", "caffeine",
            "weather changes", "lack of sleep", "emotional stress"
        ]
        
        alleviating_factors = [
            "rest", "medication", "position change", "ice", "heat",
            "massage", "stretching", "eating", "avoiding certain foods"
        ]
        
        symptom_qualities = [
            f"{random.choice(intensities)} and {random.choice(patterns)}",
            f"associated with {random.choice(associated_symptoms)}" + (f" and {random.choice(associated_symptoms)}" if random.random() < 0.3 else ""),
            f"exacerbated by {random.choice(exacerbating_factors)}" + (f" and {random.choice(exacerbating_factors)}" if random.random() < 0.3 else ""),
            f"relieved by {random.choice(alleviating_factors)}" + (f" and {random.choice(alleviating_factors)}" if random.random() < 0.3 else ""),
            f"rated as {random.randint(1, 10)}/10 in severity"
        ]
        symptom_quality = random.choice(symptom_qualities)
        
        # Replace placeholders in the template
        subjective = template.replace("{age}", str(age))
        subjective = subjective.replace("{gender}", gender)
        subjective = subjective.replace("{conditions}", conditions_text)
        subjective = subjective.replace("{reason}", chief_complaint)
        subjective = subjective.replace("{symptom_description}", symptom_description)
        subjective = subjective.replace("{patient_statement}", patient_statement)
        subjective = subjective.replace("{symptom_changes}", symptom_change)
        subjective = subjective.replace("{symptom_onset}", symptom_onset)
        subjective = subjective.replace("{symptom_quality}", symptom_quality)
        
        return subjective
    
    def _generate_objective(self, conditions: List[str]) -> str:
        """
        Generate the objective section of the note with enhanced variability and realism.
        Creates more diverse and realistic physical examination findings.
        """
        # Generate vital signs with more variability and condition-appropriate values
        vitals = []
        
        # Generate more realistic BP based on conditions
        has_hypertension = "Hypertension" in conditions
        has_hypotension = any(c for c in conditions if "hypotension" in c.lower())
        
        if has_hypertension:
            # Higher BP for hypertensive patients
            systolic = random.randint(130, 170)
            diastolic = random.randint(80, 100)
        elif has_hypotension:
            # Lower BP for hypotensive patients
            systolic = random.randint(80, 110)
            diastolic = random.randint(50, 70)
        else:
            # Normal range with some variability
            systolic = random.randint(110, 140)
            diastolic = random.randint(60, 90)
        
        vitals.append(self.vital_signs[0].format(systolic, diastolic))  # BP
        
        # Generate HR based on conditions
        has_tachycardia = any(c for c in conditions if "tachycardia" in c.lower() or "atrial fibrillation" in c.lower())
        has_bradycardia = any(c for c in conditions if "bradycardia" in c.lower())
        
        if has_tachycardia:
            hr = random.randint(90, 120)
        elif has_bradycardia:
            hr = random.randint(40, 60)
        else:
            hr = random.randint(60, 100)
        
        vitals.append(self.vital_signs[1].format(hr))  # HR
        
        # Generate RR based on conditions
        has_respiratory_issue = any(c for c in conditions if c in ["Asthma", "COPD", "Pneumonia", "Bronchitis"])
        
        if has_respiratory_issue:
            rr = random.randint(18, 28)
        else:
            rr = random.randint(12, 20)
        
        vitals.append(self.vital_signs[2].format(rr))  # RR
        
        # Generate temperature based on conditions
        has_fever = any(c for c in conditions if "fever" in c.lower() or "infection" in c.lower())
        
        if has_fever:
            temp = random.uniform(99.5, 102.5)
        else:
            temp = random.uniform(97.0, 99.5)
        
        vitals.append(self.vital_signs[3].format(temp))  # Temp
        
        # Generate O2 saturation based on conditions
        has_oxygen_issue = any(c for c in conditions if c in ["Asthma", "COPD", "Pneumonia", "Pulmonary Embolism"])
        
        if has_oxygen_issue:
            o2 = random.randint(88, 95)
        else:
            o2 = random.randint(95, 100)
        
        vitals.append(self.vital_signs[4].format(o2))  # O2
        
        # Add weight and height occasionally
        if random.random() < 0.7:
            weight = random.randint(120, 220)
            vitals.append(self.vital_signs[5].format(weight))  # Weight
            
            # If we add weight, usually add height too
            if random.random() < 0.9:
                height_ft = random.randint(5, 6)
                height_in = random.randint(0, 11)
                vitals.append(self.vital_signs[6].format(height_ft, height_in))  # Height
                
                # Calculate and add BMI if we have both weight and height
                height_inches = height_ft * 12 + height_in
                bmi = (weight / (height_inches ** 2)) * 703
                vitals.append(self.vital_signs[7].format(bmi))  # BMI
        
        # Add section headers with different styles
        vital_headers = [
            "Vital Signs:",
            "VITAL SIGNS:",
            "Vitals:",
            "VITALS:"
        ]
        
        vitals_text = random.choice(vital_headers) + "\n" + "\n".join(vitals)
        
        # Generate physical exam findings with more condition-specific abnormalities
        exam_findings = []
        
        # Map conditions to relevant body systems for more realistic findings
        condition_system_map = {
            "Hypertension": ["Cardiovascular"],
            "Heart Failure": ["Cardiovascular", "Respiratory"],
            "Atrial Fibrillation": ["Cardiovascular"],
            "Asthma": ["Respiratory"],
            "COPD": ["Respiratory"],
            "Pneumonia": ["Respiratory"],
            "GERD": ["Gastrointestinal"],
            "Peptic Ulcer": ["Gastrointestinal"],
            "Irritable Bowel Syndrome": ["Gastrointestinal"],
            "Osteoarthritis": ["Musculoskeletal"],
            "Rheumatoid Arthritis": ["Musculoskeletal"],
            "Back Pain": ["Musculoskeletal"],
            "Migraine": ["Neurological", "HEENT"],
            "Stroke": ["Neurological"],
            "Seizure Disorder": ["Neurological"],
            "Depression": ["Psychiatric"],
            "Anxiety": ["Psychiatric"],
            "Bipolar Disorder": ["Psychiatric"],
            "Eczema": ["Skin"],
            "Psoriasis": ["Skin"],
            "Hypothyroidism": ["HEENT"]
        }
        
        # Determine which systems should have abnormal findings based on conditions
        abnormal_systems = set()
        for condition in conditions:
            if condition in condition_system_map:
                abnormal_systems.update(condition_system_map[condition])
        
        # Add some randomness - not every related system will always be abnormal
        abnormal_systems = {system for system in abnormal_systems if random.random() < 0.7}
        
        # Add some randomness - sometimes unrelated systems might be abnormal
        for system_name in self.abnormal_findings.keys():
            if system_name not in abnormal_systems and random.random() < 0.1:
                abnormal_systems.add(system_name)
        
        # Generate findings for each system
        for system in self.physical_exam_findings:
            system_name = system.split(":")[0]
            
            if system_name in abnormal_systems and system_name in self.abnormal_findings:
                # For abnormal systems, sometimes include multiple findings
                if random.random() < 0.3 and len(self.abnormal_findings[system_name]) > 1:
                    findings = random.sample(self.abnormal_findings[system_name], 2)
                    finding = system.format(f"{findings[0]} and {findings[1]}")
                else:
                    finding = system.format(random.choice(self.abnormal_findings[system_name]))
            else:
                # More varied normal findings
                normal_findings_extended = self.normal_findings + [
                    "no abnormalities",
                    "normal on examination",
                    "without significant findings",
                    "appears normal",
                    "no concerning findings"
                ]
                finding = system.format(random.choice(normal_findings_extended))
            
            exam_findings.append(finding)
        
        # Add section headers with different styles
        exam_headers = [
            "Physical Examination:",
            "PHYSICAL EXAMINATION:",
            "Physical Exam:",
            "PHYSICAL EXAM:"
        ]
        
        exam_text = random.choice(exam_headers) + "\n" + "\n".join(exam_findings)
        
        # Sometimes add a general appearance section
        if random.random() < 0.7:
            general_appearances = [
                "Patient appears well-nourished and in no acute distress.",
                "Patient is alert and oriented to person, place, and time.",
                "Patient appears comfortable and in no apparent distress.",
                "Patient is well-developed and well-nourished.",
                "Patient appears stated age, alert and cooperative."
            ]
            general_text = "General: " + random.choice(general_appearances) + "\n\n"
            return f"{vitals_text}\n\n{general_text}{exam_text}"
        
        return f"{vitals_text}\n\n{exam_text}"
    
    def _generate_assessment(self, conditions: List[str]) -> str:
        """
        Generate the assessment section of the note with enhanced variability and realism.
        Creates more diverse and realistic clinical assessments.
        """
        if not conditions:
            healthy_assessments = [
                "No acute findings. Patient is healthy.",
                "Healthy adult with no significant medical concerns.",
                "Routine examination with normal findings.",
                "Wellness visit with no acute issues identified.",
                "Preventive health assessment with normal findings."
            ]
            return random.choice(healthy_assessments)
        
        if not self.templates.get("assessment"):
            # Create varied assessment formats if no templates are provided
            assessment_formats = [
                f"Assessment: {', '.join(conditions)}.",
                f"Impression: {', '.join(conditions)}.",
                f"Diagnoses: {', '.join(conditions)}.",
                f"Assessment/Plan: {', '.join(conditions)}."
            ]
            return random.choice(assessment_formats)
        
        template = random.choice(self.templates["assessment"])
        
        # Handle multiple conditions with different approaches
        if len(conditions) > 1 and random.random() < 0.4:
            # Sometimes create a numbered list of assessments for multiple conditions
            assessments = []
            for i, condition in enumerate(conditions, 1):
                # Generate a detailed assessment for each condition
                stability = random.choice([
                    f"{random.choice(['stable', 'improving', 'worsening', 'well-controlled', 'poorly controlled'])}",
                    f"{random.choice(['responding to', 'not responding adequately to'])} current treatment",
                    f"with {random.choice(['minimal', 'moderate', 'significant'])} symptoms"
                ])
                
                plan = random.choice([
                    f"Will {random.choice(['continue', 'adjust', 'optimize', 'discontinue'])} current management",
                    f"Recommend {random.choice(['follow-up in clinic', 'additional testing', 'specialist referral', 'medication adjustment'])}",
                    f"Consider {random.choice(['lifestyle modifications', 'closer monitoring', 'additional therapy', 'alternative treatment options'])}"
                ])
                
                assessments.append(f"{i}. {condition}: {stability}. {plan}.")
            
            return "\n".join(assessments)
        else:
            # Select a condition to focus on (or the only condition)
            diagnosis = random.choice(conditions)
            
            # Add clinical specificity to the diagnosis
            if random.random() < 0.3:
                specificity_terms = [
                    f"{random.choice(['acute', 'chronic', 'recurrent', 'persistent'])} {diagnosis}",
                    f"{diagnosis}, {random.choice(['newly diagnosed', 'long-standing', 'previously treated', 'with recent exacerbation'])}",
                    f"{diagnosis} {random.choice(['type 1', 'type 2', 'unspecified type', 'with complications', 'without complications'])}"
                ]
                diagnosis = random.choice(specificity_terms)
            
            # Generate more varied stability statements
            stability_statements = [
                f"Condition is {random.choice(['stable', 'improving', 'worsening', 'fluctuating', 'refractory to treatment'])}",
                f"Patient is {random.choice(['responding well to', 'showing partial response to', 'not responding to', 'experiencing side effects from'])} current treatment",
                f"Symptoms are {random.choice(['well-controlled', 'moderately controlled', 'poorly controlled', 'exacerbated by recent events'])}",
                f"Disease is {random.choice(['in remission', 'active but stable', 'progressing slowly', 'progressing rapidly', 'at risk of complications'])}",
                f"Current status is {random.choice(['better than previous visit', 'unchanged from previous visit', 'worse than previous visit', 'concerning for progression'])}"
            ]
            stability_statement = random.choice(stability_statements)
            
            # Generate more varied plan rationales
            plan_rationales = [
                f"Will {random.choice(['continue', 'adjust', 'optimize', 'discontinue', 'reassess'])} current treatment plan",
                f"Recommend {random.choice(['additional testing', 'specialist referral', 'medication adjustment', 'close follow-up', 'watchful waiting'])}",
                f"Patient would benefit from {random.choice(['lifestyle modifications', 'closer monitoring', 'additional therapy', 'patient education', 'support services'])}",
                f"Plan to {random.choice(['increase medication dosage', 'decrease medication dosage', 'add additional medication', 'switch to alternative therapy', 'order diagnostic testing'])}",
                f"Consider {random.choice(['preventive measures', 'screening for complications', 'alternative treatment options', 'complementary therapies', 'multidisciplinary approach'])}"
            ]
            plan_rationale = random.choice(plan_rationales)
            
            # Generate more varied severity assessments
            severities = [
                "mild", "moderate", "severe", "well-controlled", "poorly controlled",
                "mild to moderate", "moderate to severe", "minimally symptomatic",
                "significantly symptomatic", "in early stages", "in advanced stages",
                "with minimal functional impact", "with significant functional impact"
            ]
            severity = random.choice(severities)
            
            # Generate more varied complication risks
            complication_risks = [
                f"At {random.choice(['low', 'moderate', 'high', 'increased', 'significant'])} risk for complications",
                f"Monitor for {random.choice(['progression', 'side effects', 'complications', 'treatment failure', 'recurrence'])}",
                f"Prognosis is {random.choice(['excellent', 'good', 'fair', 'guarded', 'poor', 'uncertain'])}",
                f"Risk factors include {random.choice(['age', 'comorbidities', 'family history', 'lifestyle factors', 'medication interactions'])}",
                f"Potential complications include {random.choice(['organ damage', 'functional decline', 'secondary infections', 'treatment resistance', 'psychological impact'])}"
            ]
            complication_risk = random.choice(complication_risks)
            
            # Generate more varied diagnostic criteria
            diagnostic_criteria = [
                f"clinical presentation and {random.choice(['physical exam findings', 'laboratory results', 'imaging studies', 'patient history', 'response to treatment'])}",
                f"patient history and {random.choice(['symptom pattern', 'response to treatment', 'risk factors', 'family history', 'environmental exposures'])}",
                f"{random.choice(['consistent', 'classic', 'typical', 'pathognomonic', 'suggestive'])} signs and symptoms",
                f"diagnostic criteria including {random.choice(['laboratory abnormalities', 'imaging findings', 'clinical manifestations', 'disease progression', 'treatment response'])}",
                f"findings on {random.choice(['physical examination', 'laboratory testing', 'diagnostic imaging', 'specialized testing', 'clinical assessment'])}"
            ]
            diagnostic_criterion = random.choice(diagnostic_criteria)
        
        # Replace placeholders in the template
        assessment = template.replace("{diagnosis}", diagnosis)
        assessment = assessment.replace("{stability_statement}", stability_statement)
        assessment = assessment.replace("{plan_rationale}", plan_rationale)
        assessment = assessment.replace("{severity}", severity)
        assessment = assessment.replace("{complication_risk}", complication_risk)
        assessment = assessment.replace("{diagnostic_criteria}", diagnostic_criterion)
        
        return assessment
    
    def _generate_plan(self, conditions: List[str], medications: List[str]) -> str:
        """Generate the plan section of the note."""
        if not self.templates.get("plan"):
            # Generate a basic plan if no templates are available
            plan_items = []
            for _ in range(random.randint(2, 4)):
                plan_template = random.choice(self.plan_elements)
                
                if "{}" in plan_template:
                    if "medications" in plan_template and medications:
                        plan_items.append(plan_template.format(random.choice(medications)))
                    elif "weeks" in plan_template:
                        plan_items.append(plan_template.format(random.randint(1, 12)))
                    elif "laboratory tests" in plan_template:
                        lab_tests = ["CBC", "CMP", "lipid panel", "HbA1c", "thyroid panel"]
                        plan_items.append(plan_template.format(random.choice(lab_tests)))
                    elif "specialist" in plan_template:
                        specialists = ["cardiology", "endocrinology", "neurology", "gastroenterology", "rheumatology"]
                        plan_items.append(plan_template.format(random.choice(specialists)))
                    elif "imaging" in plan_template:
                        imaging = ["X-ray", "MRI", "CT scan", "ultrasound", "DEXA scan"]
                        plan_items.append(plan_template.format(random.choice(imaging)))
                    else:
                        plan_items.append(plan_template.format("appropriate"))
                else:
                    plan_items.append(plan_template)
            
            return "\n".join(plan_items)
        
        template = random.choice(self.templates["plan"])
        
        # Generate treatment plans
        treatment_plans = [
            f"Continue current management of {random.choice(conditions) if conditions else 'condition'}",
            f"Start {random.choice(['new medication', 'physical therapy', 'dietary changes'])}",
            f"Refer to {random.choice(['specialist', 'physical therapy', 'nutritionist'])}",
            f"Order {random.choice(['laboratory tests', 'imaging studies', 'diagnostic procedures'])}"
        ]
        treatment_plan = random.choice(treatment_plans)
        
        # Generate medication plans
        medication_plans = [
            f"Continue all current medications",
            f"Start {random.choice(['new medication', 'additional treatment'])}",
            f"Adjust dosage of {random.choice(medications) if medications else 'medication'}",
            f"Discontinue {random.choice(medications) if medications else 'medication'}"
        ]
        medication_plan = random.choice(medication_plans)
        
        # Generate follow-up plans
        follow_up_plans = [
            f"Follow up in {random.randint(1, 12)} {random.choice(['weeks', 'months'])}",
            f"Return to clinic if symptoms {random.choice(['worsen', 'persist', 'change'])}",
            f"Schedule follow-up after {random.choice(['completing treatment', 'diagnostic testing', 'specialist consultation'])}",
            f"No follow-up needed at this time"
        ]
        follow_up_plan = random.choice(follow_up_plans)
        
        # Generate monitoring plans
        monitoring_plans = [
            f"Monitor {random.choice(['symptoms', 'blood pressure', 'blood glucose', 'weight'])} at home",
            f"Return for repeat {random.choice(['laboratory testing', 'imaging', 'evaluation'])} in {random.randint(1, 12)} {random.choice(['weeks', 'months'])}",
            f"Contact office if {random.choice(['symptoms worsen', 'side effects occur', 'no improvement'])}"
        ]
        monitoring_plan = random.choice(monitoring_plans)
        
        # Generate diagnostic plans
        diagnostic_plans = [
            f"Order {random.choice(['CBC', 'CMP', 'lipid panel', 'HbA1c', 'thyroid panel'])}",
            f"Schedule {random.choice(['X-ray', 'MRI', 'CT scan', 'ultrasound', 'DEXA scan'])}",
            f"Refer for {random.choice(['stress test', 'sleep study', 'pulmonary function tests', 'endoscopy'])}"
        ]
        diagnostic_plan = random.choice(diagnostic_plans)
        
        # Generate timeframes
        timeframes = [
            f"{random.randint(1, 12)} {random.choice(['weeks', 'months'])}",
            "as needed",
            "after completing treatment",
            "once test results are available"
        ]
        timeframe = random.choice(timeframes)
        
        # Replace placeholders in the template
        plan = template.replace("{treatment_plan}", treatment_plan)
        plan = plan.replace("{medication_plan}", medication_plan)
        plan = plan.replace("{follow_up_plan}", follow_up_plan)
        plan = plan.replace("{monitoring_plan}", monitoring_plan)
        plan = plan.replace("{diagnostic_plan}", diagnostic_plan)
        plan = plan.replace("{timeframe}", timeframe)
        plan = plan.replace("{current_medications}", "current medications" if medications else "prescribed regimen")
        
        return plan
    
    def _generate_diagnosis_codes(self, conditions: List[str]) -> List[str]:
        """Generate mock diagnosis codes for the conditions."""
        if not conditions:
            return []
        
        # In a real implementation, this would map to actual ICD-10 codes
        # For this example, we'll generate mock codes
        codes = []
        for _ in range(min(len(conditions), 3)):  # Up to 3 codes
            letter = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"])
            number = random.randint(0, 99)
            decimal = random.randint(0, 9)
            codes.append(f"{letter}{number}.{decimal}")
        
        return codes
    
    def _generate_procedure_codes(self, procedures: List[str]) -> List[str]:
        """Generate mock procedure codes."""
        if not procedures:
            return []
        
        # In a real implementation, this would map to actual CPT codes
        # For this example, we'll generate mock codes
        codes = []
        for _ in range(min(len(procedures), 2)):  # Up to 2 codes
            code = random.randint(10000, 99999)
            codes.append(str(code))
        
        return codes