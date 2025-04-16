"""
Communication records generator for the synthetic healthcare data generator.

This module generates synthetic communication records between healthcare entities.
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
from src.models.narrative import CommunicationRecord, CommunicationType


class CommunicationGenerator(BaseGenerator):
    """Generator for synthetic communication records."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the communication records generator.
        
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
    
    def _load_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load communication templates from the configuration.
        
        Returns:
            Dictionary of templates for different communication types.
        """
        templates = {}
        
        # Default templates if not provided in config
        default_templates = {
            "provider_to_provider": {
                "subject": [
                    "Consultation Request: {member_name}",
                    "Patient Referral: {member_name}",
                    "Care Coordination for {member_name}",
                    "Treatment Plan Discussion: {member_name}",
                    "Test Results for {member_name}"
                ],
                "content": [
                    "I am referring {member_name}, a {age}-year-old {gender} with {condition}, for your evaluation and management. The patient has been experiencing {symptom} for {duration}. Current medications include {medications}. Please advise on {request}.",
                    "Thank you for seeing {member_name} in consultation. The patient has a history of {condition} and has been experiencing {symptom}. I would appreciate your thoughts on {request}.",
                    "I wanted to update you on our mutual patient, {member_name}. Recent {test_type} showed {test_results}. I have {action} and would appreciate your input on {request}.",
                    "I am managing {member_name} for {condition} and would like your opinion on {request}. The patient has tried {treatments} with {response}.",
                    "This is regarding {member_name}, who I recently started on {medication} for {condition}. The patient is reporting {symptom}. Would you recommend {request}?"
                ]
            },
            "provider_to_patient": {
                "subject": [
                    "Your Recent Appointment Follow-up",
                    "Test Results Available",
                    "Medication Information",
                    "Appointment Reminder",
                    "Care Plan Update"
                ],
                "content": [
                    "I wanted to follow up after your recent appointment. As we discussed, you have been diagnosed with {condition}. Please continue {instructions}. If you experience {symptoms}, please contact our office.",
                    "Your recent {test_type} results are now available. {test_results}. Based on these results, I recommend {recommendation}. Please schedule a follow-up appointment to discuss further.",
                    "This is a reminder about your medication changes. Please {medication_instructions}. Watch for side effects such as {side_effects} and contact us if they occur.",
                    "Just a reminder that you have an appointment scheduled for {date_time}. Please bring {items_to_bring}. If you need to reschedule, please call our office.",
                    "I am writing to update your care plan for {condition}. Please {new_instructions}. We will reassess at your next appointment on {date}."
                ]
            },
            "patient_to_provider": {
                "subject": [
                    "Question about Medication",
                    "Symptom Update",
                    "Appointment Request",
                    "Test Results Question",
                    "Prescription Refill Request"
                ],
                "content": [
                    "I have been taking {medication} as prescribed for my {condition}, but I'm experiencing {symptom}. Is this a normal side effect or should I be concerned?",
                    "I wanted to update you on my symptoms. The {symptom} has {change} since my last visit. I have been following your advice to {instructions}, but I'm still concerned.",
                    "I would like to schedule an appointment to discuss {concern}. I am available {availability}. Is there anything I should do in the meantime?",
                    "I received my test results through the patient portal, but I'm not sure what they mean. Could you explain what {test_result} indicates for my {condition}?",
                    "I need a refill of my {medication} prescription. I have been taking it as prescribed for my {condition}. My pharmacy information is {pharmacy_info}."
                ]
            },
            "care_team_discussion": {
                "subject": [
                    "Care Team Meeting: {member_name}",
                    "Care Coordination Update: {member_name}",
                    "Treatment Plan Review: {member_name}",
                    "Discharge Planning: {member_name}",
                    "Care Transition: {member_name}"
                ],
                "content": [
                    "During our care team meeting for {member_name}, we discussed the patient's {condition}. Dr. {doctor_name} recommended {recommendation}. The care manager will {care_manager_action}. Our next steps include {next_steps}.",
                    "This is an update on our care coordination for {member_name}. The patient has {recent_development}. The {specialist_type} has recommended {specialist_recommendation}. We need to {team_action}.",
                    "We reviewed {member_name}'s treatment plan today. The patient is {progress} with current interventions. We decided to {decision}. Each team member will {team_responsibilities}.",
                    "We are planning for {member_name}'s discharge. The patient will need {post_discharge_needs}. We have arranged for {arrangements}. Follow-up appointments include {follow_up}.",
                    "We are coordinating {member_name}'s transition from {source} to {destination}. Key considerations include {considerations}. The receiving team should be aware of {important_information}."
                ]
            },
            "insurance_communication": {
                "subject": [
                    "Prior Authorization Request: {member_name}",
                    "Claim Inquiry: #{claim_id}",
                    "Coverage Determination: {service}",
                    "Appeal for Denied Claim: #{claim_id}",
                    "Medical Necessity Documentation: {member_name}"
                ],
                "content": [
                    "I am requesting prior authorization for {member_name} to receive {service}. The patient has been diagnosed with {condition} and has tried {previous_treatments} without adequate improvement. Clinical justification includes {justification}.",
                    "I am inquiring about claim #{claim_id} for {member_name}, which was {claim_status}. The service provided was {service} on {date}. Please review the claim and provide {request}.",
                    "I am seeking a coverage determination for {service} for {member_name}. The patient requires this {service_type} due to {medical_necessity}. Supporting documentation includes {documentation}.",
                    "I am appealing the denial of claim #{claim_id} for {member_name}. The service {service} was denied for {denial_reason}. I believe this service meets medical necessity criteria because {appeal_justification}.",
                    "I am providing additional medical necessity documentation for {member_name}'s {service}. The patient's condition {condition_details} requires this intervention because {necessity_explanation}."
                ]
            },
            "pharmacy_communication": {
                "subject": [
                    "Medication Interaction Alert: {member_name}",
                    "Prescription Clarification: {member_name}",
                    "Prior Authorization Needed: {medication}",
                    "Refill Request Status: {member_name}",
                    "Formulary Alternative Suggestion: {medication}"
                ],
                "content": [
                    "I wanted to alert you to a potential interaction between {medication1} and {medication2} prescribed for {member_name}. The interaction may cause {interaction_effect}. Would you like to {suggested_action}?",
                    "I need clarification on the prescription for {medication} for {member_name}. The {prescription_issue} is unclear. Could you please specify {clarification_request}?",
                    "The prescription for {medication} for {member_name} requires prior authorization from their insurance. Would you like to {authorization_options}?",
                    "Regarding {member_name}'s refill request for {medication}: {refill_status}. The patient has {refill_details}. Please advise if you would like to {refill_options}.",
                    "{medication} prescribed for {member_name} is not on their insurance formulary. Would you consider {alternative_medication} as an alternative? It is {tier_information} and has similar {efficacy_comparison}."
                ]
            }
        }
        
        # Use templates from config if available, otherwise use defaults
        comm_templates = self.config.get("communication_templates", default_templates)
        
        for comm_type, sections in comm_templates.items():
            templates[comm_type] = sections
        
        return templates
    
    def generate(self, members: List[Dict], claims: Optional[List[Dict]] = None, 
                 authorizations: Optional[List[Dict]] = None, count: Optional[int] = None) -> List[CommunicationRecord]:
        """
        Generate synthetic communication records based on member, claim, and authorization data.
        
        Args:
            members: List of member dictionaries to generate communications for.
            claims: Optional list of claim dictionaries to reference in communications.
            authorizations: Optional list of authorization dictionaries to reference.
            count: Optional number of communications to generate. If not provided,
                   will generate based on config settings.
                   
        Returns:
            List of generated communication records.
        """
        if not members:
            self.logger.warning("No members provided for communication generation")
            return []
        
        communications = []
        comms_per_member = self.config.get("communications_per_member", {"min": 2, "max": 8})
        
        # Create a lookup for members by ID
        member_lookup = {member["id"]: member for member in members}
        
        # Create lookups for claims and authorizations by member ID
        claim_lookup = {}
        if claims:
            for claim in claims:
                member_id = claim.get("member_id")
                if member_id not in claim_lookup:
                    claim_lookup[member_id] = []
                claim_lookup[member_id].append(claim)
        
        auth_lookup = {}
        if authorizations:
            for auth in authorizations:
                member_id = auth.get("member_id")
                if member_id not in auth_lookup:
                    auth_lookup[member_id] = []
                auth_lookup[member_id].append(auth)
        
        for member_id, member in member_lookup.items():
            # Determine how many communications to generate for this member
            num_comms = random.randint(comms_per_member["min"], comms_per_member["max"])
            
            # Get related claims and authorizations
            member_claims = claim_lookup.get(member_id, [])
            member_auths = auth_lookup.get(member_id, [])
            
            # Generate communications for this member
            member_comms = self._generate_communications_for_member(
                member, member_claims, member_auths, num_comms
            )
            communications.extend(member_comms)
        
        # If count is specified, randomly select that many communications
        if count is not None and count < len(communications):
            communications = random.sample(communications, count)
        
        return communications
    
    def _generate_communications_for_member(self, member: Dict, claims: List[Dict], 
                                           authorizations: List[Dict], num_comms: int) -> List[CommunicationRecord]:
        """
        Generate a specified number of communication records for a member.
        
        Args:
            member: Member dictionary to generate communications for.
            claims: List of claims for this member.
            authorizations: List of authorizations for this member.
            num_comms: Number of communications to generate.
            
        Returns:
            List of generated communication records.
        """
        communications = []
        
        # Get member details
        member_id = member["id"]
        member_name = member["full_name"]
        age = member["age"]
        gender = member["demographics"]["gender"]
        conditions = member.get("conditions", [])
        medications = member.get("medications", [])
        
        # Generate dates for the communications (within the last 6 months)
        today = datetime.now()
        date_range = 180  # days
        
        # Generate provider IDs (in a real system, these would come from a provider database)
        provider_ids = [f"PROV{random.randint(10000, 99999)}" for _ in range(3)]
        
        for _ in range(num_comms):
            # Generate a random date within the last 6 months
            days_ago = random.randint(0, date_range)
            comm_date = today - timedelta(days=days_ago)
            
            # Select a random communication type
            comm_type = random.choice(list(CommunicationType))
            
            # Generate the communication content based on type
            comm_data = self._generate_communication_by_type(
                comm_type, member_id, member_name, age, gender, 
                conditions, medications, provider_ids, claims, authorizations
            )
            
            # Create the communication record
            comm = CommunicationRecord(
                id=f"COMM{uuid.uuid4().hex[:8]}",
                communication_type=comm_type,
                date_time=comm_date,
                subject=comm_data["subject"],
                content=comm_data["content"],
                sender_id=comm_data["sender_id"],
                sender_type=comm_data["sender_type"],
                recipient_id=comm_data["recipient_id"],
                recipient_type=comm_data["recipient_type"],
                related_to=comm_data.get("related_to"),
                attachments=comm_data.get("attachments", [])
            )
            
            communications.append(comm)
        
        return communications
    
    def _generate_communication_by_type(self, comm_type: CommunicationType, member_id: str, 
                                       member_name: str, age: int, gender: str, conditions: List[str], 
                                       medications: List[str], provider_ids: List[str], 
                                       claims: List[Dict], authorizations: List[Dict]) -> Dict:
        """
        Generate communication data based on the communication type.
        
        Args:
            comm_type: Type of communication to generate.
            member_id: ID of the member.
            member_name: Name of the member.
            age: Age of the member.
            gender: Gender of the member.
            conditions: List of member's conditions.
            medications: List of member's medications.
            provider_ids: List of provider IDs to use.
            claims: List of claims for this member.
            authorizations: List of authorizations for this member.
            
        Returns:
            Dictionary with communication data.
        """
        comm_data = {
            "sender_id": "",
            "sender_type": "",
            "recipient_id": "",
            "recipient_type": "",
            "subject": "",
            "content": "",
            "related_to": None,
            "attachments": []
        }
        
        # Get a condition and medication if available
        condition = random.choice(conditions) if conditions else "chronic condition"
        medication = random.choice(medications) if medications else "prescribed medication"
        
        # Get a claim or authorization if available
        claim = random.choice(claims) if claims else None
        authorization = random.choice(authorizations) if authorizations else None
        
        # Set up common template variables
        template_vars = {
            "member_name": member_name,
            "age": age,
            "gender": gender,
            "condition": condition,
            "medication": medication,
            "medications": ", ".join(medications[:3]) if len(medications) > 0 else "none",
            "symptom": random.choice(["pain", "fatigue", "dizziness", "shortness of breath", "nausea"]),
            "duration": f"{random.randint(1, 30)} days",
            "date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%m/%d/%Y"),
            "date_time": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%m/%d/%Y at %I:%M %p")
        }
        
        # Configure communication based on type
        if comm_type == CommunicationType.PROVIDER_TO_PROVIDER:
            # Provider to provider communication
            sender_id = provider_ids[0]
            recipient_id = provider_ids[1]
            
            comm_data["sender_id"] = sender_id
            comm_data["sender_type"] = "provider"
            comm_data["recipient_id"] = recipient_id
            comm_data["recipient_type"] = "provider"
            
            # Additional template variables
            template_vars.update({
                "request": random.choice(["treatment recommendations", "further evaluation", "medication adjustment", "specialist input"]),
                "test_type": random.choice(["laboratory tests", "imaging studies", "diagnostic procedures"]),
                "test_results": random.choice(["abnormal findings", "concerning results", "improvement from previous studies", "stable findings"]),
                "action": random.choice(["adjusted medications", "ordered additional tests", "scheduled follow-up", "discussed options with the patient"]),
                "treatments": random.choice(["first-line therapies", "conservative management", "medication adjustments", "lifestyle modifications"]),
                "response": random.choice(["minimal improvement", "partial response", "good initial response but plateau", "side effects limiting treatment"])
            })
            
        elif comm_type == CommunicationType.PROVIDER_TO_PATIENT:
            # Provider to patient communication
            sender_id = provider_ids[0]
            recipient_id = member_id
            
            comm_data["sender_id"] = sender_id
            comm_data["sender_type"] = "provider"
            comm_data["recipient_id"] = recipient_id
            comm_data["recipient_type"] = "patient"
            
            # Additional template variables
            template_vars.update({
                "instructions": random.choice(["taking your medications as prescribed", "monitoring your symptoms", "following the diet and exercise plan we discussed"]),
                "symptoms": random.choice(["worsening symptoms", "new symptoms", "side effects", "fever or severe pain"]),
                "test_type": random.choice(["blood work", "imaging", "diagnostic procedure"]),
                "test_results": random.choice(["within normal limits", "showing some abnormalities that we should discuss", "improved from your previous results", "requiring further investigation"]),
                "recommendation": random.choice(["continuing your current treatment", "adjusting your medication", "additional testing", "lifestyle modifications"]),
                "medication_instructions": random.choice(["take the new medication as prescribed", "discontinue the previous medication", "adjust the dosage as we discussed"]),
                "side_effects": random.choice(["dizziness, nausea, or rash", "headache or fatigue", "digestive issues", "changes in mood or sleep"]),
                "items_to_bring": random.choice(["your current medications", "your blood pressure log", "your glucose readings", "any recent test results from other providers"]),
                "new_instructions": random.choice(["continue with the current plan", "increase your physical activity", "modify your diet as discussed", "monitor your symptoms more frequently"])
            })
            
        elif comm_type == CommunicationType.PATIENT_TO_PROVIDER:
            # Patient to provider communication
            sender_id = member_id
            recipient_id = provider_ids[0]
            
            comm_data["sender_id"] = sender_id
            comm_data["sender_type"] = "patient"
            comm_data["recipient_id"] = recipient_id
            comm_data["recipient_type"] = "provider"
            
            # Additional template variables
            template_vars.update({
                "symptom": random.choice(["pain", "fatigue", "dizziness", "shortness of breath", "nausea", "rash", "swelling"]),
                "change": random.choice(["improved", "worsened", "remained the same", "changed in character"]),
                "instructions": random.choice(["take the medication", "rest", "apply ice", "monitor symptoms", "modify diet"]),
                "concern": random.choice(["ongoing symptoms", "medication side effects", "test results", "new health issue"]),
                "availability": random.choice(["mornings next week", "afternoons on Tuesday or Thursday", "anytime except Wednesday", "as soon as possible"]),
                "test_result": random.choice(["elevated blood pressure", "abnormal blood count", "cholesterol levels", "thyroid function"]),
                "pharmacy_info": random.choice(["Walgreens on Main Street", "CVS on Oak Avenue", "the pharmacy you have on file"])
            })
            
        elif comm_type == CommunicationType.CARE_TEAM_DISCUSSION:
            # Care team discussion
            sender_id = provider_ids[0]
            recipient_id = provider_ids[1]
            
            comm_data["sender_id"] = sender_id
            comm_data["sender_type"] = "provider"
            comm_data["recipient_id"] = recipient_id
            comm_data["recipient_type"] = "provider"
            
            # Additional template variables
            template_vars.update({
                "doctor_name": self.faker.last_name(),
                "recommendation": random.choice(["adjusting medications", "additional testing", "specialist referral", "care management enrollment"]),
                "care_manager_action": random.choice(["follow up weekly", "coordinate home services", "provide education", "monitor adherence"]),
                "next_steps": random.choice(["reassess in 30 days", "schedule team follow-up", "update care plan", "coordinate with specialists"]),
                "recent_development": random.choice(["been hospitalized", "shown improvement", "experienced complications", "started new treatment"]),
                "specialist_type": random.choice(["cardiologist", "endocrinologist", "neurologist", "orthopedist"]),
                "specialist_recommendation": random.choice(["medication changes", "additional testing", "procedure", "conservative management"]),
                "team_action": random.choice(["coordinate care", "update treatment plan", "schedule follow-up", "provide additional resources"]),
                "progress": random.choice(["showing improvement", "not responding adequately", "experiencing side effects", "maintaining stability"]),
                "decision": random.choice(["continue current approach", "modify treatment plan", "add new interventions", "consult additional specialists"]),
                "team_responsibilities": random.choice(["follow up as scheduled", "document progress", "communicate changes", "coordinate services"]),
                "post_discharge_needs": random.choice(["home health services", "durable medical equipment", "medication management", "follow-up appointments"]),
                "arrangements": random.choice(["home health visits", "equipment delivery", "transportation", "meal services"]),
                "follow_up": random.choice(["primary care in 1 week", "specialist in 2 weeks", "therapy 3 times weekly", "nurse call in 48 hours"]),
                "source": random.choice(["hospital", "skilled nursing facility", "home health", "specialist care"]),
                "destination": random.choice(["home with services", "rehabilitation facility", "assisted living", "primary care management"]),
                "considerations": random.choice(["medication reconciliation", "functional status", "caregiver support", "social determinants"]),
                "important_information": random.choice(["recent medication changes", "fall risk", "cognitive status", "care preferences"])
            })
            
        elif comm_type == CommunicationType.INSURANCE_COMMUNICATION:
            # Insurance communication
            if random.choice([True, False]):
                # Provider to insurance
                sender_id = provider_ids[0]
                sender_type = "provider"
                recipient_id = f"INS{random.randint(1000, 9999)}"
                recipient_type = "insurance"
            else:
                # Insurance to provider
                sender_id = f"INS{random.randint(1000, 9999)}"
                sender_type = "insurance"
                recipient_id = provider_ids[0]
                recipient_type = "provider"
            
            comm_data["sender_id"] = sender_id
            comm_data["sender_type"] = sender_type
            comm_data["recipient_id"] = recipient_id
            comm_data["recipient_type"] = recipient_type
            
            # Use claim or authorization if available
            if claim:
                comm_data["related_to"] = claim.get("id")
                template_vars["claim_id"] = claim.get("id", "12345")
                template_vars["claim_status"] = claim.get("status", "pending")
                template_vars["service"] = claim.get("service_lines", [{}])[0].get("description", "medical service") if claim.get("service_lines") else "medical service"
                template_vars["date"] = claim.get("date_of_service", datetime.now().strftime("%m/%d/%Y"))
            elif authorization:
                comm_data["related_to"] = authorization.get("id")
                template_vars["service"] = authorization.get("service_lines", [{}])[0].get("description", "medical service") if authorization.get("service_lines") else "medical service"
            else:
                template_vars["claim_id"] = f"CL{random.randint(10000, 99999)}"
                template_vars["claim_status"] = random.choice(["pending", "denied", "partially paid", "under review"])
                template_vars["service"] = random.choice(["office visit", "diagnostic procedure", "specialist consultation", "inpatient stay", "therapy services"])
                template_vars["date"] = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%m/%d/%Y")
            
            # Additional template variables
            template_vars.update({
                "previous_treatments": random.choice(["conservative management", "first-line medications", "physical therapy", "lifestyle modifications"]),
                "justification": random.choice(["clinical guidelines", "failure of standard therapy", "comorbid conditions", "specific diagnostic findings"]),
                "request": random.choice(["clarification", "reconsideration", "expedited processing", "additional information"]),
                "service_type": random.choice(["diagnostic test", "procedure", "therapy", "equipment", "medication"]),
                "medical_necessity": random.choice(["confirmed diagnosis", "functional impairment", "risk of complications", "failure of conservative treatment"]),
                "documentation": random.choice(["clinical notes", "test results", "specialist recommendations", "treatment history"]),
                "denial_reason": random.choice(["not medically necessary", "experimental/investigational", "out of network", "insufficient documentation"]),
                "appeal_justification": random.choice(["clinical guidelines support this service", "patient's unique circumstances", "previous treatments have failed", "potential complications without treatment"]),
                "condition_details": random.choice(["severity", "duration", "impact on function", "complication risk"]),
                "necessity_explanation": random.choice(["standard treatments have failed", "rapid progression", "high risk of complications", "significant functional impairment"])
            })
            
        elif comm_type == CommunicationType.PHARMACY_COMMUNICATION:
            # Pharmacy communication
            if random.choice([True, False]):
                # Pharmacy to provider
                sender_id = f"PHARM{random.randint(100, 999)}"
                sender_type = "pharmacy"
                recipient_id = provider_ids[0]
                recipient_type = "provider"
            else:
                # Provider to pharmacy
                sender_id = provider_ids[0]
                sender_type = "provider"
                recipient_id = f"PHARM{random.randint(100, 999)}"
                recipient_type = "pharmacy"
            
            comm_data["sender_id"] = sender_id
            comm_data["sender_type"] = sender_type
            comm_data["recipient_id"] = recipient_id
            comm_data["recipient_type"] = recipient_type
            
            # Additional template variables
            if len(medications) >= 2:
                med1, med2 = random.sample(medications, 2)
            else:
                med1 = medication
                med2 = random.choice(["lisinopril", "metformin", "atorvastatin", "levothyroxine", "amlodipine"])
            
            template_vars.update({
                "medication1": med1,
                "medication2": med2,
                "interaction_effect": random.choice(["increased risk of side effects", "decreased effectiveness", "QT prolongation", "serotonin syndrome", "increased bleeding risk"]),
                "suggested_action": random.choice(["adjust the dosage", "monitor more closely", "consider an alternative medication", "space administration times"]),
                "prescription_issue": random.choice(["dosage", "frequency", "duration", "formulation", "quantity"]),
                "clarification_request": random.choice(["the intended dosage", "how long to continue therapy", "whether to take with food", "if this replaces the previous prescription"]),
                "authorization_options": random.choice(["submit a prior authorization request", "switch to a formulary alternative", "provide clinical justification", "discuss options with the patient"]),
                "refill_status": random.choice(["approved", "pending", "requires your authorization", "denied by insurance"]),
                "refill_details": random.choice(["no refills remaining", "requested early refill", "insurance coverage issue", "dosage discrepancy"]),
                "refill_options": random.choice(["authorize additional refills", "schedule patient for follow-up before refill", "adjust the prescription", "switch to an alternative"]),
                "alternative_medication": random.choice(["generic equivalent", "therapeutic alternative", "formulary option"]),
                "tier_information": random.choice(["a tier 1 medication", "covered without prior authorization", "at a lower copay", "preferred by the patient's insurance"]),
                "efficacy_comparison": random.choice(["efficacy profile", "side effect profile", "dosing schedule", "drug interactions"])
            })
        
        # Get templates for this communication type
        type_key = comm_type.value
        if type_key in self.templates:
            # Get subject template
            subject_templates = self.templates[type_key].get("subject", ["Communication regarding {member_name}"])
            subject_template = random.choice(subject_templates)
            
            # Get content template
            content_templates = self.templates[type_key].get("content", ["This is a communication regarding {member_name}."])
            content_template = random.choice(content_templates)
            
            # Format templates with variables
            subject = self._format_template(subject_template, template_vars)
            content = self._format_template(content_template, template_vars)
            
            comm_data["subject"] = subject
            comm_data["content"] = content
        else:
            # Fallback if no templates are available
            comm_data["subject"] = f"Communication regarding {member_name}"
            comm_data["content"] = f"This is a {comm_type.value} communication about {member_name}."
        
        # Randomly add attachments
        if random.random() < 0.3:  # 30% chance of having attachments
            attachment_types = ["Clinical Summary", "Lab Results", "Imaging Report", "Prescription", "Insurance Form"]
            num_attachments = random.randint(1, 2)
            comm_data["attachments"] = random.sample(attachment_types, num_attachments)
        
        return comm_data
    
    def _format_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Format a template string with the provided variables.
        
        Args:
            template: Template string with placeholders.
            variables: Dictionary of variables to substitute.
            
        Returns:
            Formatted string.
        """
        result = template
        
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result