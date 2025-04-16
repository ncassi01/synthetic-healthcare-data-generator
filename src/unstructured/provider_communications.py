"""
Provider-to-provider communications generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic communications between healthcare providers
such as referrals, consults, and other professional exchanges.
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


class ProviderCommunicationsGenerator(BaseGenerator):
    """Generator for synthetic provider-to-provider communications."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the provider communications generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract configuration
        self.provider_comm_config = config.get('provider_communications_config', {})
        
    def generate(self, count: int, member_ids: List[str] = None, provider_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic provider-to-provider communications.
        
        Args:
            count: Number of communications to generate.
            member_ids: Optional list of member IDs to associate with the communications.
                If not provided, random IDs will be generated.
            provider_ids: Optional list of provider IDs to use as senders and recipients.
                If not provided, random IDs will be generated.
                
        Returns:
            List of generated provider communication entries.
        """
        self.logger.info(f"Generating {count} provider-to-provider communications")
        
        if member_ids is None:
            # Generate random member IDs if not provided
            member_ids = [f"MEM{i:08d}" for i in range(count)]
        
        if provider_ids is None:
            # Generate random provider IDs if not provided
            provider_ids = [f"PRV{i:08d}" for i in range(20)]  # Generate 20 providers
        
        # If fewer member IDs than count, repeat member IDs
        if len(member_ids) < count:
            member_ids = (member_ids * (count // len(member_ids) + 1))[:count]
        
        communications = []
        
        # Generate different types of provider communications
        comm_types = ['referral', 'consult_request', 'consult_response', 'transfer_of_care', 'care_coordination']
        
        for i in range(count):
            comm_type = random.choice(comm_types)
            
            if comm_type == 'referral':
                comm = self._generate_referral(member_ids[i], provider_ids)
            elif comm_type == 'consult_request':
                comm = self._generate_consult_request(member_ids[i], provider_ids)
            elif comm_type == 'consult_response':
                comm = self._generate_consult_response(member_ids[i], provider_ids)
            elif comm_type == 'transfer_of_care':
                comm = self._generate_transfer_of_care(member_ids[i], provider_ids)
            elif comm_type == 'care_coordination':
                comm = self._generate_care_coordination(member_ids[i], provider_ids)
            
            communications.append(comm)
            
        self.logger.info(f"Generated {len(communications)} provider-to-provider communications")
        return communications
    
    def _generate_referral(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a provider referral communication."""
        # Select random sending and receiving providers
        sender_id = random.choice(provider_ids)
        recipient_id = random.choice([p for p in provider_ids if p != sender_id])
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Specialties
        specialties = [
            "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology", 
            "Hematology", "Infectious Disease", "Nephrology", "Neurology", 
            "Oncology", "Orthopedics", "Pulmonology", "Rheumatology", 
            "Urology", "Psychiatry", "Pain Management"
        ]
        
        # Reasons for referral
        referral_reasons = [
            "Consultation", "Procedure", "Second opinion", "Specialized care",
            "Diagnostic testing", "Treatment", "Follow-up", "Evaluation"
        ]
        
        # Generate specialty for recipient
        recipient_specialty = random.choice(specialties)
        
        # Generate reason for referral
        reason = random.choice(referral_reasons)
        
        # Generate urgency
        urgency = random.choice(["Routine", "Urgent", "STAT"])
        
        # Generate clinical information
        diagnoses = [
            "Hypertension", "Type 2 Diabetes", "Asthma", "Obesity", 
            "Depression", "Anxiety", "GERD", "Osteoarthritis",
            "Hyperlipidemia", "Hypothyroidism", "Allergic Rhinitis",
            "Migraine", "Insomnia", "Back Pain", "Osteoporosis"
        ]
        
        selected_diagnoses = random.sample(diagnoses, random.randint(1, 3))
        
        # Generate clinical summary
        clinical_summary = self._generate_clinical_summary(selected_diagnoses)
        
        return {
            "id": f"REF{random.randint(10000, 99999)}",
            "type": "referral",
            "member_id": member_id,
            "sender_id": sender_id,
            "sender_name": f"Dr. {self.faker.last_name()}",
            "sender_specialty": "Primary Care",
            "recipient_id": recipient_id,
            "recipient_name": f"Dr. {self.faker.last_name()}",
            "recipient_specialty": recipient_specialty,
            "date": comm_date.strftime("%Y-%m-%d"),
            "time": comm_date.strftime("%H:%M"),
            "reason_for_referral": reason,
            "urgency": urgency,
            "diagnoses": selected_diagnoses,
            "clinical_summary": clinical_summary,
            "questions_for_consultant": self._generate_referral_questions(recipient_specialty),
            "requested_services": self._generate_requested_services(recipient_specialty),
            "attachments": self._generate_attachments() if random.random() > 0.7 else [],
            "notes": self.faker.paragraph() if random.random() > 0.5 else ""
        }
    
    def _generate_consult_request(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a consultation request communication."""
        # Select random sending and receiving providers
        sender_id = random.choice(provider_ids)
        recipient_id = random.choice([p for p in provider_ids if p != sender_id])
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Specialties
        specialties = [
            "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology", 
            "Hematology", "Infectious Disease", "Nephrology", "Neurology", 
            "Oncology", "Orthopedics", "Pulmonology", "Rheumatology", 
            "Urology", "Psychiatry", "Pain Management"
        ]
        
        # Generate specialty for recipient
        recipient_specialty = random.choice(specialties)
        
        # Generate clinical question
        clinical_questions = [
            f"Please evaluate for {random.choice(['possible', 'suspected', 'confirmed'])} {self.faker.word()}",
            f"Would you recommend {random.choice(['starting', 'adjusting', 'discontinuing'])} {self.faker.word()} therapy?",
            f"Please assess {random.choice(['risk', 'benefit', 'appropriateness'])} of {self.faker.word()} in this patient",
            f"What is your interpretation of these {random.choice(['findings', 'results', 'symptoms'])}?",
            f"Would you recommend further {random.choice(['testing', 'imaging', 'evaluation'])}?"
        ]
        
        clinical_question = random.choice(clinical_questions)
        
        # Generate diagnoses
        diagnoses = [
            "Hypertension", "Type 2 Diabetes", "Asthma", "Obesity", 
            "Depression", "Anxiety", "GERD", "Osteoarthritis",
            "Hyperlipidemia", "Hypothyroidism", "Allergic Rhinitis",
            "Migraine", "Insomnia", "Back Pain", "Osteoporosis"
        ]
        
        selected_diagnoses = random.sample(diagnoses, random.randint(1, 3))
        
        # Generate clinical summary
        clinical_summary = self._generate_clinical_summary(selected_diagnoses)
        
        return {
            "id": f"CREQ{random.randint(10000, 99999)}",
            "type": "consult_request",
            "member_id": member_id,
            "sender_id": sender_id,
            "sender_name": f"Dr. {self.faker.last_name()}",
            "sender_specialty": "Primary Care",
            "recipient_id": recipient_id,
            "recipient_name": f"Dr. {self.faker.last_name()}",
            "recipient_specialty": recipient_specialty,
            "date": comm_date.strftime("%Y-%m-%d"),
            "time": comm_date.strftime("%H:%M"),
            "clinical_question": clinical_question,
            "urgency": random.choice(["Routine", "Urgent", "STAT"]),
            "diagnoses": selected_diagnoses,
            "clinical_summary": clinical_summary,
            "relevant_history": self._generate_relevant_history(),
            "current_medications": self._generate_medications(),
            "recent_results": self._generate_recent_results(),
            "attachments": self._generate_attachments() if random.random() > 0.7 else [],
            "notes": self.faker.paragraph() if random.random() > 0.5 else ""
        }
    
    def _generate_consult_response(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a consultation response communication."""
        # Select random sending and receiving providers
        recipient_id = random.choice(provider_ids)
        sender_id = random.choice([p for p in provider_ids if p != recipient_id])
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Specialties
        specialties = [
            "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology", 
            "Hematology", "Infectious Disease", "Nephrology", "Neurology", 
            "Oncology", "Orthopedics", "Pulmonology", "Rheumatology", 
            "Urology", "Psychiatry", "Pain Management"
        ]
        
        # Generate specialty for sender
        sender_specialty = random.choice(specialties)
        
        # Generate diagnoses
        diagnoses = [
            "Hypertension", "Type 2 Diabetes", "Asthma", "Obesity", 
            "Depression", "Anxiety", "GERD", "Osteoarthritis",
            "Hyperlipidemia", "Hypothyroidism", "Allergic Rhinitis",
            "Migraine", "Insomnia", "Back Pain", "Osteoporosis"
        ]
        
        selected_diagnoses = random.sample(diagnoses, random.randint(1, 3))
        
        # Generate assessment
        assessment = self._generate_assessment(selected_diagnoses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sender_specialty)
        
        return {
            "id": f"CRES{random.randint(10000, 99999)}",
            "type": "consult_response",
            "member_id": member_id,
            "sender_id": sender_id,
            "sender_name": f"Dr. {self.faker.last_name()}",
            "sender_specialty": sender_specialty,
            "recipient_id": recipient_id,
            "recipient_name": f"Dr. {self.faker.last_name()}",
            "recipient_specialty": "Primary Care",
            "date": comm_date.strftime("%Y-%m-%d"),
            "time": comm_date.strftime("%H:%M"),
            "reference_consult_id": f"CREQ{random.randint(10000, 99999)}",
            "diagnoses": selected_diagnoses,
            "assessment": assessment,
            "recommendations": recommendations,
            "follow_up_plan": self._generate_follow_up_plan(),
            "additional_testing": self._generate_additional_testing() if random.random() > 0.5 else [],
            "medication_changes": self._generate_medication_changes() if random.random() > 0.6 else [],
            "attachments": self._generate_attachments() if random.random() > 0.7 else [],
            "notes": self.faker.paragraph() if random.random() > 0.5 else ""
        }
    
    def _generate_transfer_of_care(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a transfer of care communication."""
        # Select random sending and receiving providers
        sender_id = random.choice(provider_ids)
        recipient_id = random.choice([p for p in provider_ids if p != sender_id])
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Generate reason for transfer
        transfer_reasons = [
            "Patient relocation", "Provider retirement", "Specialist care needed",
            "Insurance change", "Patient request", "Practice closure",
            "Transition from pediatric to adult care", "Transition to long-term care"
        ]
        
        reason = random.choice(transfer_reasons)
        
        # Generate diagnoses
        diagnoses = [
            "Hypertension", "Type 2 Diabetes", "Asthma", "Obesity", 
            "Depression", "Anxiety", "GERD", "Osteoarthritis",
            "Hyperlipidemia", "Hypothyroidism", "Allergic Rhinitis",
            "Migraine", "Insomnia", "Back Pain", "Osteoporosis"
        ]
        
        selected_diagnoses = random.sample(diagnoses, random.randint(1, 3))
        
        # Generate clinical summary
        clinical_summary = self._generate_clinical_summary(selected_diagnoses)
        
        return {
            "id": f"TOC{random.randint(10000, 99999)}",
            "type": "transfer_of_care",
            "member_id": member_id,
            "sender_id": sender_id,
            "sender_name": f"Dr. {self.faker.last_name()}",
            "sender_specialty": "Primary Care",
            "recipient_id": recipient_id,
            "recipient_name": f"Dr. {self.faker.last_name()}",
            "recipient_specialty": "Primary Care",
            "date": comm_date.strftime("%Y-%m-%d"),
            "time": comm_date.strftime("%H:%M"),
            "reason_for_transfer": reason,
            "diagnoses": selected_diagnoses,
            "clinical_summary": clinical_summary,
            "active_problems": self._generate_active_problems(),
            "current_medications": self._generate_medications(),
            "allergies": self._generate_allergies(),
            "recent_results": self._generate_recent_results(),
            "pending_tests": self._generate_pending_tests() if random.random() > 0.7 else [],
            "care_plan": self._generate_care_plan(),
            "social_history": self._generate_social_history() if random.random() > 0.6 else "",
            "family_history": self._generate_family_history() if random.random() > 0.6 else "",
            "attachments": self._generate_attachments() if random.random() > 0.7 else [],
            "notes": self.faker.paragraph() if random.random() > 0.5 else ""
        }
    
    def _generate_care_coordination(self, member_id: str, provider_ids: List[str]) -> Dict[str, Any]:
        """Generate a care coordination communication."""
        # Select random sending and receiving providers
        sender_id = random.choice(provider_ids)
        recipient_id = random.choice([p for p in provider_ids if p != sender_id])
        
        # Generate random date within the last 90 days
        comm_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Generate coordination type
        coordination_types = [
            "Care plan update", "Medication reconciliation", "Post-discharge follow-up",
            "Care team meeting summary", "Care gap notification", "Treatment adherence",
            "Social needs coordination", "Behavioral health integration"
        ]
        
        coordination_type = random.choice(coordination_types)
        
        # Generate diagnoses
        diagnoses = [
            "Hypertension", "Type 2 Diabetes", "Asthma", "Obesity", 
            "Depression", "Anxiety", "GERD", "Osteoarthritis",
            "Hyperlipidemia", "Hypothyroidism", "Allergic Rhinitis",
            "Migraine", "Insomnia", "Back Pain", "Osteoporosis"
        ]
        
        selected_diagnoses = random.sample(diagnoses, random.randint(1, 3))
        
        return {
            "id": f"CC{random.randint(10000, 99999)}",
            "type": "care_coordination",
            "member_id": member_id,
            "sender_id": sender_id,
            "sender_name": f"Dr. {self.faker.last_name()}",
            "sender_specialty": random.choice(["Primary Care", "Care Management", "Social Work", "Nursing"]),
            "recipient_id": recipient_id,
            "recipient_name": f"Dr. {self.faker.last_name()}",
            "recipient_specialty": random.choice(["Primary Care", "Cardiology", "Endocrinology", "Psychiatry"]),
            "date": comm_date.strftime("%Y-%m-%d"),
            "time": comm_date.strftime("%H:%M"),
            "coordination_type": coordination_type,
            "diagnoses": selected_diagnoses,
            "current_status": self._generate_current_status(),
            "care_team_members": self._generate_care_team_members(provider_ids),
            "action_items": self._generate_action_items(),
            "barriers_to_care": self._generate_barriers_to_care() if random.random() > 0.6 else [],
            "patient_goals": self._generate_patient_goals() if random.random() > 0.7 else [],
            "next_review_date": (datetime.now() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
            "attachments": self._generate_attachments() if random.random() > 0.7 else [],
            "notes": self.faker.paragraph() if random.random() > 0.5 else ""
        }
    
    def _generate_clinical_summary(self, diagnoses: List[str]) -> str:
        """Generate a clinical summary based on diagnoses."""
        summary_parts = []
        
        # Add introduction
        summary_parts.append(f"Patient with {', '.join(diagnoses[:-1]) + ' and ' + diagnoses[-1] if len(diagnoses) > 1 else diagnoses[0]}.")
        
        # Add details for each diagnosis
        for diagnosis in diagnoses:
            if diagnosis == "Hypertension":
                summary_parts.append(f"Hypertension {random.choice(['well-controlled', 'poorly controlled', 'with recent medication adjustment'])}. BP averaging {random.randint(110, 170)}/{random.randint(60, 100)}.")
            elif diagnosis == "Type 2 Diabetes":
                summary_parts.append(f"Type 2 Diabetes {random.choice(['well-controlled', 'poorly controlled', 'with recent medication adjustment'])}. Last A1c {random.uniform(5.5, 11.0):.1f}%.")
            elif diagnosis == "Asthma":
                summary_parts.append(f"Asthma {random.choice(['well-controlled', 'with occasional exacerbations', 'requiring frequent rescue inhaler use'])}.")
            elif diagnosis == "Depression":
                summary_parts.append(f"Depression {random.choice(['well-controlled on current regimen', 'with ongoing symptoms', 'recently started on therapy'])}.")
            else:
                summary_parts.append(f"{diagnosis} {random.choice(['stable', 'improving', 'worsening', 'requiring ongoing management'])}.")
        
        # Add recent events if applicable
        if random.random() > 0.7:
            events = [
                f"Recent ED visit for {self.faker.word()} on {(datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')}.",
                f"Hospitalized for {self.faker.word()} from {(datetime.now() - timedelta(days=random.randint(10, 60))).strftime('%Y-%m-%d')} to {(datetime.now() - timedelta(days=random.randint(1, 9))).strftime('%Y-%m-%d')}.",
                f"Recent {random.choice(['surgery', 'procedure', 'imaging study'])} on {(datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')}."
            ]
            summary_parts.append(random.choice(events))
        
        return " ".join(summary_parts)
    
    def _generate_referral_questions(self, specialty: str) -> List[str]:
        """Generate questions for a referral based on specialty."""
        questions = []
        
        # Generic questions
        generic_questions = [
            "Please evaluate and recommend appropriate treatment.",
            "Would you recommend any additional testing?",
            "What is your assessment of the current treatment plan?"
        ]
        
        # Add 1-2 generic questions
        questions.extend(random.sample(generic_questions, random.randint(1, 2)))
        
        # Add specialty-specific question if applicable
        if specialty == "Cardiology":
            questions.append(random.choice([
                "Is a cardiac stress test indicated?",
                "Please evaluate for possible coronary artery disease.",
                "Would you recommend anticoagulation therapy?"
            ]))
        elif specialty == "Gastroenterology":
            questions.append(random.choice([
                "Is colonoscopy indicated at this time?",
                "Please evaluate for possible inflammatory bowel disease.",
                "What dietary modifications would you recommend?"
            ]))
        elif specialty == "Neurology":
            questions.append(random.choice([
                "Please evaluate for possible seizure disorder.",
                "Is neuroimaging indicated?",
                "Would you recommend migraine prophylaxis?"
            ]))
        
        return questions
    
    def _generate_requested_services(self, specialty: str) -> List[str]:
        """Generate requested services for a referral based on specialty."""
        # Generic services
        generic_services = [
            "Consultation and recommendations",
            "Follow-up care as needed",
            "Patient education"
        ]
        
        # Specialty-specific services
        specialty_services = {
            "Cardiology": [
                "Echocardiogram", "Stress test", "Holter monitor", 
                "Cardiac catheterization", "Arrhythmia evaluation"
            ],
            "Dermatology": [
                "Skin biopsy", "Lesion removal", "Patch testing",
                "Phototherapy", "Dermatopathology review"
            ],
            "Gastroenterology": [
                "Colonoscopy", "Upper endoscopy", "ERCP",
                "Capsule endoscopy", "Breath testing"
            ],
            "Neurology": [
                "EEG", "EMG/NCS", "Lumbar puncture",
                "Neuroimaging interpretation", "Botox injections"
            ],
            "Orthopedics": [
                "Joint injection", "Fracture management", "Arthroscopy",
                "Casting/splinting", "Surgical evaluation"
            ]
        }
        
        # Select 1-2 generic services
        services = random.sample(generic_services, random.randint(1, 2))
        
        # Add 1-2 specialty-specific services if available
        if specialty in specialty_services:
            services.extend(random.sample(specialty_services[specialty], random.randint(1, 2)))
        
        return services
    
    def _generate_attachments(self) -> List[Dict[str, str]]:
        """Generate a list of attachments."""
        attachment_types = [
            "Lab results", "Imaging report", "Progress note", 
            "Discharge summary", "Procedure report", "Pathology report",
            "Medication list", "Prior authorization", "Consultation note"
        ]
        
        # Generate 1-3 attachments
        num_attachments = random.randint(1, 3)
        
        attachments = []
        for _ in range(num_attachments):
            attachment_type = random.choice(attachment_types)
            date = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            
            attachments.append({
                "type": attachment_type,
                "date": date,
                "filename": f"{attachment_type.lower().replace(' ', '_')}_{date}.pdf",
                "size": f"{random.randint(100, 5000)} KB"
            })
        
        return attachments
    
    def _generate_relevant_history(self) -> str:
        """Generate relevant medical history."""
        history_parts = []
        
        # Past medical history
        past_conditions = [
            "Myocardial infarction", "Stroke", "Pulmonary embolism", 
            "Deep vein thrombosis", "Pneumonia", "Appendectomy",
            "Cholecystectomy", "Hysterectomy", "Tonsillectomy",
            "Fracture", "Cancer", "Seizure disorder"
        ]
        
        # Select 0-3 past conditions
        selected_past = random.sample(past_conditions, random.randint(0, 3))
        
        if selected_past:
            history_parts.append(f"Past Medical History: {', '.join(selected_past)}.")
        
        # Surgical history
        surgeries = [
            "Appendectomy", "Cholecystectomy", "Hysterectomy", 
            "Tonsillectomy", "Hernia repair", "Joint replacement",
            "CABG", "Cesarean section", "Spinal fusion"
        ]
        
        # Select 0-2 surgeries
        selected_surgeries = random.sample(surgeries, random.randint(0, 2))
        
        if selected_surgeries:
            dates = [(datetime.now() - timedelta(days=random.randint(365, 3650))).year for _ in selected_surgeries]
            surgery_with_dates = [f"{s} ({d})" for s, d in zip(selected_surgeries, dates)]
            history_parts.append(f"Surgical History: {', '.join(surgery_with_dates)}.")
        
        # Add other relevant information
        if random.random() > 0.7:
            other_info = random.choice([
                f"Patient has been followed for this condition since {(datetime.now() - timedelta(days=random.randint(365, 3650))).year}.",
                "Patient has had multiple medication trials with limited success.",
                "Patient reports gradual worsening of symptoms over the past several months.",
                "Patient has been hospitalized twice in the past year for this condition."
            ])
            history_parts.append(other_info)
        
        return " ".join(history_parts)
    
    def _generate_medications(self) -> List[Dict[str, Any]]:
        """Generate a list of current medications."""
        medications = [
            {"name": "Lisinopril", "dose": "10 mg", "frequency": "daily"},
            {"name": "Metformin", "dose": "500 mg", "frequency": "twice daily"},
            {"name": "Atorvastatin", "dose": "20 mg", "frequency": "daily at bedtime"},
            {"name": "Levothyroxine", "dose": "88 mcg", "frequency": "daily"},
            {"name": "Amlodipine", "dose": "5 mg", "frequency": "daily"},
            {"name": "Omeprazole", "dose": "20 mg", "frequency": "daily"},
            {"name": "Sertraline", "dose": "50 mg", "frequency": "daily"},
            {"name": "Albuterol", "dose": "90 mcg", "frequency": "as needed"},
            {"name": "Montelukast", "dose": "10 mg", "frequency": "daily at bedtime"},
            {"name": "Hydrochlorothiazide", "dose": "25 mg", "frequency": "daily"},
            {"name": "Gabapentin", "dose": "300 mg", "frequency": "three times daily"},
            {"name": "Fluticasone", "dose": "50 mcg", "frequency": "1 spray each nostril daily"}
        ]
        
        # Select 0-5 medications
        num_meds = random.randint(0, 5)
        
        if num_meds == 0:
            return []
        
        return random.sample(medications, num_meds)
    
    def _generate_recent_results(self) -> List[Dict[str, Any]]:
        """Generate recent test results."""
        result_types = [
            {"type": "CBC", "components": [
                {"name": "WBC", "value": f"{random.uniform(4.0, 11.0):.1f}", "unit": "K/uL", "reference": "4.5-11.0"},
                {"name": "Hgb", "value": f"{random.uniform(12.0, 17.0):.1f}", "unit": "g/dL", "reference": "12.0-16.0"},
                {"name": "Plt", "value": f"{random.randint(150, 400)}", "unit": "K/uL", "reference": "150-400"}
            ]},
            {"type": "CMP", "components": [
                {"name": "Glucose", "value": f"{random.uniform(70, 180):.0f}", "unit": "mg/dL", "reference": "70-99"},
                {"name": "Creatinine", "value": f"{random.uniform(0.6, 1.4):.1f}", "unit": "mg/dL", "reference": "0.6-1.2"},
                {"name": "ALT", "value": f"{random.uniform(10, 50):.0f}", "unit": "U/L", "reference": "7-56"}
            ]},
            {"type": "Lipid Panel", "components": [
                {"name": "Total Cholesterol", "value": f"{random.uniform(120, 250):.0f}", "unit": "mg/dL", "reference": "<200"},
                {"name": "LDL", "value": f"{random.uniform(70, 180):.0f}", "unit": "mg/dL", "reference": "<100"},
                {"name": "HDL", "value": f"{random.uniform(35, 80):.0f}", "unit": "mg/dL", "reference": ">40"}
            ]},
            {"type": "HbA1c", "components": [
                {"name": "HbA1c", "value": f"{random.uniform(5.0, 10.0):.1f}", "unit": "%", "reference": "<5.7"}
            ]},
            {"type": "Thyroid Panel", "components": [
                {"name": "TSH", "value": f"{random.uniform(0.5, 5.0):.2f}", "unit": "mIU/L", "reference": "0.4-4.0"},
                {"name": "Free T4", "value": f"{random.uniform(0.8, 1.8):.1f}", "unit": "ng/dL", "reference": "0.8-1.8"}
            ]},
            {"type": "Urinalysis", "components": [
                {"name": "Protein", "value": random.choice(["Negative", "Trace", "1+", "2+"]), "unit": "", "reference": "Negative"},
                {"name": "Glucose", "value": random.choice(["Negative", "Trace", "1+", "2+"]), "unit": "", "reference": "Negative"},
                {"name": "WBC", "value": f"{random.randint(0, 10)}-{random.randint(0, 5)}", "unit": "/hpf", "reference": "0-5"}
            ]}
        ]
        
        # Select 0-3 result types
        num_results = random.randint(0, 3)
        
        if num_results == 0:
            return []
        
        results = random.sample(result_types, num_results)
        
        # Add dates to results
        for result in results:
            result["date"] = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
        
        return results
    
    def _generate_assessment(self, diagnoses: List[str]) -> str:
        """Generate an assessment based on diagnoses."""
        assessment_parts = []
        
        # Add introduction
        assessment_parts.append(f"I evaluated the patient with {', '.join(diagnoses[:-1]) + ' and ' + diagnoses[-1] if len(diagnoses) > 1 else diagnoses[0]}.")
        
        # Add details for each diagnosis
        for diagnosis in diagnoses:
            if diagnosis == "Hypertension":
                assessment_parts.append(f"Hypertension appears {random.choice(['well-controlled', 'poorly controlled', 'partially controlled'])} on current regimen.")
            elif diagnosis == "Type 2 Diabetes":
                assessment_parts.append(f"Diabetes is {random.choice(['well-controlled', 'poorly controlled', 'partially controlled'])} with A1c of {random.uniform(5.5, 11.0):.1f}%.")
            elif diagnosis == "Asthma":
                assessment_parts.append(f"Asthma is {random.choice(['well-controlled', 'poorly controlled', 'partially controlled'])} with {random.choice(['no', 'infrequent', 'frequent'])} exacerbations.")
            elif diagnosis == "Depression":
                assessment_parts.append(f"Depression symptoms are {random.choice(['minimal', 'mild', 'moderate', 'severe'])} at this time.")
            else:
                assessment_parts.append(f"{diagnosis} is {random.choice(['stable', 'improving', 'worsening', 'requiring adjustment in management'])}.")
        
        # Add overall impression
        overall_impressions = [
            "Overall, the patient is clinically stable.",
            "The patient would benefit from medication adjustments as outlined below.",
            "Further diagnostic evaluation is recommended.",
            "Current management appears appropriate, but close monitoring is advised."
        ]
        
        assessment_parts.append(random.choice(overall_impressions))
        
        return " ".join(assessment_parts)
    
    def _generate_recommendations(self, specialty: str) -> List[str]:
        """Generate recommendations based on specialty."""
        # Generic recommendations
        generic_recommendations = [
            "Continue current medications with no changes.",
            "Follow up with primary care provider in 3 months.",
            "Obtain repeat laboratory studies in 3-6 months."
        ]
        
        # Specialty-specific recommendations
        specialty_recommendations = {
            "Cardiology": [
                "Increase lisinopril to 20 mg daily.",
                "Add low-dose aspirin 81 mg daily.",
                "Obtain echocardiogram to assess cardiac function.",
                "Consider stress test to evaluate for ischemia."
            ],
            "Endocrinology": [
                "Increase metformin to 1000 mg twice daily.",
                "Add SGLT2 inhibitor to regimen.",
                "Check hemoglobin A1c in 3 months.",
                "Refer to diabetes education program."
            ],
            "Gastroenterology": [
                "Schedule colonoscopy for further evaluation.",
                "Trial of proton pump inhibitor therapy.",
                "Dietary modifications including low FODMAP diet.",
                "Obtain abdominal ultrasound."
            ],
            "Neurology": [
                "Start prophylactic therapy with topiramate 25 mg daily, titrate as directed.",
                "Obtain MRI brain without contrast.",
                "Consider EEG to evaluate for seizure activity.",
                "Neurocognitive testing is recommended."
            ],
            "Pulmonology": [
                "Add inhaled corticosteroid to current regimen.",
                "Obtain pulmonary function tests.",
                "Consider sleep study to evaluate for sleep apnea.",
                "Smoking cessation strongly recommended."
            ]
        }
        
        # Select 1-2 generic recommendations
        recommendations = random.sample(generic_recommendations, random.randint(1, 2))
        
        # Add 1-3 specialty-specific recommendations if available
        if specialty in specialty_recommendations:
            recommendations.extend(random.sample(specialty_recommendations[specialty], random.randint(1, 3)))
        
        return recommendations
    
    def _generate_follow_up_plan(self) -> Dict[str, Any]:
        """Generate a follow-up plan."""
        return {
            "timing": f"{random.randint(1, 6)} {random.choice(['weeks', 'months'])}",
            "provider": random.choice(["Primary care", "Specialist", "Either primary care or specialist"]),
            "tests_before_visit": random.sample([
                "Repeat comprehensive metabolic panel",
                "Repeat complete blood count",
                "Repeat hemoglobin A1c",
                "Repeat lipid panel",
                "Repeat thyroid studies",
                "Repeat urinalysis"
            ], random.randint(0, 3)) if random.random() > 0.5 else []
        }
    
    def _generate_additional_testing(self) -> List[str]:
        """Generate recommended additional testing."""
        tests = [
            "Echocardiogram", "Stress test", "Holter monitor",
            "Sleep study", "Pulmonary function tests", "CT scan",
            "MRI", "Ultrasound", "Endoscopy", "Colonoscopy",
            "Bone density scan", "EMG/NCS", "EEG"
        ]
        
        # Select 1-3 tests
        num_tests = random.randint(1, 3)
        
        return random.sample(tests, num_tests)
    
    def _generate_medication_changes(self) -> List[Dict[str, str]]:
        """Generate medication changes."""
        changes = []
        
        change_types = ["Start", "Increase", "Decrease", "Stop", "Switch"]
        medications = [
            "Lisinopril", "Metformin", "Atorvastatin", "Amlodipine",
            "Sertraline", "Omeprazole", "Gabapentin", "Hydrochlorothiazide",
            "Levothyroxine", "Montelukast", "Fluticasone"
        ]
        
        # Generate 1-3 changes
        num_changes = random.randint(1, 3)
        
        for _ in range(num_changes):
            change_type = random.choice(change_types)
            medication = random.choice(medications)
            
            if change_type == "Start":
                changes.append({
                    "type": "Start",
                    "medication": medication,
                    "dose": f"{random.choice(['10', '20', '25', '50', '100'])} {random.choice(['mg', 'mcg'])}",
                    "frequency": random.choice(["daily", "twice daily", "three times daily", "as needed"]),
                    "reason": f"For {random.choice(['better control', 'symptom management', 'prevention'])}"
                })
            elif change_type == "Stop":
                changes.append({
                    "type": "Stop",
                    "medication": medication,
                    "reason": random.choice([
                        "No longer indicated", 
                        "Side effects", 
                        "Lack of efficacy",
                        "Being replaced with alternative"
                    ])
                })
            elif change_type in ["Increase", "Decrease"]:
                changes.append({
                    "type": change_type,
                    "medication": medication,
                    "new_dose": f"{random.choice(['10', '20', '25', '50', '100'])} {random.choice(['mg', 'mcg'])}",
                    "reason": f"For {random.choice(['better control', 'side effect management', 'symptom management'])}"
                })
            elif change_type == "Switch":
                changes.append({
                    "type": "Switch",
                    "from_medication": medication,
                    "to_medication": random.choice([m for m in medications if m != medication]),
                    "reason": random.choice([
                        "Better efficacy expected", 
                        "Fewer side effects", 
                        "Insurance coverage",
                        "Simplified regimen"
                    ])
                })
        
        return changes
    
    def _generate_active_problems(self) -> List[Dict[str, Any]]:
        """Generate a list of active problems."""
        problems = [
            {"name": "Hypertension", "onset": f"{random.randint(1, 10)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Type 2 Diabetes", "onset": f"{random.randint(1, 10)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Hyperlipidemia", "onset": f"{random.randint(1, 10)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Obesity", "onset": f"{random.randint(1, 20)} years ago", "status": "Ongoing"},
            {"name": "Osteoarthritis", "onset": f"{random.randint(1, 5)} years ago", "status": random.choice(["Stable", "Worsening", "Improving"])},
            {"name": "GERD", "onset": f"{random.randint(1, 8)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Anxiety", "onset": f"{random.randint(1, 15)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Depression", "onset": f"{random.randint(1, 15)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Insomnia", "onset": f"{random.randint(1, 5)} years ago", "status": random.choice(["Controlled", "Uncontrolled", "Partially controlled"])},
            {"name": "Chronic Low Back Pain", "onset": f"{random.randint(1, 10)} years ago", "status": random.choice(["Stable", "Worsening", "Improving"])}
        ]
        
        # Select 2-5 problems
        num_problems = random.randint(2, 5)
        
        return random.sample(problems, num_problems)
    
    def _generate_allergies(self) -> List[Dict[str, str]]:
        """Generate a list of allergies."""
        allergies = [
            {"agent": "Penicillin", "reaction": "Hives", "severity": "Moderate"},
            {"agent": "Sulfa", "reaction": "Rash", "severity": "Mild"},
            {"agent": "Codeine", "reaction": "Nausea", "severity": "Mild"},
            {"agent": "Latex", "reaction": "Contact dermatitis", "severity": "Mild"},
            {"agent": "Contrast dye", "reaction": "Anaphylaxis", "severity": "Severe"},
            {"agent": "NSAIDs", "reaction": "GI upset", "severity": "Moderate"},
            {"agent": "Shellfish", "reaction": "Swelling", "severity": "Moderate"},
            {"agent": "Peanuts", "reaction": "Anaphylaxis", "severity": "Severe"}
        ]
        
        # 30% chance of no allergies
        if random.random() < 0.3:
            return []
        
        # Select 1-3 allergies
        num_allergies = random.randint(1, 3)
        
        return random.sample(allergies, num_allergies)
    
    def _generate_pending_tests(self) -> List[Dict[str, str]]:
        """Generate a list of pending tests."""
        tests = [
            {"test": "Colonoscopy", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Screening"},
            {"test": "Mammogram", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Screening"},
            {"test": "DEXA scan", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Osteoporosis screening"},
            {"test": "CT chest", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Abnormal chest x-ray"},
            {"test": "MRI brain", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Headaches"},
            {"test": "Echocardiogram", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Murmur"},
            {"test": "Sleep study", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Suspected sleep apnea"},
            {"test": "Pulmonary function tests", "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"), "reason": "Shortness of breath"}
        ]
        
        # Select 1-2 pending tests
        num_tests = random.randint(1, 2)
        
        return random.sample(tests, num_tests)
    
    def _generate_care_plan(self) -> Dict[str, Any]:
        """Generate a care plan."""
        return {
            "preventive_care": random.sample([
                "Annual physical", "Colonoscopy every 10 years", "Annual mammogram",
                "Annual flu vaccine", "Pneumococcal vaccine", "Shingles vaccine",
                "Dental exam every 6 months", "Eye exam annually"
            ], random.randint(2, 4)),
            "chronic_disease_management": random.sample([
                "Blood pressure checks monthly",
                "Hemoglobin A1c every 3 months",
                "Lipid panel annually",
                "Foot exams at each visit",
                "Medication reconciliation at each visit",
                "Weight management program"
            ], random.randint(1, 3)) if random.random() > 0.5 else [],
            "lifestyle_recommendations": random.sample([
                "Low sodium diet", "Regular exercise", "Weight loss",
                "Smoking cessation", "Limit alcohol intake", "Stress management"
            ], random.randint(1, 3))
        }
    
    def _generate_social_history(self) -> str:
        """Generate a social history."""
        # Smoking status
        smoking_status = random.choice([
            "Never smoker", 
            f"Former smoker, quit {random.randint(1, 20)} years ago", 
            f"Current smoker, {random.randint(1, 40)} pack-years"
        ])
        
        # Alcohol use
        alcohol_use = random.choice([
            "No alcohol use", 
            f"Social alcohol use, {random.randint(1, 4)} drinks per week", 
            f"Regular alcohol use, {random.randint(5, 14)} drinks per week",
            "History of alcohol use disorder, currently in remission"
        ])
        
        # Exercise
        exercise = random.choice([
            "No regular exercise", 
            f"Moderate exercise {random.randint(1, 3)} times per week", 
            f"Regular exercise {random.randint(4, 7)} times per week"
        ])
        
        # Occupation
        occupation = random.choice([
            "Retired", "Office worker", "Healthcare worker", 
            "Manual laborer", "Teacher", "Unemployed"
        ])
        
        # Living situation
        living_situation = random.choice([
            "Lives alone", "Lives with spouse", "Lives with family",
            "Assisted living facility", "Nursing home"
        ])
        
        return f"Smoking: {smoking_status}. Alcohol: {alcohol_use}. Exercise: {exercise}. Occupation: {occupation}. Living situation: {living_situation}."
    
    def _generate_family_history(self) -> str:
        """Generate a family history."""
        conditions = [
            "Hypertension", "Diabetes", "Coronary artery disease", 
            "Stroke", "Cancer", "Alzheimer's disease", "Osteoporosis"
        ]
        
        family_members = ["Mother", "Father", "Sister", "Brother", "Maternal grandmother", "Maternal grandfather", "Paternal grandmother", "Paternal grandfather"]
        
        history_parts = []
        
        # Generate 2-4 family history entries
        num_entries = random.randint(2, 4)
        
        for _ in range(num_entries):
            condition = random.choice(conditions)
            family_member = random.choice(family_members)
            
            # Age of onset or diagnosis
            age = random.randint(40, 85)
            
            history_parts.append(f"{family_member}: {condition} diagnosed at age {age}")
        
        return ". ".join(history_parts) + "."
    
    def _generate_current_status(self) -> str:
        """Generate current status for care coordination."""
        status_options = [
            "Patient is stable and following care plan as directed.",
            "Patient has had difficulty adhering to medication regimen.",
            "Patient recently discharged from hospital and requires close follow-up.",
            "Patient reports worsening symptoms despite current treatment.",
            "Patient has shown improvement with recent medication adjustments.",
            "Patient has missed several appointments and needs re-engagement.",
            "Patient has new social needs affecting care plan adherence.",
            "Patient requires additional education on disease management."
        ]
        
        return random.choice(status_options)
    
    def _generate_care_team_members(self, provider_ids: List[str]) -> List[Dict[str, str]]:
        """Generate care team members."""
        roles = [
            "Primary Care Provider", "Cardiologist", "Endocrinologist",
            "Care Manager", "Social Worker", "Pharmacist",
            "Nutritionist", "Physical Therapist", "Behavioral Health Provider"
        ]
        
        # Select 2-5 roles
        selected_roles = random.sample(roles, random.randint(2, 5))
        
        # Generate care team members
        care_team = []
        for role in selected_roles:
            provider_id = random.choice(provider_ids)
            
            care_team.append({
                "role": role,
                "name": f"Dr. {self.faker.last_name()}" if "Provider" in role or role in ["Cardiologist", "Endocrinologist"] else self.faker.name(),
                "provider_id": provider_id,
                "last_contact": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
            })
        
        return care_team
    
    def _generate_action_items(self) -> List[Dict[str, Any]]:
        """Generate action items for care coordination."""
        action_items = []
        
        # Potential action items
        potential_items = [
            {"description": "Schedule follow-up appointment", "assigned_to": "Primary Care Provider", "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")},
            {"description": "Medication reconciliation", "assigned_to": "Pharmacist", "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")},
            {"description": "Home safety evaluation", "assigned_to": "Social Worker", "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")},
            {"description": "Nutritional assessment", "assigned_to": "Nutritionist", "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")},
            {"description": "Arrange transportation to appointments", "assigned_to": "Care Manager", "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")},
            {"description": "Review recent lab results", "assigned_to": "Primary Care Provider", "due_date": (datetime.now() + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")},
            {"description": "Assess medication adherence", "assigned_to": "Care Manager", "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")},
            {"description": "Behavioral health screening", "assigned_to": "Behavioral Health Provider", "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")},
            {"description": "Arrange home health services", "assigned_to": "Social Worker", "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")},
            {"description": "Diabetes education session", "assigned_to": "Diabetes Educator", "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")}
        ]
        
        # Select 2-4 action items
        num_items = random.randint(2, 4)
        
        return random.sample(potential_items, num_items)
    
    def _generate_barriers_to_care(self) -> List[str]:
        """Generate barriers to care."""
        barriers = [
            "Transportation issues",
            "Financial constraints",
            "Lack of social support",
            "Health literacy challenges",
            "Language barriers",
            "Cultural factors",
            "Cognitive impairment",
            "Mental health issues",
            "Medication cost",
            "Work schedule conflicts",
            "Childcare responsibilities",
            "Housing instability",
            "Food insecurity",
            "Technology access limitations"
        ]
        
        # Select 1-3 barriers
        num_barriers = random.randint(1, 3)
        
        return random.sample(barriers, num_barriers)
    
    def _generate_patient_goals(self) -> List[str]:
        """Generate patient goals."""
        goals = [
            "Improve blood pressure control",
            "Achieve better glucose control",
            "Lose weight",
            "Increase physical activity",
            "Reduce medication side effects",
            "Improve sleep quality",
            "Manage pain more effectively",
            "Return to work",
            "Maintain independence at home",
            "Reduce hospital admissions",
            "Improve mobility",
            "Better understand condition and treatment options"
        ]
        
        # Select 1-3 goals
        num_goals = random.randint(1, 3)
        
        return random.sample(goals, num_goals)