"""
Enhanced Member Generator for the synthetic healthcare data generator.

This module extends the base MemberGenerator with improved data quality and realism.
"""

import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set

import numpy as np
from faker import Faker

from src.generators.member_generator import MemberGenerator
from src.models.member import Address, Contact, Demographics, Insurance, Member


class EnhancedMemberGenerator(MemberGenerator):
    """Enhanced generator for synthetic member data with improved realism."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the enhanced member generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        
        # Initialize condition-medication mappings
        self._initialize_condition_mappings()
        
        # Initialize age-appropriate condition mappings
        self._initialize_age_condition_mappings()
        
        # Initialize demographic-condition correlations
        self._initialize_demographic_condition_correlations()
        
        # Initialize procedure mappings
        self._initialize_procedure_mappings()
        
        # Initialize realistic name distributions
        self._initialize_name_distributions()
    
    def _initialize_condition_mappings(self):
        """Initialize mappings between conditions and related medications."""
        # Map conditions to common medications used to treat them
        self.condition_to_medications = {
            "Hypertension": [
                "Lisinopril", "Amlodipine", "Hydrochlorothiazide", "Losartan",
                "Metoprolol", "Valsartan", "Atenolol", "Diltiazem", "Chlorthalidone"
            ],
            "Type 2 Diabetes": [
                "Metformin", "Glipizide", "Januvia", "Jardiance", "Ozempic",
                "Trulicity", "Glyburide", "Invokana", "Farxiga"
            ],
            "Asthma": [
                "Albuterol", "Fluticasone", "Montelukast", "Symbicort", "Advair",
                "Budesonide", "Ipratropium", "Theophylline", "Prednisone"
            ],
            "Obesity": [
                "Phentermine", "Contrave", "Wegovy", "Saxenda", "Qsymia",
                "Xenical", "Metformin"
            ],
            "Depression": [
                "Sertraline", "Escitalopram", "Fluoxetine", "Bupropion", "Venlafaxine",
                "Duloxetine", "Mirtazapine", "Trazodone", "Paroxetine"
            ],
            "Anxiety": [
                "Sertraline", "Escitalopram", "Buspirone", "Alprazolam", "Lorazepam",
                "Duloxetine", "Venlafaxine", "Hydroxyzine", "Propranolol"
            ],
            "GERD": [
                "Omeprazole", "Pantoprazole", "Famotidine", "Ranitidine", "Esomeprazole",
                "Lansoprazole", "Sucralfate", "Dexlansoprazole"
            ],
            "Osteoarthritis": [
                "Acetaminophen", "Ibuprofen", "Naproxen", "Meloxicam", "Celecoxib",
                "Diclofenac", "Tramadol", "Duloxetine", "Prednisone"
            ],
            "Hyperlipidemia": [
                "Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin", "Ezetimibe",
                "Fenofibrate", "Gemfibrozil", "Lovastatin", "Alirocumab"
            ],
            "Hypothyroidism": [
                "Levothyroxine", "Liothyronine", "Armour Thyroid", "Synthroid", "Tirosint"
            ],
            "Allergic Rhinitis": [
                "Fluticasone", "Cetirizine", "Loratadine", "Fexofenadine", "Montelukast",
                "Azelastine", "Diphenhydramine", "Desloratadine", "Levocetirizine"
            ],
            "Migraine": [
                "Sumatriptan", "Rizatriptan", "Propranolol", "Topiramate", "Amitriptyline",
                "Aimovig", "Ubrelvy", "Nurtec", "Botox"
            ],
            "Insomnia": [
                "Zolpidem", "Eszopiclone", "Temazepam", "Trazodone", "Doxepin",
                "Ramelteon", "Melatonin", "Belsomra", "Dayvigo"
            ],
            "Back Pain": [
                "Acetaminophen", "Ibuprofen", "Naproxen", "Cyclobenzaprine", "Gabapentin",
                "Tramadol", "Duloxetine", "Diclofenac", "Methocarbamol"
            ],
            "Osteoporosis": [
                "Alendronate", "Risedronate", "Denosumab", "Teriparatide", "Ibandronate",
                "Raloxifene", "Zoledronic Acid", "Calcitonin", "Abaloparatide"
            ],
            "Chronic Kidney Disease": [
                "Lisinopril", "Losartan", "Furosemide", "Spironolactone", "Sevelamer",
                "Calcitriol", "Cinacalcet", "Darbepoetin", "Sodium Bicarbonate"
            ],
            "Atrial Fibrillation": [
                "Warfarin", "Apixaban", "Rivaroxaban", "Dabigatran", "Metoprolol",
                "Diltiazem", "Amiodarone", "Sotalol", "Flecainide"
            ],
            "COPD": [
                "Albuterol", "Tiotropium", "Fluticasone/Salmeterol", "Budesonide/Formoterol",
                "Ipratropium", "Roflumilast", "Prednisone", "Azithromycin", "Montelukast"
            ],
            "Benign Prostatic Hyperplasia": [
                "Tamsulosin", "Finasteride", "Dutasteride", "Alfuzosin", "Silodosin",
                "Terazosin", "Doxazosin"
            ],
            "Heart Failure": [
                "Lisinopril", "Metoprolol", "Furosemide", "Spironolactone", "Sacubitril/Valsartan",
                "Carvedilol", "Digoxin", "Eplerenone", "Hydralazine/Isosorbide"
            ],
            "Rheumatoid Arthritis": [
                "Methotrexate", "Hydroxychloroquine", "Prednisone", "Adalimumab", "Etanercept",
                "Leflunomide", "Sulfasalazine", "Tofacitinib", "Rituximab"
            ]
        }
        
        # Map conditions to related conditions (comorbidities)
        self.condition_comorbidities = {
            "Hypertension": ["Hyperlipidemia", "Type 2 Diabetes", "Chronic Kidney Disease", "Heart Failure"],
            "Type 2 Diabetes": ["Hypertension", "Hyperlipidemia", "Obesity", "Chronic Kidney Disease"],
            "Asthma": ["Allergic Rhinitis", "GERD", "Obesity"],
            "Obesity": ["Type 2 Diabetes", "Hypertension", "GERD", "Osteoarthritis", "Back Pain"],
            "Depression": ["Anxiety", "Insomnia", "Chronic Pain"],
            "Anxiety": ["Depression", "Insomnia", "GERD"],
            "GERD": ["Asthma", "Obesity", "Insomnia"],
            "Osteoarthritis": ["Obesity", "Back Pain", "Osteoporosis"],
            "Hyperlipidemia": ["Hypertension", "Type 2 Diabetes", "Heart Failure"],
            "Hypothyroidism": ["Depression", "Hyperlipidemia", "Obesity"],
            "Allergic Rhinitis": ["Asthma", "Sinusitis"],
            "Migraine": ["Depression", "Anxiety", "Insomnia"],
            "Insomnia": ["Depression", "Anxiety", "Chronic Pain"],
            "Back Pain": ["Obesity", "Osteoarthritis", "Depression"],
            "Osteoporosis": ["Hypothyroidism", "Rheumatoid Arthritis"],
            "Chronic Kidney Disease": ["Hypertension", "Type 2 Diabetes", "Heart Failure"],
            "Atrial Fibrillation": ["Hypertension", "Heart Failure", "Hyperlipidemia"],
            "COPD": ["Hypertension", "Osteoporosis", "Depression"],
            "Benign Prostatic Hyperplasia": ["Hypertension", "Type 2 Diabetes"],
            "Heart Failure": ["Hypertension", "Hyperlipidemia", "Atrial Fibrillation", "Chronic Kidney Disease"],
            "Rheumatoid Arthritis": ["Osteoporosis", "Depression", "Hypothyroidism"]
        }
        
        # Create reverse mapping from medications to conditions
        self.medication_to_conditions = {}
        for condition, medications in self.condition_to_medications.items():
            for medication in medications:
                if medication not in self.medication_to_conditions:
                    self.medication_to_conditions[medication] = []
                self.medication_to_conditions[medication].append(condition)
    
    def _initialize_age_condition_mappings(self):
        """Initialize mappings between age groups and common conditions."""
        self.age_condition_prevalence = {
            # Pediatric (0-17)
            (0, 17): {
                "Asthma": 0.08,
                "Allergic Rhinitis": 0.15,
                "Obesity": 0.05,
                "Type 1 Diabetes": 0.002,
                "ADHD": 0.09,
                "Anxiety": 0.07,
                "Depression": 0.03,
                "Eczema": 0.1
            },
            # Young Adult (18-34)
            (18, 34): {
                "Anxiety": 0.1,
                "Depression": 0.08,
                "Asthma": 0.07,
                "Allergic Rhinitis": 0.12,
                "Obesity": 0.15,
                "GERD": 0.05,
                "Migraine": 0.06,
                "Insomnia": 0.07,
                "Type 2 Diabetes": 0.03,
                "Hypertension": 0.05
            },
            # Middle Age (35-50)
            (35, 50): {
                "Hypertension": 0.2,
                "Type 2 Diabetes": 0.1,
                "Hyperlipidemia": 0.15,
                "Obesity": 0.25,
                "Depression": 0.1,
                "Anxiety": 0.12,
                "GERD": 0.15,
                "Back Pain": 0.2,
                "Migraine": 0.08,
                "Insomnia": 0.1,
                "Asthma": 0.06,
                "Hypothyroidism": 0.05
            },
            # Older Adult (51-64)
            (51, 64): {
                "Hypertension": 0.4,
                "Hyperlipidemia": 0.35,
                "Type 2 Diabetes": 0.2,
                "Obesity": 0.3,
                "Osteoarthritis": 0.15,
                "GERD": 0.2,
                "Hypothyroidism": 0.1,
                "Back Pain": 0.25,
                "Insomnia": 0.15,
                "Depression": 0.12,
                "Anxiety": 0.1,
                "Chronic Kidney Disease": 0.05,
                "Benign Prostatic Hyperplasia": 0.15,  # Males only
                "Osteoporosis": 0.1  # Females primarily
            },
            # Senior (65+)
            (65, 100): {
                "Hypertension": 0.6,
                "Hyperlipidemia": 0.45,
                "Type 2 Diabetes": 0.25,
                "Osteoarthritis": 0.3,
                "GERD": 0.25,
                "Hypothyroidism": 0.15,
                "Chronic Kidney Disease": 0.15,
                "Heart Failure": 0.1,
                "Atrial Fibrillation": 0.08,
                "COPD": 0.1,
                "Osteoporosis": 0.2,  # Females primarily
                "Benign Prostatic Hyperplasia": 0.3,  # Males only
                "Depression": 0.15,
                "Insomnia": 0.2,
                "Back Pain": 0.3,
                "Obesity": 0.25
            }
        }
        
        # Gender-specific conditions
        self.gender_specific_conditions = {
            "male": ["Benign Prostatic Hyperplasia", "Erectile Dysfunction", "Testicular Cancer"],
            "female": ["Breast Cancer", "Ovarian Cancer", "Endometriosis", "Polycystic Ovary Syndrome"],
            "other": []  # No gender-specific conditions for "other" gender
        }
        
        # Conditions that should be excluded for certain age groups
        self.age_excluded_conditions = {
            (0, 17): ["Benign Prostatic Hyperplasia", "Osteoporosis", "Atrial Fibrillation",
                     "Heart Failure", "Chronic Kidney Disease", "Type 2 Diabetes"],
            (18, 34): ["Benign Prostatic Hyperplasia", "Osteoporosis", "Atrial Fibrillation",
                      "Heart Failure", "Chronic Kidney Disease"]
        }
    
    def _initialize_demographic_condition_correlations(self):
        """Initialize correlations between demographic factors and conditions."""
        # Race/ethnicity correlations with certain conditions
        self.race_condition_correlations = {
            "White": {
                "Multiple Sclerosis": 1.5,  # Higher prevalence
                "Cystic Fibrosis": 1.5,
                "Osteoporosis": 1.2
            },
            "Black": {
                "Hypertension": 1.4,  # Higher prevalence
                "Type 2 Diabetes": 1.3,
                "Sickle Cell Disease": 8.0,
                "Lupus": 2.0
            },
            "Asian": {
                "Type 2 Diabetes": 1.2,  # Higher prevalence
                "Lactose Intolerance": 1.5,
                "Hypertension": 0.9  # Slightly lower prevalence
            },
            "Native American": {
                "Type 2 Diabetes": 1.6,  # Higher prevalence
                "Alcoholism": 1.3,
                "Obesity": 1.3
            },
            "Pacific Islander": {
                "Type 2 Diabetes": 1.5,  # Higher prevalence
                "Obesity": 1.4,
                "Gout": 1.5
            },
            "Other": {
                # No specific correlations
            }
        }
        
        # State/region correlations with certain conditions
        self.region_condition_correlations = {
            # States with higher obesity rates
            "MS": {"Obesity": 1.5, "Type 2 Diabetes": 1.3, "Hypertension": 1.2},
            "WV": {"Obesity": 1.5, "COPD": 1.4, "Depression": 1.2},
            "AL": {"Obesity": 1.4, "Type 2 Diabetes": 1.3, "Hypertension": 1.2},
            "LA": {"Obesity": 1.4, "Type 2 Diabetes": 1.3, "Hypertension": 1.2},
            "KY": {"Obesity": 1.4, "COPD": 1.4, "Depression": 1.2},
            
            # States with higher asthma rates
            "NY": {"Asthma": 1.3, "Anxiety": 1.2},
            "MA": {"Asthma": 1.3, "Anxiety": 1.2},
            "OH": {"Asthma": 1.2, "COPD": 1.2},
            
            # States with higher allergy rates
            "TX": {"Allergic Rhinitis": 1.3},
            "TN": {"Allergic Rhinitis": 1.3},
            "SC": {"Allergic Rhinitis": 1.3},
            
            # States with higher skin cancer rates
            "AZ": {"Skin Cancer": 1.4},
            "NV": {"Skin Cancer": 1.4},
            "UT": {"Skin Cancer": 1.4},
            "CO": {"Skin Cancer": 1.3},
            
            # States with higher depression rates
            "OR": {"Depression": 1.3, "Anxiety": 1.2},
            "WA": {"Depression": 1.3, "Anxiety": 1.2},
            "ME": {"Depression": 1.3, "Seasonal Affective Disorder": 1.5},
            "VT": {"Depression": 1.3, "Seasonal Affective Disorder": 1.5},
            "NH": {"Depression": 1.3, "Seasonal Affective Disorder": 1.5}
        }
    
    def _initialize_procedure_mappings(self):
        """Initialize mappings between conditions and related procedures."""
        self.condition_to_procedures = {
            "Hypertension": [
                "Blood Pressure Check", "EKG", "Echocardiogram", "Lipid Panel",
                "Renal Function Panel", "Annual Physical"
            ],
            "Type 2 Diabetes": [
                "HbA1c Test", "Lipid Panel", "Diabetic Eye Exam", "Diabetic Foot Exam",
                "Renal Function Panel", "Annual Physical"
            ],
            "Asthma": [
                "Pulmonary Function Test", "Peak Flow Measurement", "Chest X-Ray",
                "Allergy Testing", "Annual Physical"
            ],
            "Obesity": [
                "BMI Assessment", "Lipid Panel", "Glucose Test", "Nutritional Counseling",
                "Annual Physical"
            ],
            "Depression": [
                "PHQ-9 Screening", "Psychotherapy", "Medication Management",
                "Annual Physical"
            ],
            "Anxiety": [
                "GAD-7 Screening", "Psychotherapy", "Medication Management",
                "Annual Physical"
            ],
            "GERD": [
                "Endoscopy", "Esophageal pH Monitoring", "H. Pylori Testing",
                "Annual Physical"
            ],
            "Osteoarthritis": [
                "Joint X-Ray", "Joint MRI", "Joint Injection", "Physical Therapy",
                "Annual Physical"
            ],
            "Hyperlipidemia": [
                "Lipid Panel", "Cardiovascular Risk Assessment", "Carotid Ultrasound",
                "Stress Test", "Annual Physical"
            ],
            "Hypothyroidism": [
                "Thyroid Function Panel", "Thyroid Ultrasound", "Annual Physical"
            ],
            "Allergic Rhinitis": [
                "Allergy Testing", "Nasal Endoscopy", "Annual Physical"
            ],
            "Migraine": [
                "Neurological Exam", "Brain MRI", "Annual Physical"
            ],
            "Insomnia": [
                "Sleep Study", "Psychological Evaluation", "Annual Physical"
            ],
            "Back Pain": [
                "Spine X-Ray", "Spine MRI", "Physical Therapy", "EMG",
                "Annual Physical"
            ],
            "Osteoporosis": [
                "DEXA Scan", "Vitamin D Level", "Calcium Level", "Annual Physical"
            ],
            "Chronic Kidney Disease": [
                "Renal Function Panel", "Renal Ultrasound", "Urine Microalbumin",
                "Annual Physical"
            ],
            "Atrial Fibrillation": [
                "EKG", "Echocardiogram", "Holter Monitor", "Annual Physical"
            ],
            "COPD": [
                "Pulmonary Function Test", "Chest X-Ray", "Oxygen Saturation",
                "Annual Physical"
            ],
            "Benign Prostatic Hyperplasia": [
                "Prostate Exam", "PSA Test", "Urodynamic Testing", "Annual Physical"
            ],
            "Heart Failure": [
                "EKG", "Echocardiogram", "BNP Test", "Stress Test", "Annual Physical"
            ],
            "Rheumatoid Arthritis": [
                "Rheumatoid Factor", "Anti-CCP Antibody", "Joint X-Ray", "Annual Physical"
            ],
            "Colorectal Cancer Screening": [
                "Colonoscopy", "Fecal Occult Blood Test", "Sigmoidoscopy", "Annual Physical"
            ],
            "Breast Cancer Screening": [
                "Mammogram", "Breast Ultrasound", "Annual Physical"
            ],
            "Prostate Cancer Screening": [
                "PSA Test", "Digital Rectal Exam", "Annual Physical"
            ],
            "Cervical Cancer Screening": [
                "Pap Smear", "HPV Testing", "Annual Physical"
            ],
            "Lung Cancer Screening": [
                "Low-Dose CT Scan", "Chest X-Ray", "Annual Physical"
            ]
        }
        
        # Create reverse mapping from procedures to conditions
        self.procedure_to_conditions = {}
        for condition, procedures in self.condition_to_procedures.items():
            for procedure in procedures:
                if procedure not in self.procedure_to_conditions:
                    self.procedure_to_conditions[procedure] = []
                self.procedure_to_conditions[procedure].append(condition)
    
    def _initialize_name_distributions(self):
        """Initialize more realistic name distributions."""
        # This is a placeholder for potential future enhancement
        # We could add more realistic name distributions based on demographics
        pass
    
    def generate(self, count: int) -> List[Member]:
        """
        Generate synthetic member data with improved realism.
        
        Args:
            count: Number of members to generate.
            
        Returns:
            List of generated Member objects.
        """
        self.logger.info(f"Generating {count} members with enhanced realism")
        members = []
        
        for i in range(count):
            member = self._generate_enhanced_member(i)
            members.append(member)
            
        self.logger.info(f"Generated {len(members)} members")
        return members
    
    def _generate_enhanced_member(self, index: int) -> Member:
        """
        Generate a single synthetic member with enhanced realism.
        
        Args:
            index: Index of the member (used for ID generation).
            
        Returns:
            A synthetic Member object.
        """
        # Generate member ID
        member_id = f"MEM{index:08d}"
        
        # Generate gender with realistic distribution
        gender = self._generate_gender()
        
        # Generate name based on gender
        if gender == "male":
            first_name = self.faker.first_name_male()
        elif gender == "female":
            first_name = self.faker.first_name_female()
        else:
            first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        
        # Generate demographics with realistic age distribution
        demographics = self._generate_demographics(gender)
        
        # Generate address
        address = self._generate_address()
        
        # Generate contact information
        contact = self._generate_contact()
        
        # Generate insurance information
        insurance = self._generate_insurance(member_id)
        
        # Generate clinical information with realistic correlations
        age = (date.today() - demographics.date_of_birth).days // 365
        conditions = self._generate_enhanced_conditions(age, gender, demographics.race, address.state)
        medications = self._generate_enhanced_medications(conditions, age, gender)
        procedures = self._generate_enhanced_procedures(conditions, age, gender)
        
        # Create and return member
        return Member(
            id=member_id,
            first_name=first_name,
            last_name=last_name,
            demographics=demographics,
            address=address,
            contact=contact,
            insurance=insurance,
            conditions=conditions,
            medications=medications,
            procedures=procedures
        )
    
    def _generate_enhanced_conditions(self, age: int, gender: str, race: str, state: str) -> List[str]:
        """
        Generate a list of medical conditions with realistic correlations.
        
        Args:
            age: Age of the member.
            gender: Gender of the member.
            race: Race of the member.
            state: State of residence.
            
        Returns:
            List of conditions.
        """
        # Determine age group
        age_group = None
        for age_range in self.age_condition_prevalence.keys():
            if age_range[0] <= age <= age_range[1]:
                age_group = age_range
                break
        
        if not age_group:
            # Fallback to default condition generation if age group not found
            return super()._generate_conditions()
        
        # Get conditions and prevalence for this age group
        age_conditions = self.age_condition_prevalence[age_group]
        
        # Apply demographic correlations
        adjusted_conditions = {}
        for condition, prevalence in age_conditions.items():
            # Skip gender-specific conditions that don't apply
            if (condition in self.gender_specific_conditions.get("male", []) and gender != "male") or \
               (condition in self.gender_specific_conditions.get("female", []) and gender != "female"):
                continue
            
            # Skip conditions excluded for this age group
            if age_group in self.age_excluded_conditions and condition in self.age_excluded_conditions[age_group]:
                continue
            
            # Apply race/ethnicity correlation if available
            race_multiplier = 1.0
            if race in self.race_condition_correlations and condition in self.race_condition_correlations[race]:
                race_multiplier = self.race_condition_correlations[race][condition]
            
            # Apply regional correlation if available
            region_multiplier = 1.0
            if state in self.region_condition_correlations and condition in self.region_condition_correlations[state]:
                region_multiplier = self.region_condition_correlations[state][condition]
            
            # Calculate adjusted prevalence
            adjusted_prevalence = prevalence * race_multiplier * region_multiplier
            adjusted_conditions[condition] = min(adjusted_prevalence, 0.95)  # Cap at 95% probability
        
        # Determine number of conditions based on config
        condition_config = self.clinical_config.get('condition_count', {
            'min': 0,
            'max': 10,
            'mean': 3,
            'std_dev': 2
        })
        
        num_conditions = int(np.clip(
            np.random.normal(condition_config['mean'], condition_config['std_dev']),
            condition_config['min'],
            condition_config['max']
        ))
        
        if num_conditions == 0:
            return []
        
        # Select conditions based on adjusted prevalence
        selected_conditions = []
        for condition, prevalence in adjusted_conditions.items():
            if random.random() < prevalence and len(selected_conditions) < num_conditions:
                selected_conditions.append(condition)
        
        # If we need more conditions, add comorbidities
        if len(selected_conditions) > 0 and len(selected_conditions) < num_conditions:
            possible_comorbidities = set()
            for condition in selected_conditions:
                if condition in self.condition_comorbidities:
                    possible_comorbidities.update(self.condition_comorbidities[condition])
            
            # Filter out already selected conditions and those not appropriate for age
            possible_comorbidities = [c for c in possible_comorbidities if c not in selected_conditions]
            if age_group in self.age_excluded_conditions:
                possible_comorbidities = [c for c in possible_comorbidities if c not in self.age_excluded_conditions[age_group]]
            
            # Add comorbidities until we reach the desired number or run out of options
            while len(selected_conditions) < num_conditions and possible_comorbidities:
                comorbidity = random.choice(possible_comorbidities)
                selected_conditions.append(comorbidity)
                possible_comorbidities.remove(comorbidity)
        
        # If we still need more conditions, add random ones from the age-appropriate list
        remaining_conditions = [c for c in age_conditions.keys() if c not in selected_conditions]
        while len(selected_conditions) < num_conditions and remaining_conditions:
            condition = random.choice(remaining_conditions)
            if (condition in self.gender_specific_conditions.get("male", []) and gender != "male") or \
               (condition in self.gender_specific_conditions.get("female", []) and gender != "female"):
                remaining_conditions.remove(condition)
                continue
            
            selected_conditions.append(condition)
            remaining_conditions.remove(condition)
        
        return selected_conditions
    
    def _generate_enhanced_medications(self, conditions: List[str], age: int, gender: str) -> List[str]:
        """
        Generate a list of medications with realistic correlations to conditions.
        
        Args:
            conditions: List of member conditions.
            age: Age of the member.
            gender: Gender of the member.
            
        Returns:
            List of medications.
        """
        if not conditions:
            return []
        
        # Determine number of medications based on config and age
        medication_config = self.clinical_config.get('medication_count', {
            'min': 0,
            'max': 15,
            'mean': 2,
            'std_dev': 3
        })
        
        # Older people tend to have more medications
        age_multiplier = 1.0
        if age >= 65:
            age_multiplier = 1.5
        elif age >= 50:
            age_multiplier = 1.3
        elif age >= 35:
            age_multiplier = 1.1
        
        adjusted_mean = medication_config['mean'] * age_multiplier
        
        # Calculate number of medications
        num_medications = int(np.clip(
            np.random.normal(adjusted_mean, medication_config['std_dev']),
            medication_config['min'],
            medication_config['max']
        ))
        
        if num_medications == 0:
            return []
        
        # Generate medications based on conditions
        potential_medications = []
        for condition in conditions:
            if condition in self.condition_to_medications:
                potential_medications.extend(self.condition_to_medications[condition])
        
        # Remove duplicates
        potential_medications = list(set(potential_medications))
        
        # If we have more potential medications than needed, select a subset
        if len(potential_medications) > num_medications:
            return random.sample(potential_medications, num_medications)
        
        # If we need more medications, add some random ones
        if len(potential_medications) < num_medications:
            all_medications = []
            for medications in self.condition_to_medications.values():
                all_medications.extend(medications)
            
            # Remove duplicates and already selected medications
            all_medications = list(set(all_medications) - set(potential_medications))
            
            # Add random medications until we reach the desired number
            additional_count = min(num_medications - len(potential_medications), len(all_medications))
            if additional_count > 0:
                potential_medications.extend(random.sample(all_medications, additional_count))
        
        return potential_medications
    
    def _generate_enhanced_procedures(self, conditions: List[str], age: int, gender: str) -> List[str]:
        """
        Generate a list of procedures with realistic correlations to conditions.
        
        Args:
            conditions: List of member conditions.
            age: Age of the member.
            gender: Gender of the member.
            
        Returns:
            List of procedures.
        """
        if not conditions:
            return []
        
        # Determine number of procedures based on config
        procedure_config = self.clinical_config.get('procedure_count', {
            'min': 0,
            'max': 5,
            'mean': 1,
            'std_dev': 1
        })
        
        # Calculate number of procedures
        num_procedures = int(np.clip(
            np.random.normal(procedure_config['mean'], procedure_config['std_dev']),
            procedure_config['min'],
            procedure_config['max']
        ))
        
        if num_procedures == 0:
            return []
        
        # Generate procedures based on conditions
        potential_procedures = []
        for condition in conditions:
            if condition in self.condition_to_procedures:
                potential_procedures.extend(self.condition_to_procedures[condition])
        
        # Add age and gender appropriate screening procedures
        if age >= 45 and gender == "male":
            potential_procedures.append("Prostate Cancer Screening")
        if age >= 40 and gender == "female":
            potential_procedures.append("Mammogram")
        if age >= 45:
            potential_procedures.append("Colorectal Cancer Screening")
        if age >= 55 and "Smoking" in conditions:
            potential_procedures.append("Lung Cancer Screening")
        
        # Always include annual physical for adults
        if age >= 18:
            potential_procedures.append("Annual Physical")
        
        # Remove duplicates
        potential_procedures = list(set(potential_procedures))
        
        # If we have more potential procedures than needed, select a subset
        if len(potential_procedures) > num_procedures:
            # Ensure Annual Physical is included if it was in the potential list
            if "Annual Physical" in potential_procedures and num_procedures > 0:
                selected_procedures = ["Annual Physical"]
                potential_procedures.remove("Annual Physical")
                if num_procedures > 1:
                    selected_procedures.extend(random.sample(potential_procedures, num_procedures - 1))
                return selected_procedures
            else:
                return random.sample(potential_procedures, num_procedures)
        
        return potential_procedures
