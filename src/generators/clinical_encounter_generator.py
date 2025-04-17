"""
Clinical encounter generator for the synthetic healthcare data generator.

This module generates synthetic clinical encounters and related entities based on
member and provider data.
"""

import json
import logging
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from faker import Faker

from src.generators.base_generator import BaseGenerator
from src.models.clinical import (
    ClinicalEncounter, EncounterParticipant, EncounterLocation, 
    EncounterDiagnosis, EncounterProcedure, ClinicalNote, 
    EncounterService, EncounterAssessment, EncounterMedication,
    EncounterTransition, ValidationResult,
    # Enums
    EncounterType, EncounterStatus, EncounterClass, EncounterPriority,
    AdmissionType, DischargeDisposition, ServiceType, ParticipantType,
    ProviderRole, LocationType, LocationStatus, DiagnosisType,
    ProcedureStatus, NoteType, NoteStatus, ServiceStatus,
    AssessmentType, MedicationRoute, MedicationStatus, TransitionType
)


class ClinicalEncounterGenerator(BaseGenerator):
    """Generator for synthetic clinical encounters and related entities."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the clinical encounter generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            self.faker.seed_instance(seed)
        
        # Load configuration
        self.encounter_config = self.config.get("clinical_config", {})
        
        # Default configuration if not provided
        self.default_config = {
            "encounter_count_per_member": {
                "min": 0,
                "max": 20,
                "mean": 5,
                "std_dev": 3
            },
            "encounter_type_distribution": {
                "Inpatient": 0.15,
                "Ambulatory": 0.45,
                "Emergency": 0.1,
                "Observation": 0.05,
                "Virtual": 0.2,
                "Home Health": 0.05
            },
            "encounter_status_distribution": {
                "Planned": 0.05,
                "Arrived": 0.05,
                "In-Progress": 0.1,
                "On-Leave": 0.01,
                "Finished": 0.75,
                "Cancelled": 0.04
            },
            "inpatient_length_of_stay": {
                "min": 1,
                "max": 30,
                "mean": 4.5,
                "std_dev": 3
            },
            "readmission_probability": 0.08,
            "transition_probability": 0.25,
            "participant_count": {
                "min": 1,
                "max": 10,
                "mean": 3,
                "std_dev": 2
            },
            "location_change_probability": 0.3,
            "diagnosis_count": {
                "min": 1,
                "max": 8,
                "mean": 2,
                "std_dev": 1
            },
            "procedure_count": {
                "min": 0,
                "max": 5,
                "mean": 1,
                "std_dev": 1
            },
            "service_count": {
                "min": 0,
                "max": 10,
                "mean": 3,
                "std_dev": 2
            },
            "assessment_count": {
                "min": 0,
                "max": 5,
                "mean": 2,
                "std_dev": 1
            },
            "medication_count": {
                "min": 0,
                "max": 8,
                "mean": 2,
                "std_dev": 2
            },
            "note_count": {
                "min": 0,
                "max": 5,
                "mean": 1,
                "std_dev": 1
            }
        }
        
        # Merge default config with provided config
        for key, value in self.default_config.items():
            if key not in self.encounter_config:
                self.encounter_config[key] = value
        
        # Common chief complaints by encounter type
        self.chief_complaints = {
            EncounterType.INPATIENT: [
                "Chest pain", "Shortness of breath", "Abdominal pain", "Fever",
                "Altered mental status", "Syncope", "Weakness", "Pneumonia",
                "Sepsis", "Heart failure exacerbation", "COPD exacerbation",
                "Gastrointestinal bleeding", "Stroke", "Diabetic ketoacidosis",
                "Cellulitis", "Acute kidney injury", "Pancreatitis"
            ],
            EncounterType.AMBULATORY: [
                "Annual wellness visit", "Medication refill", "Follow-up visit",
                "Hypertension management", "Diabetes management", "Preventive care",
                "Chronic disease management", "Skin lesion evaluation", "Joint pain",
                "Back pain", "Headache", "Fatigue", "Depression", "Anxiety",
                "Allergies", "Cough", "Rash", "Urinary symptoms"
            ],
            EncounterType.EMERGENCY: [
                "Chest pain", "Shortness of breath", "Abdominal pain", "Fever",
                "Trauma", "Laceration", "Fracture", "Head injury", "Seizure",
                "Severe headache", "Allergic reaction", "Overdose", "Intoxication",
                "Suicidal ideation", "Severe vomiting", "Severe diarrhea",
                "Eye injury", "Foreign body", "Burn"
            ],
            EncounterType.OBSERVATION: [
                "Chest pain", "Abdominal pain", "Syncope", "Transient ischemic attack",
                "Dehydration", "Mild head injury", "Asthma exacerbation", "Cellulitis",
                "Renal colic", "Vertigo", "Hyperemesis", "Mild pancreatitis"
            ],
            EncounterType.VIRTUAL: [
                "Medication refill", "Follow-up visit", "Minor illness",
                "Rash", "Cold symptoms", "Sinus symptoms", "Mild anxiety",
                "Depression follow-up", "Urinary symptoms", "Back pain",
                "Headache", "Insomnia", "Allergies", "Minor skin issues"
            ],
            EncounterType.HOME_HEALTH: [
                "Wound care", "IV therapy", "Physical therapy", "Post-surgical care",
                "Medication management", "Chronic disease monitoring", "Palliative care",
                "Rehabilitation", "Fall prevention", "Nutritional support"
            ]
        }
        
        # Common services by encounter type
        self.services = {
            EncounterType.INPATIENT: [
                {"code": "99221", "description": "Initial hospital care, low severity"},
                {"code": "99222", "description": "Initial hospital care, moderate severity"},
                {"code": "99223", "description": "Initial hospital care, high severity"},
                {"code": "99231", "description": "Subsequent hospital care, low severity"},
                {"code": "99232", "description": "Subsequent hospital care, moderate severity"},
                {"code": "99233", "description": "Subsequent hospital care, high severity"},
                {"code": "99238", "description": "Hospital discharge services, 30 minutes or less"},
                {"code": "99239", "description": "Hospital discharge services, more than 30 minutes"}
            ],
            EncounterType.AMBULATORY: [
                {"code": "99201", "description": "Office or other outpatient visit, new patient, problem-focused"},
                {"code": "99202", "description": "Office or other outpatient visit, new patient, expanded problem-focused"},
                {"code": "99203", "description": "Office or other outpatient visit, new patient, detailed"},
                {"code": "99204", "description": "Office or other outpatient visit, new patient, comprehensive, moderate complexity"},
                {"code": "99211", "description": "Office or other outpatient visit, established patient, minimal"},
                {"code": "99212", "description": "Office or other outpatient visit, established patient, problem-focused"},
                {"code": "99213", "description": "Office or other outpatient visit, established patient, expanded problem-focused"},
                {"code": "99214", "description": "Office or other outpatient visit, established patient, detailed"}
            ],
            EncounterType.EMERGENCY: [
                {"code": "99281", "description": "Emergency department visit, self-limited or minor problem"},
                {"code": "99282", "description": "Emergency department visit, low to moderate severity"},
                {"code": "99283", "description": "Emergency department visit, moderate severity"},
                {"code": "99284", "description": "Emergency department visit, high severity, urgent evaluation"},
                {"code": "99285", "description": "Emergency department visit, high severity, immediate significant threat to life"}
            ],
            EncounterType.OBSERVATION: [
                {"code": "99217", "description": "Observation care discharge services"},
                {"code": "99218", "description": "Initial observation care, low severity"},
                {"code": "99219", "description": "Initial observation care, moderate severity"},
                {"code": "99220", "description": "Initial observation care, high severity"},
                {"code": "99224", "description": "Subsequent observation care, low severity"},
                {"code": "99225", "description": "Subsequent observation care, moderate severity"},
                {"code": "99226", "description": "Subsequent observation care, high severity"}
            ],
            EncounterType.VIRTUAL: [
                {"code": "99421", "description": "Online digital E/M service, 5-10 minutes"},
                {"code": "99422", "description": "Online digital E/M service, 11-20 minutes"},
                {"code": "99423", "description": "Online digital E/M service, 21 or more minutes"},
                {"code": "99441", "description": "Telephone E/M service, 5-10 minutes"},
                {"code": "99442", "description": "Telephone E/M service, 11-20 minutes"},
                {"code": "99443", "description": "Telephone E/M service, 21-30 minutes"},
                {"code": "G2012", "description": "Brief check-in by physician or other qualified health care professional"}
            ],
            EncounterType.HOME_HEALTH: [
                {"code": "99341", "description": "Home visit, new patient, problem-focused"},
                {"code": "99342", "description": "Home visit, new patient, expanded problem-focused"},
                {"code": "99343", "description": "Home visit, new patient, detailed"},
                {"code": "99344", "description": "Home visit, new patient, comprehensive, moderate complexity"},
                {"code": "99347", "description": "Home visit, established patient, problem-focused"},
                {"code": "99348", "description": "Home visit, established patient, expanded problem-focused"},
                {"code": "99349", "description": "Home visit, established patient, detailed"},
                {"code": "99350", "description": "Home visit, established patient, comprehensive"}
            ]
        }
        
        # Common medications by encounter type
        self.medications = {
            EncounterType.INPATIENT: [
                {"id": "MED001", "name": "Ceftriaxone", "dose": "1g", "route": MedicationRoute.IV},
                {"id": "MED002", "name": "Vancomycin", "dose": "1g", "route": MedicationRoute.IV},
                {"id": "MED003", "name": "Piperacillin-Tazobactam", "dose": "4.5g", "route": MedicationRoute.IV},
                {"id": "MED004", "name": "Heparin", "dose": "5000 units", "route": MedicationRoute.SC},
                {"id": "MED005", "name": "Enoxaparin", "dose": "40mg", "route": MedicationRoute.SC},
                {"id": "MED006", "name": "Morphine", "dose": "4mg", "route": MedicationRoute.IV},
                {"id": "MED007", "name": "Hydromorphone", "dose": "1mg", "route": MedicationRoute.IV},
                {"id": "MED008", "name": "Furosemide", "dose": "40mg", "route": MedicationRoute.IV},
                {"id": "MED009", "name": "Metoprolol", "dose": "25mg", "route": MedicationRoute.ORAL},
                {"id": "MED010", "name": "Insulin Regular", "dose": "10 units", "route": MedicationRoute.SC}
            ],
            EncounterType.AMBULATORY: [
                {"id": "MED011", "name": "Lisinopril", "dose": "10mg", "route": MedicationRoute.ORAL},
                {"id": "MED012", "name": "Metformin", "dose": "500mg", "route": MedicationRoute.ORAL},
                {"id": "MED013", "name": "Atorvastatin", "dose": "20mg", "route": MedicationRoute.ORAL},
                {"id": "MED014", "name": "Levothyroxine", "dose": "50mcg", "route": MedicationRoute.ORAL},
                {"id": "MED015", "name": "Amlodipine", "dose": "5mg", "route": MedicationRoute.ORAL},
                {"id": "MED016", "name": "Sertraline", "dose": "50mg", "route": MedicationRoute.ORAL},
                {"id": "MED017", "name": "Albuterol", "dose": "2 puffs", "route": MedicationRoute.INHALED},
                {"id": "MED018", "name": "Fluticasone", "dose": "1 spray", "route": MedicationRoute.INHALED}
            ],
            EncounterType.EMERGENCY: [
                {"id": "MED019", "name": "Ketorolac", "dose": "30mg", "route": MedicationRoute.IV},
                {"id": "MED020", "name": "Ondansetron", "dose": "4mg", "route": MedicationRoute.IV},
                {"id": "MED021", "name": "Morphine", "dose": "4mg", "route": MedicationRoute.IV},
                {"id": "MED022", "name": "Ceftriaxone", "dose": "1g", "route": MedicationRoute.IV},
                {"id": "MED023", "name": "Methylprednisolone", "dose": "125mg", "route": MedicationRoute.IV},
                {"id": "MED024", "name": "Lorazepam", "dose": "1mg", "route": MedicationRoute.IV},
                {"id": "MED025", "name": "Diphenhydramine", "dose": "25mg", "route": MedicationRoute.IV}
            ],
            EncounterType.OBSERVATION: [
                {"id": "MED026", "name": "Ondansetron", "dose": "4mg", "route": MedicationRoute.IV},
                {"id": "MED027", "name": "Ketorolac", "dose": "15mg", "route": MedicationRoute.IV},
                {"id": "MED028", "name": "Normal Saline", "dose": "1000mL", "route": MedicationRoute.IV},
                {"id": "MED029", "name": "Pantoprazole", "dose": "40mg", "route": MedicationRoute.IV},
                {"id": "MED030", "name": "Ceftriaxone", "dose": "1g", "route": MedicationRoute.IV}
            ],
            EncounterType.VIRTUAL: [
                {"id": "MED031", "name": "Amoxicillin", "dose": "500mg", "route": MedicationRoute.ORAL},
                {"id": "MED032", "name": "Azithromycin", "dose": "250mg", "route": MedicationRoute.ORAL},
                {"id": "MED033", "name": "Prednisone", "dose": "20mg", "route": MedicationRoute.ORAL},
                {"id": "MED034", "name": "Ibuprofen", "dose": "600mg", "route": MedicationRoute.ORAL},
                {"id": "MED035", "name": "Acetaminophen", "dose": "500mg", "route": MedicationRoute.ORAL}
            ],
            EncounterType.HOME_HEALTH: [
                {"id": "MED036", "name": "Cephalexin", "dose": "500mg", "route": MedicationRoute.ORAL},
                {"id": "MED037", "name": "Warfarin", "dose": "5mg", "route": MedicationRoute.ORAL},
                {"id": "MED038", "name": "Furosemide", "dose": "40mg", "route": MedicationRoute.ORAL},
                {"id": "MED039", "name": "Insulin Glargine", "dose": "20 units", "route": MedicationRoute.SC},
                {"id": "MED040", "name": "Morphine Sulfate", "dose": "15mg", "route": MedicationRoute.ORAL}
            ]
        }
        
        # Common procedures by encounter type
        self.procedures = {
            EncounterType.INPATIENT: [
                {"code": "33533", "description": "Coronary artery bypass, using arterial graft"},
                {"code": "47562", "description": "Laparoscopic cholecystectomy"},
                {"code": "44950", "description": "Appendectomy"},
                {"code": "27447", "description": "Total knee arthroplasty"},
                {"code": "27130", "description": "Total hip arthroplasty"},
                {"code": "43239", "description": "Upper GI endoscopy, biopsy"},
                {"code": "45378", "description": "Colonoscopy, diagnostic"},
                {"code": "36415", "description": "Routine venipuncture"},
                {"code": "71045", "description": "X-ray, chest, single view"},
                {"code": "93306", "description": "Echocardiography, complete"}
            ],
            EncounterType.AMBULATORY: [
                {"code": "99213", "description": "Office/outpatient visit, established patient"},
                {"code": "20610", "description": "Arthrocentesis, major joint"},
                {"code": "29125", "description": "Application of short arm splint"},
                {"code": "11042", "description": "Debridement, subcutaneous tissue"},
                {"code": "17000", "description": "Destruction of premalignant lesion"},
                {"code": "36415", "description": "Routine venipuncture"},
                {"code": "71046", "description": "X-ray, chest, 2 views"},
                {"code": "93000", "description": "Electrocardiogram, complete"}
            ],
            EncounterType.EMERGENCY: [
                {"code": "31500", "description": "Endotracheal intubation"},
                {"code": "12001", "description": "Simple suture, 2.5 cm or less"},
                {"code": "29125", "description": "Application of short arm splint"},
                {"code": "36415", "description": "Routine venipuncture"},
                {"code": "71045", "description": "X-ray, chest, single view"},
                {"code": "70450", "description": "CT scan, head/brain, without contrast"},
                {"code": "43752", "description": "Nasogastric tube placement"},
                {"code": "96360", "description": "IV infusion, hydration, initial"}
            ],
            EncounterType.OBSERVATION: [
                {"code": "36415", "description": "Routine venipuncture"},
                {"code": "71046", "description": "X-ray, chest, 2 views"},
                {"code": "93005", "description": "Electrocardiogram, tracing only"},
                {"code": "96360", "description": "IV infusion, hydration, initial"},
                {"code": "96361", "description": "IV infusion, hydration, additional hour"},
                {"code": "96374", "description": "IV push, single or initial substance/drug"}
            ],
            EncounterType.VIRTUAL: [
                {"code": "99421", "description": "Online digital E/M service, 5-10 minutes"},
                {"code": "99422", "description": "Online digital E/M service, 11-20 minutes"},
                {"code": "99423", "description": "Online digital E/M service, 21+ minutes"}
            ],
            EncounterType.HOME_HEALTH: [
                {"code": "99347", "description": "Home visit, established patient"},
                {"code": "99348", "description": "Home visit, established patient, moderate severity"},
                {"code": "36415", "description": "Routine venipuncture"},
                {"code": "97110", "description": "Therapeutic exercises"},
                {"code": "97530", "description": "Therapeutic activities"},
                {"code": "97112", "description": "Neuromuscular reeducation"}
            ]
        }
        
        # Common diagnoses by encounter type
        self.diagnoses = {
            EncounterType.INPATIENT: [
                {"code": "I21.3", "description": "ST elevation (STEMI) myocardial infarction of unspecified site"},
                {"code": "J18.9", "description": "Pneumonia, unspecified organism"},
                {"code": "J44.1", "description": "Chronic obstructive pulmonary disease with (acute) exacerbation"},
                {"code": "K92.2", "description": "Gastrointestinal hemorrhage, unspecified"},
                {"code": "N17.9", "description": "Acute kidney failure, unspecified"},
                {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
                {"code": "I50.9", "description": "Heart failure, unspecified"},
                {"code": "K85.9", "description": "Acute pancreatitis, unspecified"},
                {"code": "A41.9", "description": "Sepsis, unspecified organism"},
                {"code": "I63.9", "description": "Cerebral infarction, unspecified"}
            ],
            EncounterType.AMBULATORY: [
                {"code": "I10", "description": "Essential (primary) hypertension"},
                {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
                {"code": "E78.5", "description": "Hyperlipidemia, unspecified"},
                {"code": "M54.5", "description": "Low back pain"},
                {"code": "J45.909", "description": "Unspecified asthma, uncomplicated"},
                {"code": "F41.9", "description": "Anxiety disorder, unspecified"},
                {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified"},
                {"code": "M19.90", "description": "Unspecified osteoarthritis, unspecified site"},
                {"code": "R53.83", "description": "Other fatigue"},
                {"code": "Z00.00", "description": "Encounter for general adult medical examination without abnormal findings"}
            ],
            EncounterType.EMERGENCY: [
                {"code": "R07.9", "description": "Chest pain, unspecified"},
                {"code": "R10.9", "description": "Unspecified abdominal pain"},
                {"code": "S06.0X0A", "description": "Concussion without loss of consciousness, initial encounter"},
                {"code": "R50.9", "description": "Fever, unspecified"},
                {"code": "J06.9", "description": "Acute upper respiratory infection, unspecified"},
                {"code": "S61.419A", "description": "Laceration with foreign body of unspecified hand, initial encounter"},
                {"code": "R11.2", "description": "Nausea with vomiting, unspecified"},
                {"code": "R42", "description": "Dizziness and giddiness"},
                {"code": "S93.401A", "description": "Sprain of unspecified ankle, initial encounter"},
                {"code": "T14.90XA", "description": "Injury, unspecified, initial encounter"}
            ],
            EncounterType.OBSERVATION: [
                {"code": "R07.9", "description": "Chest pain, unspecified"},
                {"code": "R55", "description": "Syncope and collapse"},
                {"code": "R10.9", "description": "Unspecified abdominal pain"},
                {"code": "R42", "description": "Dizziness and giddiness"},
                {"code": "G45.9", "description": "Transient cerebral ischemic attack, unspecified"},
                {"code": "R11.2", "description": "Nausea with vomiting, unspecified"},
                {"code": "J45.901", "description": "Unspecified asthma with (acute) exacerbation"},
                {"code": "N23", "description": "Unspecified renal colic"},
                {"code": "L03.90", "description": "Cellulitis, unspecified"}
            ],
            EncounterType.VIRTUAL: [
                {"code": "J06.9", "description": "Acute upper respiratory infection, unspecified"},
                {"code": "J01.90", "description": "Acute sinusitis, unspecified"},
                {"code": "L30.9", "description": "Dermatitis, unspecified"},
                {"code": "F41.9", "description": "Anxiety disorder, unspecified"},
                {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified"},
                {"code": "M54.5", "description": "Low back pain"},
                {"code": "R51", "description": "Headache"},
                {"code": "G47.00", "description": "Insomnia, unspecified"},
                {"code": "N39.0", "description": "Urinary tract infection, site not specified"}
            ],
            EncounterType.HOME_HEALTH: [
                {"code": "I50.9", "description": "Heart failure, unspecified"},
                {"code": "I10", "description": "Essential (primary) hypertension"},
                {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
                {"code": "Z48.89", "description": "Encounter for other specified surgical aftercare"},
                {"code": "Z51.89", "description": "Encounter for other specified aftercare"},
                {"code": "M19.90", "description": "Unspecified osteoarthritis, unspecified site"},
                {"code": "M54.5", "description": "Low back pain"},
                {"code": "Z74.09", "description": "Other reduced mobility"},
                {"code": "Z74.1", "description": "Need for assistance with personal care"}
            ]
        }
        
        # Common assessment types and results
        self.assessments = {
            AssessmentType.VITAL_SIGNS: {
                "Blood Pressure": lambda: f"{random.randint(90, 180)}/{random.randint(60, 110)} mmHg",
                "Heart Rate": lambda: f"{random.randint(60, 120)} bpm",
                "Respiratory Rate": lambda: f"{random.randint(12, 24)} breaths/min",
                "Temperature": lambda: f"{round(random.uniform(97.0, 101.0), 1)}°F",
                "Oxygen Saturation": lambda: f"{random.randint(88, 100)}%",
                "Weight": lambda: f"{random.randint(110, 250)} lbs",
                "Height": lambda: f"{random.randint(60, 75)} inches",
                "BMI": lambda: f"{round(random.uniform(18.5, 35.0), 1)} kg/m²"
            },
            AssessmentType.PAIN: {
                "Pain Score": lambda: f"{random.randint(0, 10)}/10",
                "Pain Location": lambda: random.choice(["Head", "Neck", "Chest", "Abdomen", "Back", "Extremities"]),
                "Pain Quality": lambda: random.choice(["Sharp", "Dull", "Aching", "Burning", "Throbbing", "Stabbing"]),
                "Pain Duration": lambda: random.choice(["Acute", "Chronic", "Intermittent", "Constant"])
            },
            AssessmentType.FUNCTIONAL_STATUS: {
                "Mobility": lambda: random.choice(["Independent", "Requires assistance", "Dependent", "Bed-bound"]),
                "Activities of Daily Living": lambda: random.choice(["Independent", "Requires assistance", "Dependent"]),
                "Fall Risk": lambda: random.choice(["Low", "Moderate", "High"]),
                "Cognitive Status": lambda: random.choice(["Alert and oriented", "Confused", "Disoriented", "Unresponsive"])
            },
            AssessmentType.MENTAL_STATUS: {
                "Mood": lambda: random.choice(["Euthymic", "Depressed", "Anxious", "Irritable", "Labile"]),
                "Affect": lambda: random.choice(["Full", "Restricted", "Blunted", "Flat"]),
                "Thought Process": lambda: random.choice(["Linear", "Tangential", "Circumstantial", "Disorganized"]),
                "Suicidal Ideation": lambda: random.choice(["None", "Passive", "Active without plan", "Active with plan"])
            },
            AssessmentType.RISK_ASSESSMENT: {
                "Pressure Ulcer Risk": lambda: random.choice(["Low", "Moderate", "High"]),
                "VTE Risk": lambda: random.choice(["Low", "Moderate", "High"]),
                "Readmission Risk": lambda: random.choice(["Low", "Moderate", "High"]),
                "Malnutrition Risk": lambda: random.choice(["Low", "Moderate", "High"])
            }
        }
    
    def generate(self, members: List[Dict], providers: List[Dict], count: Optional[int] = None) -> List[Dict]:
        """
        Generate synthetic clinical encounters based on member and provider data.
        
        Args:
            members: List of member dictionaries to generate encounters for.
            providers: List of provider dictionaries to use as participants.
            count: Optional number of encounters to generate. If not provided,
                   will generate based on config settings.
                   
        Returns:
            List of generated clinical encounters as dictionaries.
        """
        if not members:
            self.logger.warning("No members provided for clinical encounter generation")
            return []
        
        if not providers:
            self.logger.warning("No providers provided for clinical encounter generation")
            return []
        
        encounters = []
        
        # Generate encounters for each member
        for member in members:
            # Determine how many encounters to generate for this member
            encounter_count_config = self.encounter_config.get("encounter_count_per_member", {"min": 0, "max": 5})
            
            # Use normal distribution if mean and std_dev are provided
            if "mean" in encounter_count_config and "std_dev" in encounter_count_config:
                num_encounters = int(np.random.normal(
                    encounter_count_config["mean"],
                    encounter_count_config["std_dev"]
                ))
                # Ensure within min/max bounds
                num_encounters = max(encounter_count_config.get("min", 0),
                                    min(encounter_count_config.get("max", 10), num_encounters))
            else:
                # Otherwise use uniform distribution
                num_encounters = random.randint(
                    encounter_count_config.get("min", 0),
                    encounter_count_config.get("max", 5)
                )
            
            # Generate encounters for this member
            member_encounters = self._generate_encounters_for_member(member, providers, num_encounters)
            encounters.extend(member_encounters)
        
        # If count is specified, randomly select that many encounters
        if count is not None and count < len(encounters):
            encounters = random.sample(encounters, count)
        
        return encounters
    
    def _select_weighted_option(self, options: Dict[str, float]) -> str:
        """
        Select an option based on weighted probabilities.
        
        Args:
            options: Dictionary mapping options to their probabilities.
            
        Returns:
            Selected option.
        """
        options_list = list(options.keys())
        weights = list(options.values())
        
        # Normalize weights if they don't sum to 1
        weight_sum = sum(weights)
        if weight_sum != 1.0:
            weights = [w / weight_sum for w in weights]
        
        return random.choices(options_list, weights=weights, k=1)[0]
    
    def _get_encounter_class(self, encounter_type: EncounterType) -> EncounterClass:
        """
        Get the appropriate encounter class based on encounter type.
        
        Args:
            encounter_type: Type of encounter.
            
        Returns:
            Appropriate encounter class.
        """
        type_to_class = {
            EncounterType.INPATIENT: EncounterClass.INPATIENT,
            EncounterType.AMBULATORY: EncounterClass.AMBULATORY,
            EncounterType.EMERGENCY: EncounterClass.EMERGENCY,
            EncounterType.OBSERVATION: EncounterClass.INPATIENT,  # Observation is typically inpatient class
            EncounterType.VIRTUAL: EncounterClass.VIRTUAL,
            EncounterType.HOME_HEALTH: EncounterClass.HOME
        }
        
        return type_to_class.get(encounter_type, EncounterClass.OTHER)
    
    def _get_encounter_priority(self, encounter_type: EncounterType) -> Optional[EncounterPriority]:
        """
        Get the appropriate encounter priority based on encounter type.
        
        Args:
            encounter_type: Type of encounter.
            
        Returns:
            Appropriate encounter priority, or None if not applicable.
        """
        # Default priorities by encounter type
        type_to_priority = {
            EncounterType.INPATIENT: [EncounterPriority.ELECTIVE, EncounterPriority.URGENT, EncounterPriority.EMERGENCY],
            EncounterType.AMBULATORY: [EncounterPriority.ROUTINE, EncounterPriority.URGENT],
            EncounterType.EMERGENCY: [EncounterPriority.URGENT, EncounterPriority.EMERGENCY],
            EncounterType.OBSERVATION: [EncounterPriority.URGENT, EncounterPriority.EMERGENCY],
            EncounterType.VIRTUAL: [EncounterPriority.ROUTINE],
            EncounterType.HOME_HEALTH: [EncounterPriority.ROUTINE]
        }
        
        priorities = type_to_priority.get(encounter_type, [EncounterPriority.ROUTINE])
        return random.choice(priorities)
    
    def _generate_participants(self, encounter_id: str, member_id: str, providers: List[Dict]) -> List[Dict]:
        """
        Generate participants for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            member_id: ID of the member (patient).
            providers: List of provider dictionaries.
            
        Returns:
            List of participant dictionaries.
        """
        participants = []
        
        # Always add the member as a patient participant
        patient_participant = {
            "id": f"PART{uuid.uuid4().hex[:8]}",
            "encounter_id": encounter_id,
            "participant_type": ParticipantType.PATIENT.value,
            "participant_id": member_id,
            "role": None,
            "start_datetime": None,  # Will be set to encounter start time
            "end_datetime": None,    # Will be set to encounter end time
            "primary": True
        }
        participants.append(patient_participant)
        
        # Determine how many provider participants to add
        participant_count_config = self.encounter_config.get("participant_count", {"min": 1, "max": 5})
        provider_count = random.randint(
            participant_count_config.get("min", 1) - 1,  # -1 because we already added the patient
            participant_count_config.get("max", 5) - 1
        )
        
        # Add provider participants
        if providers and provider_count > 0:
            # Select random providers
            selected_providers = random.sample(providers, min(provider_count, len(providers)))
            
            for i, provider in enumerate(selected_providers):
                # Determine provider role based on specialty if available
                provider_role = None
                if "specialty" in provider:
                    provider_role = self._map_specialty_to_role(provider["specialty"])
                else:
                    provider_role = random.choice(list(ProviderRole))
                
                provider_participant = {
                    "id": f"PART{uuid.uuid4().hex[:8]}",
                    "encounter_id": encounter_id,
                    "participant_type": ParticipantType.PROVIDER.value,
                    "participant_id": provider["id"],
                    "role": provider_role.value,
                    "start_datetime": None,  # Will be set to encounter start time
                    "end_datetime": None,    # Will be set to encounter end time
                    "primary": i == 0  # First provider is primary
                }
                participants.append(provider_participant)
        
        return participants
    
    def _map_specialty_to_role(self, specialty: str) -> ProviderRole:
        """
        Map provider specialty to a provider role.
        
        Args:
            specialty: Provider specialty.
            
        Returns:
            Appropriate provider role.
        """
        specialty_to_role = {
            "Internal Medicine": ProviderRole.ATTENDING,
            "Family Medicine": ProviderRole.PCP,
            "Emergency Medicine": ProviderRole.ATTENDING,
            "Surgery": ProviderRole.SURGEON,
            "Anesthesiology": ProviderRole.ANESTHESIOLOGIST,
            "Radiology": ProviderRole.RADIOLOGIST,
            "Pathology": ProviderRole.PATHOLOGIST,
            "Cardiology": ProviderRole.CONSULTING,
            "Neurology": ProviderRole.CONSULTING,
            "Orthopedics": ProviderRole.SURGEON,
            "Psychiatry": ProviderRole.CONSULTING,
            "Pediatrics": ProviderRole.ATTENDING,
            "Obstetrics and Gynecology": ProviderRole.ATTENDING,
            "Dermatology": ProviderRole.CONSULTING,
            "Ophthalmology": ProviderRole.CONSULTING,
            "Otolaryngology": ProviderRole.CONSULTING,
            "Urology": ProviderRole.CONSULTING,
            "Nephrology": ProviderRole.CONSULTING,
            "Endocrinology": ProviderRole.CONSULTING,
            "Gastroenterology": ProviderRole.CONSULTING,
            "Pulmonology": ProviderRole.CONSULTING,
            "Rheumatology": ProviderRole.CONSULTING,
            "Infectious Disease": ProviderRole.CONSULTING,
            "Hematology/Oncology": ProviderRole.CONSULTING,
            "Physical Therapy": ProviderRole.THERAPIST,
            "Occupational Therapy": ProviderRole.THERAPIST,
            "Speech Therapy": ProviderRole.THERAPIST,
            "Nursing": ProviderRole.NURSE
        }
        
        return specialty_to_role.get(specialty, ProviderRole.OTHER)
    
    def _generate_locations(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate locations for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of location dictionaries.
        """
        locations = []
        
        # Determine location type based on encounter type
        location_type = self._get_location_type(encounter_type)
        
        # Generate a primary location
        primary_location = {
            "id": f"LOC{uuid.uuid4().hex[:8]}",
            "encounter_id": encounter_id,
            "facility_id": f"FAC{random.randint(1000, 9999)}",
            "department_id": f"DEPT{random.randint(100, 999)}",
            "location_type": location_type.value,
            "start_datetime": None,  # Will be set to encounter start time
            "end_datetime": None,    # Will be set to encounter end time
            "status": LocationStatus.ACTIVE.value,
            "bed_id": f"BED{random.randint(100, 999)}" if encounter_type == EncounterType.INPATIENT else None
        }
        locations.append(primary_location)
        
        # For inpatient encounters, potentially add location changes
        if encounter_type == EncounterType.INPATIENT:
            location_change_probability = self.encounter_config.get("location_change_probability", 0.3)
            
            # Add additional locations with some probability
            while random.random() < location_change_probability and len(locations) < 3:
                # Choose a different location type
                new_location_type = random.choice([
                    LocationType.ICU, LocationType.WARD, LocationType.OPERATING_ROOM,
                    LocationType.RADIOLOGY, LocationType.LABORATORY
                ])
                
                additional_location = {
                    "id": f"LOC{uuid.uuid4().hex[:8]}",
                    "encounter_id": encounter_id,
                    "facility_id": primary_location["facility_id"],  # Same facility
                    "department_id": f"DEPT{random.randint(100, 999)}",  # Different department
                    "location_type": new_location_type.value,
                    "start_datetime": None,  # Will be calculated based on encounter timeline
                    "end_datetime": None,    # Will be calculated based on encounter timeline
                    "status": LocationStatus.ACTIVE.value,
                    "bed_id": f"BED{random.randint(100, 999)}" if new_location_type in [LocationType.ICU, LocationType.WARD] else None
                }
                locations.append(additional_location)
        
        return locations
    
    def _get_location_type(self, encounter_type: EncounterType) -> LocationType:
        """
        Get the appropriate location type based on encounter type.
        
        Args:
            encounter_type: Type of encounter.
            
        Returns:
            Appropriate location type.
        """
        type_to_location = {
            EncounterType.INPATIENT: LocationType.WARD,
            EncounterType.AMBULATORY: LocationType.CLINIC,
            EncounterType.EMERGENCY: LocationType.ER,
            EncounterType.OBSERVATION: LocationType.WARD,
            EncounterType.VIRTUAL: LocationType.OTHER,
            EncounterType.HOME_HEALTH: LocationType.OTHER
        }
        
        return type_to_location.get(encounter_type, LocationType.OTHER)
    
    def _generate_diagnoses(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate diagnoses for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of diagnosis dictionaries.
        """
        diagnoses = []
        
        # Determine how many diagnoses to generate
        diagnosis_count_config = self.encounter_config.get("diagnosis_count", {"min": 1, "max": 5})
        diagnosis_count = random.randint(
            diagnosis_count_config.get("min", 1),
            diagnosis_count_config.get("max", 5)
        )
        
        # Get diagnoses for this encounter type
        encounter_diagnoses = self.diagnoses.get(encounter_type, [])
        if not encounter_diagnoses:
            # Use ambulatory diagnoses as fallback
            encounter_diagnoses = self.diagnoses.get(EncounterType.AMBULATORY, [])
        
        # Select random diagnoses
        selected_diagnoses = random.sample(
            encounter_diagnoses,
            min(diagnosis_count, len(encounter_diagnoses))
        )
        
        # Determine diagnosis types based on encounter type
        diagnosis_types = self._get_diagnosis_types(encounter_type)
        
        for i, diagnosis in enumerate(selected_diagnoses):
            # Select diagnosis type
            if i == 0 and encounter_type == EncounterType.INPATIENT:
                # First diagnosis for inpatient is principal
                diagnosis_type = DiagnosisType.PRINCIPAL
            else:
                diagnosis_type = random.choice(diagnosis_types)
            
            # Create diagnosis object
            diagnosis_obj = {
                "id": f"DIAG{uuid.uuid4().hex[:8]}",
                "encounter_id": encounter_id,
                "diagnosis_code": diagnosis["code"],
                "diagnosis_description": diagnosis["description"],
                "condition_id": f"COND{random.randint(10000, 99999)}",
                "diagnosis_type": diagnosis_type.value,
                "present_on_admission": random.random() < 0.8,  # 80% chance of being present on admission
                "rank": i + 1,
                "provider_id": None  # Will be set to a provider participant
            }
            diagnoses.append(diagnosis_obj)
        
        return diagnoses
    
    def _get_diagnosis_types(self, encounter_type: EncounterType) -> List[DiagnosisType]:
        """
        Get appropriate diagnosis types based on encounter type.
        
        Args:
            encounter_type: Type of encounter.
            
        Returns:
            List of appropriate diagnosis types.
        """
        if encounter_type == EncounterType.INPATIENT:
            return [DiagnosisType.PRINCIPAL, DiagnosisType.SECONDARY, DiagnosisType.ADMITTING, DiagnosisType.DISCHARGE]
        elif encounter_type == EncounterType.EMERGENCY:
            return [DiagnosisType.PRINCIPAL, DiagnosisType.SECONDARY]
        else:
            return [DiagnosisType.PRINCIPAL, DiagnosisType.SECONDARY, DiagnosisType.OTHER]
    
    def _generate_procedures(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate procedures for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of procedure dictionaries.
        """
        procedures = []
        
        # Determine how many procedures to generate
        procedure_count_config = self.encounter_config.get("procedure_count", {"min": 0, "max": 3})
        procedure_count = random.randint(
            procedure_count_config.get("min", 0),
            procedure_count_config.get("max", 3)
        )
        
        # Get procedures for this encounter type
        encounter_procedures = self.procedures.get(encounter_type, [])
        if not encounter_procedures:
            # Use ambulatory procedures as fallback
            encounter_procedures = self.procedures.get(EncounterType.AMBULATORY, [])
        
        # Select random procedures
        if procedure_count > 0 and encounter_procedures:
            selected_procedures = random.sample(
                encounter_procedures,
                min(procedure_count, len(encounter_procedures))
            )
            
            for i, procedure in enumerate(selected_procedures):
                # Create procedure object
                procedure_obj = {
                    "id": f"PROC{uuid.uuid4().hex[:8]}",
                    "encounter_id": encounter_id,
                    "procedure_code": procedure["code"],
                    "procedure_description": procedure["description"],
                    "procedure_id": f"P{random.randint(10000, 99999)}",
                    "datetime": None,  # Will be set based on encounter timeline
                    "duration_minutes": random.randint(15, 240),  # 15 minutes to 4 hours
                    "provider_id": None,  # Will be set to a provider participant
                    "location_id": None,  # Will be set to a location
                    "status": ProcedureStatus.COMPLETED.value,
                    "primary_procedure": i == 0  # First procedure is primary
                }
                procedures.append(procedure_obj)
        
        return procedures
    
    def _generate_notes(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate clinical notes for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of note dictionaries.
        """
        notes = []
        
        # Determine how many notes to generate
        note_count_config = self.encounter_config.get("note_count", {"min": 0, "max": 3})
        note_count = random.randint(
            note_count_config.get("min", 0),
            note_count_config.get("max", 3)
        )
        
        # Determine appropriate note types based on encounter type
        note_types = self._get_note_types(encounter_type)
        
        for i in range(note_count):
            # Select note type
            note_type = random.choice(note_types)
            
            # Create note object
            note_obj = {
                "id": f"NOTE{uuid.uuid4().hex[:8]}",
                "encounter_id": encounter_id,
                "note_type": note_type.value,
                "author_id": None,  # Will be set to a provider participant
                "datetime": None,  # Will be set based on encounter timeline
                "content": f"This is a {note_type.value} for encounter {encounter_id}.",  # Placeholder content
                "status": NoteStatus.FINAL.value,
                "signed": True,
                "signed_datetime": None  # Will be set based on encounter timeline
            }
            notes.append(note_obj)
        
        return notes
    
    def _get_note_types(self, encounter_type: EncounterType) -> List[NoteType]:
        """
        Get appropriate note types based on encounter type.
        
        Args:
            encounter_type: Type of encounter.
            
        Returns:
            List of appropriate note types.
        """
        if encounter_type == EncounterType.INPATIENT:
            return [NoteType.H_AND_P, NoteType.PROGRESS_NOTE, NoteType.DISCHARGE_SUMMARY, NoteType.CONSULTATION]
        elif encounter_type == EncounterType.EMERGENCY:
            return [NoteType.PROGRESS_NOTE, NoteType.PROCEDURE_NOTE]
        elif encounter_type == EncounterType.AMBULATORY:
            return [NoteType.PROGRESS_NOTE, NoteType.PROCEDURE_NOTE]
        elif encounter_type == EncounterType.OBSERVATION:
            return [NoteType.PROGRESS_NOTE, NoteType.DISCHARGE_SUMMARY]
        elif encounter_type == EncounterType.VIRTUAL:
            return [NoteType.PROGRESS_NOTE]
        elif encounter_type == EncounterType.HOME_HEALTH:
            return [NoteType.PROGRESS_NOTE, NoteType.NURSING_NOTE]
        else:
            # Default case for any other encounter types
            return [NoteType.PROGRESS_NOTE]
    
    def _generate_services(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate services for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of service dictionaries.
        """
        services = []
        
        # Determine how many services to generate
        service_count_config = self.encounter_config.get("service_count", {"min": 0, "max": 5})
        service_count = random.randint(
            service_count_config.get("min", 0),
            service_count_config.get("max", 5)
        )
        
        # Get services for this encounter type
        encounter_services = self.services.get(encounter_type, [])
        if not encounter_services:
            # Use ambulatory services as fallback
            encounter_services = self.services.get(EncounterType.AMBULATORY, [])
        
        # Select random services
        if service_count > 0 and encounter_services:
            selected_services = random.sample(
                encounter_services,
                min(service_count, len(encounter_services))
            )
            
            for service in selected_services:
                # Create service object
                service_obj = {
                    "id": f"SVC{uuid.uuid4().hex[:8]}",
                    "encounter_id": encounter_id,
                    "service_code": service["code"],
                    "service_description": service["description"],
                    "service_id": f"S{random.randint(10000, 99999)}",
                    "provider_id": None,  # Will be set to a provider participant
                    "datetime": None,  # Will be set based on encounter timeline
                    "quantity": random.randint(1, 3),
                    "status": ServiceStatus.COMPLETED.value
                }
                services.append(service_obj)
        
        return services
    
    def _generate_assessments(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate assessments for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of assessment dictionaries.
        """
        assessments = []
        
        # Determine how many assessments to generate
        assessment_count_config = self.encounter_config.get("assessment_count", {"min": 0, "max": 3})
        assessment_count = random.randint(
            assessment_count_config.get("min", 0),
            assessment_count_config.get("max", 3)
        )
        
        # Always include vital signs for non-virtual encounters
        assessment_types = list(self.assessments.keys())
        if encounter_type != EncounterType.VIRTUAL:
            vital_signs_assessment = self._create_assessment(
                encounter_id,
                AssessmentType.VITAL_SIGNS
            )
            assessments.append(vital_signs_assessment)
            
            # Remove vital signs from the list of possible assessments
            if AssessmentType.VITAL_SIGNS in assessment_types:
                assessment_types.remove(AssessmentType.VITAL_SIGNS)
        
        # Add additional assessments
        for i in range(min(assessment_count, len(assessment_types))):
            assessment_type = random.choice(assessment_types)
            assessment = self._create_assessment(encounter_id, assessment_type)
            assessments.append(assessment)
            
            # Remove this assessment type from the list to avoid duplicates
            assessment_types.remove(assessment_type)
        
        return assessments
    
    def _create_assessment(self, encounter_id: str, assessment_type: AssessmentType) -> Dict:
        """
        Create an assessment of the specified type.
        
        Args:
            encounter_id: ID of the encounter.
            assessment_type: Type of assessment to create.
            
        Returns:
            Assessment dictionary.
        """
        # Get the assessment template for this type
        assessment_template = self.assessments.get(assessment_type, {})
        
        # Generate result data
        result = {}
        for key, value_generator in assessment_template.items():
            result[key] = value_generator()
        
        # Create assessment object
        assessment = {
            "id": f"ASMT{uuid.uuid4().hex[:8]}",
            "encounter_id": encounter_id,
            "assessment_type": assessment_type.value,
            "datetime": None,  # Will be set based on encounter timeline
            "provider_id": None,  # Will be set to a provider participant
            "result": result,
            "interpretation": self._generate_interpretation(assessment_type, result)
        }
        
        return assessment
    
    def _generate_interpretation(self, assessment_type: AssessmentType, result: Dict) -> str:
        """
        Generate an interpretation for an assessment result.
        
        Args:
            assessment_type: Type of assessment.
            result: Assessment result data.
            
        Returns:
            Interpretation text.
        """
        if assessment_type == AssessmentType.VITAL_SIGNS:
            # Simple interpretation of vital signs
            interpretations = []
            
            if "Blood Pressure" in result:
                bp = result["Blood Pressure"]
                systolic = int(bp.split('/')[0])
                diastolic = int(bp.split('/')[1].split(' ')[0])
                
                if systolic >= 140 or diastolic >= 90:
                    interpretations.append("Elevated blood pressure")
                elif systolic <= 90 or diastolic <= 60:
                    interpretations.append("Low blood pressure")
            
            if "Heart Rate" in result:
                hr = int(result["Heart Rate"].split(' ')[0])
                if hr > 100:
                    interpretations.append("Tachycardia")
                elif hr < 60:
                    interpretations.append("Bradycardia")
            
            if "Temperature" in result:
                temp = float(result["Temperature"].split('°')[0])
                if temp >= 100.4:
                    interpretations.append("Fever")
                elif temp <= 97.0:
                    interpretations.append("Hypothermia")
            
            if interpretations:
                return "; ".join(interpretations)
            else:
                return "Vital signs within normal limits"
        
        elif assessment_type == AssessmentType.PAIN:
            # Simple interpretation of pain assessment
            if "Pain Score" in result:
                pain_score = int(result["Pain Score"].split('/')[0])
                if pain_score >= 7:
                    return "Severe pain requiring intervention"
                elif pain_score >= 4:
                    return "Moderate pain requiring management"
                else:
                    return "Mild pain, continue current management"
        
        # Default interpretation
        return "Assessment completed, no significant abnormalities noted"
    
    def _generate_medications(self, encounter_id: str, encounter_type: EncounterType) -> List[Dict]:
        """
        Generate medications for an encounter.
        
        Args:
            encounter_id: ID of the encounter.
            encounter_type: Type of encounter.
            
        Returns:
            List of medication dictionaries.
        """
        medications = []
        
        # Determine how many medications to generate
        medication_count_config = self.encounter_config.get("medication_count", {"min": 0, "max": 5})
        medication_count = random.randint(
            medication_count_config.get("min", 0),
            medication_count_config.get("max", 5)
        )
        
        # Get medications for this encounter type
        encounter_medications = self.medications.get(encounter_type, [])
        if not encounter_medications:
            # Use ambulatory medications as fallback
            encounter_medications = self.medications.get(EncounterType.AMBULATORY, [])
        
        # Select random medications
        if medication_count > 0 and encounter_medications:
            selected_medications = random.sample(
                encounter_medications,
                min(medication_count, len(encounter_medications))
            )
            
            for medication in selected_medications:
                # Create medication object
                medication_obj = {
                    "id": f"MED{uuid.uuid4().hex[:8]}",
                    "encounter_id": encounter_id,
                    "medication_id": medication["id"],
                    "order_id": f"ORD{random.randint(10000, 99999)}",
                    "datetime": None,  # Will be set based on encounter timeline
                    "dose": medication["dose"],
                    "route": medication["route"].value,
                    "provider_id": None,  # Will be set to a provider participant
                    "status": MedicationStatus.ADMINISTERED.value
                }
                medications.append(medication_obj)
        
        return medications
    
    def _generate_transitions(self, encounters: List[Dict]) -> List[Dict]:
        """
        Generate transitions between encounters.
        
        Args:
            encounters: List of encounter dictionaries.
            
        Returns:
            List of transition dictionaries.
        """
        transitions = []
        
        # Sort encounters by start date
        sorted_encounters = sorted(
            encounters,
            key=lambda e: datetime.fromisoformat(e["start_datetime"].replace('Z', '+00:00'))
        )
        
        # Generate transitions with some probability
        transition_probability = self.encounter_config.get("transition_probability", 0.25)
        
        for i in range(len(sorted_encounters) - 1):
            if random.random() < transition_probability:
                from_encounter = sorted_encounters[i]
                to_encounter = sorted_encounters[i + 1]
                
                # Determine transition type based on encounter types
                transition_type = self._get_transition_type(from_encounter["type"], to_encounter["type"])
                
                # Create transition object
                transition = {
                    "id": f"TRANS{uuid.uuid4().hex[:8]}",
                    "from_encounter_id": from_encounter["id"],
                    "to_encounter_id": to_encounter["id"],
                    "transition_type": transition_type.value,
                    "datetime": from_encounter["end_datetime"] or from_encounter["start_datetime"],
                    "reason": f"Transition from {from_encounter['type']} to {to_encounter['type']}",
                    "authorizing_provider_id": None  # Will be set to a provider participant
                }
                transitions.append(transition)
        
        return transitions
    
    def _get_transition_type(self, from_type: str, to_type: str) -> TransitionType:
        """
        Get the appropriate transition type based on encounter types.
        
        Args:
            from_type: Type of the source encounter.
            to_type: Type of the destination encounter.
            
        Returns:
            Appropriate transition type.
        """
        # Convert string types to enum if needed
        if isinstance(from_type, str):
            from_type_enum = EncounterType(from_type)
        else:
            from_type_enum = from_type
            
        if isinstance(to_type, str):
            to_type_enum = EncounterType(to_type)
        else:
            to_type_enum = to_type
        
        # Determine transition type
        if from_type_enum == EncounterType.EMERGENCY and to_type_enum == EncounterType.INPATIENT:
            return TransitionType.ADMISSION
        elif from_type_enum == EncounterType.INPATIENT and to_type_enum in [EncounterType.AMBULATORY, EncounterType.HOME_HEALTH]:
            return TransitionType.DISCHARGE
        elif from_type_enum == EncounterType.AMBULATORY and to_type_enum in [EncounterType.INPATIENT, EncounterType.EMERGENCY]:
            return TransitionType.REFERRAL
        elif from_type_enum == to_type_enum:
            return TransitionType.TRANSFER
        else:
            return TransitionType.REFERRAL
    
    def _generate_encounters_for_member(self, member: Dict, providers: List[Dict], num_encounters: int) -> List[Dict]:
        """
        Generate a specified number of clinical encounters for a member.
        
        Args:
            member: Member dictionary to generate encounters for.
            providers: List of provider dictionaries to use as participants.
            num_encounters: Number of encounters to generate.
            
        Returns:
            List of generated clinical encounters as dictionaries.
        """
        encounters = []
        
        # Get member details
        member_id = member["id"]
        
        # Generate dates for the encounters (within the last 2 years)
        today = datetime.now()
        date_range = 730  # days (2 years)
        
        # Track previous encounters for potential transitions
        previous_encounters = []
        
        for i in range(num_encounters):
            # Generate a random date within the last 2 years
            days_ago = random.randint(0, date_range)
            encounter_date = today - timedelta(days=days_ago)
            
            # Select encounter type based on distribution
            encounter_type = self._select_weighted_option(
                self.encounter_config.get("encounter_type_distribution",
                                         {"Ambulatory": 0.5, "Inpatient": 0.2, "Emergency": 0.2, "Virtual": 0.1})
            )
            encounter_type_enum = EncounterType(encounter_type)
            
            # Select encounter status based on distribution
            encounter_status = self._select_weighted_option(
                self.encounter_config.get("encounter_status_distribution",
                                         {"Finished": 0.8, "In-Progress": 0.1, "Planned": 0.1})
            )
            encounter_status_enum = EncounterStatus(encounter_status)
            
            # Generate encounter ID
            encounter_id = f"ENC{uuid.uuid4().hex[:8]}"
            
            # Generate encounter class based on type
            encounter_class = self._get_encounter_class(encounter_type_enum)
            
            # Generate encounter priority
            encounter_priority = self._get_encounter_priority(encounter_type_enum)
            
            # Generate length of stay for inpatient encounters
            length_of_stay = None
            if encounter_type_enum == EncounterType.INPATIENT:
                los_config = self.encounter_config.get("inpatient_length_of_stay",
                                                     {"min": 1, "max": 10, "mean": 4, "std_dev": 2})
                length_of_stay = int(np.random.normal(los_config["mean"], los_config["std_dev"]))
                length_of_stay = max(los_config.get("min", 1), min(los_config.get("max", 30), length_of_stay))
            
            # Generate end date for completed encounters
            end_datetime = None
            if encounter_status_enum == EncounterStatus.FINISHED:
                if length_of_stay:
                    end_datetime = encounter_date + timedelta(days=length_of_stay)
                else:
                    # For non-inpatient encounters, typically same day or next day
                    hours_duration = random.randint(1, 36)
                    end_datetime = encounter_date + timedelta(hours=hours_duration)
            
            # Generate admission type for inpatient encounters
            admission_type = None
            if encounter_type_enum == EncounterType.INPATIENT:
                admission_type = random.choice(list(AdmissionType))
            
            # Generate discharge disposition for completed inpatient encounters
            discharge_disposition = None
            if encounter_type_enum == EncounterType.INPATIENT and encounter_status_enum == EncounterStatus.FINISHED:
                discharge_disposition = random.choice(list(DischargeDisposition))
            
            # Determine if this is a readmission
            readmission = False
            if encounter_type_enum == EncounterType.INPATIENT and previous_encounters:
                readmission_probability = self.encounter_config.get("readmission_probability", 0.08)
                readmission = random.random() < readmission_probability
            
            # Generate chief complaint based on encounter type
            chief_complaint = random.choice(self.chief_complaints.get(encounter_type_enum, ["General examination"]))
            
            # Generate service type
            service_type = random.choice(list(ServiceType))
            
            # Generate account and visit numbers
            account_number = f"A{random.randint(100000, 999999)}"
            visit_number = f"V{random.randint(100000, 999999)}"
            
            # Create the encounter object
            encounter = {
                "id": encounter_id,
                "type": encounter_type,
                "status": encounter_status,
                "class_type": encounter_class.value,
                "priority": encounter_priority.value if encounter_priority else None,
                "start_datetime": encounter_date.isoformat(),
                "end_datetime": end_datetime.isoformat() if end_datetime else None,
                "length_of_stay": length_of_stay,
                "admission_type": admission_type.value if admission_type else None,
                "discharge_disposition": discharge_disposition.value if discharge_disposition else None,
                "readmission": readmission,
                "chief_complaint": chief_complaint,
                "reason_code": None,  # Could be added based on chief complaint
                "service_type": service_type.value,
                "account_number": account_number,
                "visit_number": visit_number,
                "episode_of_care_id": None  # Could be linked to care episodes if available
            }
            
            # Generate related entities
            encounter["participants"] = self._generate_participants(encounter_id, member_id, providers)
            encounter["locations"] = self._generate_locations(encounter_id, encounter_type_enum)
            encounter["diagnoses"] = self._generate_diagnoses(encounter_id, encounter_type_enum)
            encounter["procedures"] = self._generate_procedures(encounter_id, encounter_type_enum)
            encounter["notes"] = self._generate_notes(encounter_id, encounter_type_enum)
            encounter["services"] = self._generate_services(encounter_id, encounter_type_enum)
            encounter["assessments"] = self._generate_assessments(encounter_id, encounter_type_enum)
            encounter["medications"] = self._generate_medications(encounter_id, encounter_type_enum)
            
            # Add to encounters list
            encounters.append(encounter)
            
            # Add to previous encounters for potential transitions
            previous_encounters.append(encounter)
        
        # Generate transitions between encounters
        transitions = self._generate_transitions(previous_encounters)
        
        # Add transitions to their respective encounters
        for transition in transitions:
            from_encounter_id = transition["from_encounter_id"]
            to_encounter_id = transition["to_encounter_id"]
            
            # Find the encounters and add the transition
            for encounter in encounters:
                if encounter["id"] == from_encounter_id:
                    if "transitions" not in encounter:
                        encounter["transitions"] = []
                    encounter["transitions"].append(transition)
        
        return encounters
