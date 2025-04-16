"""
Pharmacy Benefit Generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic pharmacy benefits and claims,
including formularies, medication lists, and pharmacy-related claims.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from src.utils.file_utils import load_config


class Medication:
    """
    Represents a medication in a pharmacy benefit.
    """
    
    def __init__(self, medication_id: Optional[str] = None):
        """
        Initialize a medication.
        
        Args:
            medication_id: Medication ID (generated if not provided)
        """
        self.id = medication_id or f"MED{uuid.uuid4().hex[:8].upper()}"
        self.name = None
        self.generic_name = None
        self.ndc = None
        self.drug_class = None
        self.therapeutic_class = None
        self.form = None
        self.strength = None
        self.route = None
        self.tier = None
        self.prior_auth_required = None
        self.quantity_limits = None
        self.step_therapy = None
        self.specialty = None
        
    def set_basic_info(self, name: str, generic_name: str, ndc: str) -> None:
        """
        Set basic medication information.
        
        Args:
            name: Brand name of the medication
            generic_name: Generic name of the medication
            ndc: National Drug Code
        """
        self.name = name
        self.generic_name = generic_name
        self.ndc = ndc
        
    def set_classification(self, drug_class: str, therapeutic_class: str) -> None:
        """
        Set medication classification.
        
        Args:
            drug_class: Drug class
            therapeutic_class: Therapeutic class
        """
        self.drug_class = drug_class
        self.therapeutic_class = therapeutic_class
        
    def set_form_info(self, form: str, strength: str, route: str) -> None:
        """
        Set medication form information.
        
        Args:
            form: Dosage form (tablet, capsule, etc.)
            strength: Medication strength
            route: Administration route
        """
        self.form = form
        self.strength = strength
        self.route = route
        
    def set_formulary_info(self, tier: int, prior_auth_required: bool, 
                          quantity_limits: Optional[Dict[str, Any]] = None,
                          step_therapy: bool = False, specialty: bool = False) -> None:
        """
        Set formulary-related information.
        
        Args:
            tier: Formulary tier (1, 2, 3, etc.)
            prior_auth_required: Whether prior authorization is required
            quantity_limits: Quantity limits (if any)
            step_therapy: Whether step therapy is required
            specialty: Whether this is a specialty medication
        """
        self.tier = tier
        self.prior_auth_required = prior_auth_required
        self.quantity_limits = quantity_limits
        self.step_therapy = step_therapy
        self.specialty = specialty
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the medication to a dictionary.
        
        Returns:
            Dictionary representation of the medication
        """
        return {
            "id": self.id,
            "name": self.name,
            "generic_name": self.generic_name,
            "ndc": self.ndc,
            "drug_class": self.drug_class,
            "therapeutic_class": self.therapeutic_class,
            "form": self.form,
            "strength": self.strength,
            "route": self.route,
            "tier": self.tier,
            "prior_auth_required": self.prior_auth_required,
            "quantity_limits": self.quantity_limits,
            "step_therapy": self.step_therapy,
            "specialty": self.specialty
        }


class Formulary:
    """
    Represents a pharmacy benefit formulary.
    """
    
    def __init__(self, formulary_id: Optional[str] = None):
        """
        Initialize a formulary.
        
        Args:
            formulary_id: Formulary ID (generated if not provided)
        """
        self.id = formulary_id or f"FORM{uuid.uuid4().hex[:8].upper()}"
        self.name = None
        self.effective_date = None
        self.tier_structure = {}
        self.medications = []
        self.exclusions = []
        
    def set_basic_info(self, name: str, effective_date: datetime) -> None:
        """
        Set basic formulary information.
        
        Args:
            name: Formulary name
            effective_date: Effective date of the formulary
        """
        self.name = name
        self.effective_date = effective_date
        
    def set_tier_structure(self, tier_structure: Dict[int, Dict[str, Any]]) -> None:
        """
        Set the tier structure for the formulary.
        
        Args:
            tier_structure: Dictionary mapping tier numbers to tier information
        """
        self.tier_structure = tier_structure
        
    def add_medication(self, medication: Dict[str, Any]) -> None:
        """
        Add a medication to the formulary.
        
        Args:
            medication: Dictionary containing medication information
        """
        self.medications.append(medication)
        
    def add_exclusion(self, medication_id: str, reason: str) -> None:
        """
        Add an excluded medication to the formulary.
        
        Args:
            medication_id: ID of the excluded medication
            reason: Reason for exclusion
        """
        self.exclusions.append({
            "medication_id": medication_id,
            "reason": reason
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the formulary to a dictionary.
        
        Returns:
            Dictionary representation of the formulary
        """
        return {
            "id": self.id,
            "name": self.name,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "tier_structure": self.tier_structure,
            "medications": self.medications,
            "exclusions": self.exclusions
        }


class PharmacyClaim:
    """
    Represents a pharmacy claim.
    """
    
    def __init__(self, claim_id: Optional[str] = None):
        """
        Initialize a pharmacy claim.
        
        Args:
            claim_id: Claim ID (generated if not provided)
        """
        self.id = claim_id or f"RX{uuid.uuid4().hex[:8].upper()}"
        self.member_id = None
        self.medication_id = None
        self.pharmacy_id = None
        self.prescriber_id = None
        self.fill_date = None
        self.days_supply = None
        self.quantity = None
        self.refill_number = None
        self.total_refills = None
        self.ndc = None
        self.drug_name = None
        self.drug_tier = None
        self.total_cost = None
        self.member_cost = None
        self.plan_paid = None
        self.status = None
        self.rejection_reason = None
        
    def set_basic_info(self, member_id: str, medication_id: str, pharmacy_id: str, prescriber_id: str) -> None:
        """
        Set basic claim information.
        
        Args:
            member_id: ID of the member
            medication_id: ID of the medication
            pharmacy_id: ID of the pharmacy
            prescriber_id: ID of the prescriber
        """
        self.member_id = member_id
        self.medication_id = medication_id
        self.pharmacy_id = pharmacy_id
        self.prescriber_id = prescriber_id
        
    def set_fill_info(self, fill_date: datetime, days_supply: int, quantity: float,
                     refill_number: int, total_refills: int) -> None:
        """
        Set fill information.
        
        Args:
            fill_date: Date the prescription was filled
            days_supply: Number of days the supply will last
            quantity: Quantity dispensed
            refill_number: Current refill number (0 for initial fill)
            total_refills: Total number of refills authorized
        """
        self.fill_date = fill_date
        self.days_supply = days_supply
        self.quantity = quantity
        self.refill_number = refill_number
        self.total_refills = total_refills
        
    def set_drug_info(self, ndc: str, drug_name: str, drug_tier: int) -> None:
        """
        Set drug information.
        
        Args:
            ndc: National Drug Code
            drug_name: Name of the drug
            drug_tier: Formulary tier
        """
        self.ndc = ndc
        self.drug_name = drug_name
        self.drug_tier = drug_tier
        
    def set_cost_info(self, total_cost: float, member_cost: float, plan_paid: float) -> None:
        """
        Set cost information.
        
        Args:
            total_cost: Total cost of the prescription
            member_cost: Amount paid by the member
            plan_paid: Amount paid by the plan
        """
        self.total_cost = total_cost
        self.member_cost = member_cost
        self.plan_paid = plan_paid
        
    def set_status(self, status: str, rejection_reason: Optional[str] = None) -> None:
        """
        Set claim status.
        
        Args:
            status: Claim status (paid, rejected, reversed)
            rejection_reason: Reason for rejection (if applicable)
        """
        self.status = status
        self.rejection_reason = rejection_reason
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pharmacy claim to a dictionary.
        
        Returns:
            Dictionary representation of the pharmacy claim
        """
        return {
            "id": self.id,
            "member_id": self.member_id,
            "medication_id": self.medication_id,
            "pharmacy_id": self.pharmacy_id,
            "prescriber_id": self.prescriber_id,
            "fill_date": self.fill_date.isoformat() if self.fill_date else None,
            "days_supply": self.days_supply,
            "quantity": self.quantity,
            "refill_number": self.refill_number,
            "total_refills": self.total_refills,
            "ndc": self.ndc,
            "drug_name": self.drug_name,
            "drug_tier": self.drug_tier,
            "total_cost": self.total_cost,
            "member_cost": self.member_cost,
            "plan_paid": self.plan_paid,
            "status": self.status,
            "rejection_reason": self.rejection_reason
        }


class PharmacyBenefitGenerator:
    """
    Generator for synthetic pharmacy benefits and claims.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the pharmacy benefit generator.
        
        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config
        self.pharmacy_config = config.get("pharmacy_benefit_config", {})
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load reference data
        self.drug_classes = self.pharmacy_config.get("drug_classes", [
            "Analgesics", "Antihypertensives", "Antidiabetics", "Antidepressants",
            "Antipsychotics", "Antibiotics", "Anticoagulants", "Anticonvulsants",
            "Antineoplastics", "Bronchodilators", "Corticosteroids", "Lipid-lowering",
            "Proton Pump Inhibitors", "Thyroid Hormones", "Vaccines"
        ])
        
        self.therapeutic_classes = self.pharmacy_config.get("therapeutic_classes", {
            "Analgesics": ["Opioids", "NSAIDs", "Acetaminophen", "COX-2 Inhibitors"],
            "Antihypertensives": ["ACE Inhibitors", "ARBs", "Beta Blockers", "Calcium Channel Blockers", "Diuretics"],
            "Antidiabetics": ["Biguanides", "Sulfonylureas", "DPP-4 Inhibitors", "SGLT2 Inhibitors", "Insulin"],
            "Antidepressants": ["SSRIs", "SNRIs", "TCAs", "MAOIs", "Atypical Antidepressants"],
            "Antipsychotics": ["Typical Antipsychotics", "Atypical Antipsychotics"],
            "Antibiotics": ["Penicillins", "Cephalosporins", "Macrolides", "Fluoroquinolones", "Tetracyclines"],
            "Anticoagulants": ["Heparins", "Direct Oral Anticoagulants", "Vitamin K Antagonists"],
            "Anticonvulsants": ["Sodium Channel Blockers", "GABA Analogs", "GABA Transaminase Inhibitors"],
            "Antineoplastics": ["Alkylating Agents", "Antimetabolites", "Topoisomerase Inhibitors", "Mitotic Inhibitors"],
            "Bronchodilators": ["Beta-2 Agonists", "Anticholinergics", "Methylxanthines"],
            "Corticosteroids": ["Inhaled Corticosteroids", "Oral Corticosteroids", "Topical Corticosteroids"],
            "Lipid-lowering": ["Statins", "Fibrates", "Bile Acid Sequestrants", "PCSK9 Inhibitors"],
            "Proton Pump Inhibitors": ["Proton Pump Inhibitors"],
            "Thyroid Hormones": ["Thyroid Hormones"],
            "Vaccines": ["Influenza Vaccines", "Pneumococcal Vaccines", "Hepatitis Vaccines", "COVID-19 Vaccines"]
        })
        
        self.medication_data = self.pharmacy_config.get("medication_data", {
            "Antihypertensives": {
                "ACE Inhibitors": [
                    {"name": "Lisinopril", "generic_name": "Lisinopril", "forms": ["Tablet"], "strengths": ["5 mg", "10 mg", "20 mg", "40 mg"]},
                    {"name": "Prinivil", "generic_name": "Lisinopril", "forms": ["Tablet"], "strengths": ["5 mg", "10 mg", "20 mg", "40 mg"]},
                    {"name": "Zestril", "generic_name": "Lisinopril", "forms": ["Tablet"], "strengths": ["5 mg", "10 mg", "20 mg", "40 mg"]}
                ],
                "ARBs": [
                    {"name": "Losartan", "generic_name": "Losartan", "forms": ["Tablet"], "strengths": ["25 mg", "50 mg", "100 mg"]},
                    {"name": "Cozaar", "generic_name": "Losartan", "forms": ["Tablet"], "strengths": ["25 mg", "50 mg", "100 mg"]},
                    {"name": "Valsartan", "generic_name": "Valsartan", "forms": ["Tablet"], "strengths": ["40 mg", "80 mg", "160 mg", "320 mg"]}
                ],
                "Beta Blockers": [
                    {"name": "Metoprolol Tartrate", "generic_name": "Metoprolol Tartrate", "forms": ["Tablet"], "strengths": ["25 mg", "50 mg", "100 mg"]},
                    {"name": "Lopressor", "generic_name": "Metoprolol Tartrate", "forms": ["Tablet"], "strengths": ["25 mg", "50 mg", "100 mg"]},
                    {"name": "Toprol XL", "generic_name": "Metoprolol Succinate", "forms": ["Extended-Release Tablet"], "strengths": ["25 mg", "50 mg", "100 mg", "200 mg"]}
                ]
            },
            "Antidiabetics": {
                "Biguanides": [
                    {"name": "Metformin", "generic_name": "Metformin", "forms": ["Tablet", "Extended-Release Tablet"], "strengths": ["500 mg", "850 mg", "1000 mg"]},
                    {"name": "Glucophage", "generic_name": "Metformin", "forms": ["Tablet"], "strengths": ["500 mg", "850 mg", "1000 mg"]},
                    {"name": "Glucophage XR", "generic_name": "Metformin", "forms": ["Extended-Release Tablet"], "strengths": ["500 mg", "750 mg"]}
                ],
                "SGLT2 Inhibitors": [
                    {"name": "Jardiance", "generic_name": "Empagliflozin", "forms": ["Tablet"], "strengths": ["10 mg", "25 mg"]},
                    {"name": "Invokana", "generic_name": "Canagliflozin", "forms": ["Tablet"], "strengths": ["100 mg", "300 mg"]},
                    {"name": "Farxiga", "generic_name": "Dapagliflozin", "forms": ["Tablet"], "strengths": ["5 mg", "10 mg"]}
                ],
                "Insulin": [
                    {"name": "Lantus", "generic_name": "Insulin Glargine", "forms": ["Solution"], "strengths": ["100 units/mL"]},
                    {"name": "Humalog", "generic_name": "Insulin Lispro", "forms": ["Solution"], "strengths": ["100 units/mL"]},
                    {"name": "Novolog", "generic_name": "Insulin Aspart", "forms": ["Solution"], "strengths": ["100 units/mL"]}
                ]
            },
            "Lipid-lowering": {
                "Statins": [
                    {"name": "Atorvastatin", "generic_name": "Atorvastatin", "forms": ["Tablet"], "strengths": ["10 mg", "20 mg", "40 mg", "80 mg"]},
                    {"name": "Lipitor", "generic_name": "Atorvastatin", "forms": ["Tablet"], "strengths": ["10 mg", "20 mg", "40 mg", "80 mg"]},
                    {"name": "Crestor", "generic_name": "Rosuvastatin", "forms": ["Tablet"], "strengths": ["5 mg", "10 mg", "20 mg", "40 mg"]}
                ],
                "PCSK9 Inhibitors": [
                    {"name": "Repatha", "generic_name": "Evolocumab", "forms": ["Solution"], "strengths": ["140 mg/mL"]},
                    {"name": "Praluent", "generic_name": "Alirocumab", "forms": ["Solution"], "strengths": ["75 mg/mL", "150 mg/mL"]}
                ]
            }
        })
        
        self.forms = self.pharmacy_config.get("forms", [
            "Tablet", "Capsule", "Solution", "Suspension", "Injection", "Cream", "Ointment",
            "Patch", "Inhaler", "Spray", "Extended-Release Tablet", "Extended-Release Capsule"
        ])
        
        self.routes = self.pharmacy_config.get("routes", [
            "Oral", "Intravenous", "Intramuscular", "Subcutaneous", "Topical",
            "Inhalation", "Nasal", "Ophthalmic", "Otic", "Rectal", "Vaginal", "Transdermal"
        ])
        
        self.pharmacy_names = self.pharmacy_config.get("pharmacy_names", [
            "CVS Pharmacy", "Walgreens", "Rite Aid", "Walmart Pharmacy", "Target Pharmacy",
            "Kroger Pharmacy", "Costco Pharmacy", "Sam's Club Pharmacy", "Publix Pharmacy",
            "Safeway Pharmacy", "Giant Pharmacy", "Albertsons Pharmacy", "Meijer Pharmacy"
        ])
        
    def generate_medications(self, count: int) -> List[Medication]:
        """
        Generate synthetic medications.
        
        Args:
            count: Number of medications to generate
            
        Returns:
            List of generated Medication objects
        """
        medications = []
        
        # Generate medications
        for _ in range(count):
            medication = Medication()
            
            # Select a random drug class and therapeutic class
            drug_class = random.choice(self.drug_classes)
            
            if drug_class in self.therapeutic_classes:
                therapeutic_class = random.choice(self.therapeutic_classes[drug_class])
            else:
                therapeutic_class = "Other"
            
            # Select a medication from the data if available
            selected_medication = None
            if drug_class in self.medication_data and therapeutic_class in self.medication_data[drug_class]:
                selected_medication = random.choice(self.medication_data[drug_class][therapeutic_class])
            
            if selected_medication:
                # Use data from the selected medication
                name = selected_medication["name"]
                generic_name = selected_medication["generic_name"]
                form = random.choice(selected_medication["forms"])
                strength = random.choice(selected_medication["strengths"])
            else:
                # Generate random medication data
                name = f"Med-{uuid.uuid4().hex[:6].upper()}"
                generic_name = f"Generic-{uuid.uuid4().hex[:6].upper()}"
                form = random.choice(self.forms)
                strength = f"{random.choice([5, 10, 20, 25, 50, 100, 150, 200, 250, 500])} mg"
            
            # Generate NDC
            ndc = f"{random.randint(10000, 99999)}-{random.randint(100, 999)}-{random.randint(10, 99)}"
            
            # Set basic info
            medication.set_basic_info(name, generic_name, ndc)
            
            # Set classification
            medication.set_classification(drug_class, therapeutic_class)
            
            # Set form info
            route = "Oral" if form in ["Tablet", "Capsule", "Solution", "Suspension"] else random.choice(self.routes)
            medication.set_form_info(form, strength, route)
            
            # Set formulary info
            tier = random.choices([1, 2, 3, 4], weights=[0.4, 0.3, 0.2, 0.1])[0]
            prior_auth_required = random.random() < 0.2
            
            quantity_limits = None
            if random.random() < 0.3:
                quantity_limits = {
                    "days_supply": random.choice([30, 60, 90]),
                    "quantity": random.randint(30, 180),
                    "refills": random.randint(0, 5)
                }
            
            step_therapy = random.random() < 0.15
            specialty = random.random() < 0.1
            
            medication.set_formulary_info(tier, prior_auth_required, quantity_limits, step_therapy, specialty)
            
            medications.append(medication)
        
        return medications
    
    def generate_formulary(self, medications: List[Medication]) -> Formulary:
        """
        Generate a synthetic formulary.
        
        Args:
            medications: List of medications to include in the formulary
            
        Returns:
            Generated Formulary object
        """
        formulary = Formulary()
        
        # Set basic info
        name = "Standard Formulary"
        effective_date = datetime.now() - timedelta(days=random.randint(30, 365))
        
        formulary.set_basic_info(name, effective_date)
        
        # Set tier structure
        tier_structure = {
            1: {
                "name": "Tier 1 - Generic",
                "description": "Lowest cost generic medications",
                "copay": random.choice([0, 5, 10]),
                "coinsurance": 0
            },
            2: {
                "name": "Tier 2 - Preferred Brand",
                "description": "Preferred brand-name medications",
                "copay": random.choice([20, 25, 30]),
                "coinsurance": 0
            },
            3: {
                "name": "Tier 3 - Non-Preferred Brand",
                "description": "Non-preferred brand-name medications",
                "copay": random.choice([40, 50, 60]),
                "coinsurance": 0
            },
            4: {
                "name": "Tier 4 - Specialty",
                "description": "High-cost specialty medications",
                "copay": 0,
                "coinsurance": random.choice([0.2, 0.25, 0.3, 0.4])
            }
        }
        
        formulary.set_tier_structure(tier_structure)
        
        # Add medications to formulary
        for medication in medications:
            # 90% of medications are included in the formulary
            if random.random() < 0.9:
                formulary.add_medication(medication.to_dict())
            else:
                # 10% are excluded
                exclusion_reasons = [
                    "Not medically necessary",
                    "Therapeutic alternative available",
                    "Not cost-effective",
                    "Insufficient clinical evidence",
                    "Safety concerns"
                ]
                
                formulary.add_exclusion(medication.id, random.choice(exclusion_reasons))
        
        return formulary
    
    def generate_pharmacy_claims(self, count: int, members: List[Dict[str, Any]], 
                                medications: List[Medication]) -> List[PharmacyClaim]:
        """
        Generate synthetic pharmacy claims.
        
        Args:
            count: Number of claims to generate
            members: List of member dictionaries to associate claims with
            medications: List of medications to use in claims
            
        Returns:
            List of generated PharmacyClaim objects
        """
        claims = []
        
        # Ensure we have members and medications to work with
        if not members or not medications:
            return claims
        
        # Generate pharmacy claims
        for _ in range(count):
            claim = PharmacyClaim()
            
            # Select a random member
            member = random.choice(members)
            member_id = member.get("id")
            
            # Select a random medication
            medication = random.choice(medications)
            medication_id = medication.id
            
            # Generate pharmacy ID
            pharmacy_name = random.choice(self.pharmacy_names)
            pharmacy_id = f"PHARM{uuid.uuid4().hex[:8].upper()}"
            
            # Generate prescriber ID
            prescriber_id = f"PRV{random.randint(10000, 99999)}"
            
            # Set basic info
            claim.set_basic_info(member_id, medication_id, pharmacy_id, prescriber_id)
            
            # Set fill info
            fill_date = datetime.now() - timedelta(days=random.randint(1, 180))
            days_supply = random.choice([30, 60, 90])
            
            # Calculate quantity based on days supply
            if medication.form in ["Tablet", "Capsule", "Extended-Release Tablet", "Extended-Release Capsule"]:
                # Typically 1-3 units per day
                daily_units = random.choice([1, 2, 3])
                quantity = days_supply * daily_units
            elif medication.form in ["Solution", "Suspension"]:
                # Typically measured in mL
                quantity = random.choice([120, 240, 480])
            elif medication.form in ["Inhaler", "Spray"]:
                # Typically 1-2 inhalers
                quantity = random.choice([1, 2])
            else:
                # Default quantity
                quantity = random.randint(1, 5)
            
            refill_number = random.randint(0, 5)
            total_refills = random.randint(refill_number, 11)
            
            claim.set_fill_info(fill_date, days_supply, quantity, refill_number, total_refills)
            
            # Set drug info
            claim.set_drug_info(medication.ndc, medication.name, medication.tier)
            
            # Set cost info
            # Base cost depends on tier
            if medication.tier == 1:
                base_cost = random.uniform(5, 50)
            elif medication.tier == 2:
                base_cost = random.uniform(50, 200)
            elif medication.tier == 3:
                base_cost = random.uniform(200, 500)
            else:  # Tier 4 (Specialty)
                base_cost = random.uniform(500, 5000)
            
            # Adjust cost based on quantity and days supply
            total_cost = base_cost * (days_supply / 30)
            
            # Calculate member cost based on tier
            if medication.tier == 1:
                member_cost = random.choice([0, 5, 10])
            elif medication.tier == 2:
                member_cost = random.choice([20, 25, 30])
            elif medication.tier == 3:
                member_cost = random.choice([40, 50, 60])
            else:  # Tier 4 (Specialty)
                member_cost = total_cost * random.choice([0.2, 0.25, 0.3, 0.4])
            
            # Ensure member cost doesn't exceed total cost
            member_cost = min(member_cost, total_cost)
            
            # Calculate plan paid amount
            plan_paid = total_cost - member_cost
            
            claim.set_cost_info(total_cost, member_cost, plan_paid)
            
            # Set status
            status = random.choices(["paid", "rejected", "reversed"], weights=[0.9, 0.07, 0.03])[0]
            
            rejection_reason = None
            if status == "rejected":
                rejection_reasons = [
                    "Prior authorization required",
                    "Refill too soon",
                    "Quantity limit exceeded",
                    "Non-formulary medication",
                    "Step therapy required",
                    "Invalid member ID",
                    "Coverage terminated"
                ]
                rejection_reason = random.choice(rejection_reasons)
            
            claim.set_status(status, rejection_reason)
            
            claims.append(claim)
        
        return claims
    
    def generate(self, medication_count: int, claim_count: int, members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a synthetic pharmacy benefit.
        
        Args:
            medication_count: Number of medications to generate
            claim_count: Number of pharmacy claims to generate
            members: List of member dictionaries to associate claims with
            
        Returns:
            Dictionary containing the generated pharmacy benefit data
        """
        # Generate medications
        medications = self.generate_medications(medication_count)
        
        # Generate formulary
        formulary = self.generate_formulary(medications)
        
        # Generate pharmacy claims
        claims = self.generate_pharmacy_claims(claim_count, members, medications)
        
        # Convert to dictionaries
        medication_dicts = [medication.to_dict() for medication in medications]
        formulary_dict = formulary.to_dict()
        claim_dicts = [claim.to_dict() for claim in claims]
        
        return {
            "medications": medication_dicts,
            "formulary": formulary_dict,
            "pharmacy_claims": claim_dicts
        }