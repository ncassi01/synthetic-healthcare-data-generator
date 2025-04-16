"""
Provider Network Generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic provider networks,
including providers, facilities, relationships, and referral patterns.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple

from src.utils.file_utils import load_config


class Provider:
    """
    Represents a healthcare provider (individual practitioner).
    """
    
    def __init__(self, provider_id: Optional[str] = None, npi: Optional[str] = None):
        """
        Initialize a provider.
        
        Args:
            provider_id: Provider ID (generated if not provided)
            npi: National Provider Identifier (generated if not provided)
        """
        self.id = provider_id or f"PRV{uuid.uuid4().hex[:8].upper()}"
        self.npi = npi or f"{random.randint(1000000000, 9999999999)}"
        self.first_name = None
        self.last_name = None
        self.credentials = None
        self.specialty = None
        self.subspecialty = None
        self.practice_locations = []
        self.affiliations = []
        self.network_status = None
        self.accepting_new_patients = None
        self.languages = []
        self.gender = None
        self.contact_info = {}
        
    def set_basic_info(self, first_name: str, last_name: str, credentials: str, gender: str) -> None:
        """
        Set basic provider information.
        
        Args:
            first_name: Provider's first name
            last_name: Provider's last name
            credentials: Provider's credentials (MD, DO, NP, etc.)
            gender: Provider's gender
        """
        self.first_name = first_name
        self.last_name = last_name
        self.credentials = credentials
        self.gender = gender
        
    def set_specialty(self, specialty: str, subspecialty: Optional[str] = None) -> None:
        """
        Set provider specialty information.
        
        Args:
            specialty: Provider's primary specialty
            subspecialty: Provider's subspecialty (optional)
        """
        self.specialty = specialty
        self.subspecialty = subspecialty
        
    def add_practice_location(self, location: Dict[str, Any]) -> None:
        """
        Add a practice location for the provider.
        
        Args:
            location: Dictionary containing location details
        """
        self.practice_locations.append(location)
        
    def add_affiliation(self, organization_id: str, affiliation_type: str) -> None:
        """
        Add an organizational affiliation for the provider.
        
        Args:
            organization_id: ID of the affiliated organization
            affiliation_type: Type of affiliation (e.g., "employed", "contracted", "admitting")
        """
        self.affiliations.append({
            "organization_id": organization_id,
            "type": affiliation_type,
            "start_date": (datetime.now() - timedelta(days=random.randint(30, 1825))).isoformat()
        })
        
    def set_network_status(self, status: str, accepting_new_patients: bool) -> None:
        """
        Set provider network status.
        
        Args:
            status: Network status (e.g., "in-network", "out-of-network", "preferred")
            accepting_new_patients: Whether the provider is accepting new patients
        """
        self.network_status = status
        self.accepting_new_patients = accepting_new_patients
        
    def add_language(self, language: str) -> None:
        """
        Add a language spoken by the provider.
        
        Args:
            language: Language spoken
        """
        if language not in self.languages:
            self.languages.append(language)
        
    def set_contact_info(self, phone: str, email: str, fax: Optional[str] = None) -> None:
        """
        Set provider contact information.
        
        Args:
            phone: Provider's phone number
            email: Provider's email address
            fax: Provider's fax number (optional)
        """
        self.contact_info = {
            "phone": phone,
            "email": email
        }
        
        if fax:
            self.contact_info["fax"] = fax
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the provider to a dictionary.
        
        Returns:
            Dictionary representation of the provider
        """
        return {
            "id": self.id,
            "npi": self.npi,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "credentials": self.credentials,
            "specialty": self.specialty,
            "subspecialty": self.subspecialty,
            "practice_locations": self.practice_locations,
            "affiliations": self.affiliations,
            "network_status": self.network_status,
            "accepting_new_patients": self.accepting_new_patients,
            "languages": self.languages,
            "gender": self.gender,
            "contact_info": self.contact_info
        }


class Facility:
    """
    Represents a healthcare facility (hospital, clinic, etc.).
    """
    
    def __init__(self, facility_id: Optional[str] = None):
        """
        Initialize a facility.
        
        Args:
            facility_id: Facility ID (generated if not provided)
        """
        self.id = facility_id or f"FAC{uuid.uuid4().hex[:8].upper()}"
        self.name = None
        self.type = None
        self.address = {}
        self.contact_info = {}
        self.network_status = None
        self.specialties = []
        self.services = []
        self.accreditations = []
        self.affiliated_providers = []
        
    def set_basic_info(self, name: str, facility_type: str) -> None:
        """
        Set basic facility information.
        
        Args:
            name: Facility name
            facility_type: Type of facility (hospital, clinic, etc.)
        """
        self.name = name
        self.type = facility_type
        
    def set_address(self, street: str, city: str, state: str, zip_code: str) -> None:
        """
        Set facility address.
        
        Args:
            street: Street address
            city: City
            state: State
            zip_code: ZIP code
        """
        self.address = {
            "street": street,
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
        
    def set_contact_info(self, phone: str, email: str, website: Optional[str] = None) -> None:
        """
        Set facility contact information.
        
        Args:
            phone: Facility phone number
            email: Facility email address
            website: Facility website (optional)
        """
        self.contact_info = {
            "phone": phone,
            "email": email
        }
        
        if website:
            self.contact_info["website"] = website
        
    def set_network_status(self, status: str) -> None:
        """
        Set facility network status.
        
        Args:
            status: Network status (e.g., "in-network", "out-of-network", "preferred")
        """
        self.network_status = status
        
    def add_specialty(self, specialty: str) -> None:
        """
        Add a specialty offered at the facility.
        
        Args:
            specialty: Medical specialty
        """
        if specialty not in self.specialties:
            self.specialties.append(specialty)
        
    def add_service(self, service: str) -> None:
        """
        Add a service offered at the facility.
        
        Args:
            service: Healthcare service
        """
        if service not in self.services:
            self.services.append(service)
        
    def add_accreditation(self, accreditation: str, date: datetime) -> None:
        """
        Add an accreditation for the facility.
        
        Args:
            accreditation: Accreditation name
            date: Date of accreditation
        """
        self.accreditations.append({
            "name": accreditation,
            "date": date.isoformat()
        })
        
    def add_affiliated_provider(self, provider_id: str, affiliation_type: str) -> None:
        """
        Add an affiliated provider to the facility.
        
        Args:
            provider_id: ID of the affiliated provider
            affiliation_type: Type of affiliation (e.g., "employed", "contracted", "admitting")
        """
        self.affiliated_providers.append({
            "provider_id": provider_id,
            "type": affiliation_type
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the facility to a dictionary.
        
        Returns:
            Dictionary representation of the facility
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "contact_info": self.contact_info,
            "network_status": self.network_status,
            "specialties": self.specialties,
            "services": self.services,
            "accreditations": self.accreditations,
            "affiliated_providers": self.affiliated_providers
        }


class ProviderRelationship:
    """
    Represents a relationship between providers (referrals, collaborations, etc.).
    """
    
    def __init__(self, source_id: str, target_id: str, relationship_type: str):
        """
        Initialize a provider relationship.
        
        Args:
            source_id: ID of the source provider
            target_id: ID of the target provider
            relationship_type: Type of relationship (referral, collaboration, etc.)
        """
        self.id = f"REL{uuid.uuid4().hex[:8].upper()}"
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.start_date = datetime.now() - timedelta(days=random.randint(30, 1095))
        self.strength = random.uniform(0.1, 1.0)  # Relationship strength (0.1 to 1.0)
        self.referral_count = 0
        self.attributes = {}
        
    def set_referral_count(self, count: int) -> None:
        """
        Set the number of referrals between these providers.
        
        Args:
            count: Number of referrals
        """
        self.referral_count = count
        
    def add_attribute(self, key: str, value: Any) -> None:
        """
        Add an attribute to the relationship.
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        self.attributes[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the provider relationship to a dictionary.
        
        Returns:
            Dictionary representation of the provider relationship
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "start_date": self.start_date.isoformat(),
            "strength": self.strength,
            "referral_count": self.referral_count,
            "attributes": self.attributes
        }


class ProviderNetworkGenerator:
    """
    Generator for synthetic provider networks.
    """
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the provider network generator.
        
        Args:
            config: Configuration dictionary
            seed: Random seed for reproducibility
        """
        self.config = config
        self.network_config = config.get("provider_network_config", {})
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load reference data
        self.first_names = self.network_config.get("first_names", [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"
        ])
        
        self.last_names = self.network_config.get("last_names", [
            "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
            "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"
        ])
        
        self.credentials = self.network_config.get("credentials", [
            "MD", "DO", "NP", "PA", "LCSW", "PhD", "PsyD", "RN", "PT", "OT"
        ])
        
        self.specialties = self.network_config.get("specialties", [
            "Primary Care", "Cardiology", "Pulmonology", "Gastroenterology", "Orthopedics",
            "Neurology", "Endocrinology", "Psychiatry", "Oncology", "Infectious Disease",
            "Pediatrics", "Obstetrics/Gynecology", "Dermatology", "Ophthalmology", "Urology"
        ])
        
        self.subspecialties = self.network_config.get("subspecialties", {
            "Cardiology": ["Interventional Cardiology", "Electrophysiology", "Heart Failure"],
            "Pulmonology": ["Critical Care", "Sleep Medicine", "Interventional Pulmonology"],
            "Gastroenterology": ["Hepatology", "Inflammatory Bowel Disease", "Interventional Endoscopy"],
            "Orthopedics": ["Sports Medicine", "Joint Replacement", "Spine Surgery", "Hand Surgery"],
            "Neurology": ["Stroke", "Epilepsy", "Movement Disorders", "Neuromuscular"],
            "Endocrinology": ["Diabetes", "Thyroid Disorders", "Metabolic Disorders"],
            "Psychiatry": ["Child & Adolescent", "Geriatric", "Addiction Medicine"],
            "Oncology": ["Medical Oncology", "Surgical Oncology", "Radiation Oncology", "Hematology"],
            "Infectious Disease": ["HIV/AIDS", "Travel Medicine", "Transplant Infectious Disease"]
        })
        
        self.facility_types = self.network_config.get("facility_types", [
            "Hospital", "Clinic", "Ambulatory Surgery Center", "Urgent Care", "Imaging Center",
            "Laboratory", "Rehabilitation Center", "Skilled Nursing Facility", "Home Health Agency"
        ])
        
        self.facility_names = self.network_config.get("facility_names", [
            "Community", "Regional", "Memorial", "University", "General", "Saint", "Medical Center",
            "Health System", "Specialty", "Children's", "Women's", "Veterans", "County"
        ])
        
        self.facility_services = self.network_config.get("facility_services", [
            "Emergency Services", "Inpatient Care", "Outpatient Surgery", "Diagnostic Imaging",
            "Laboratory Services", "Physical Therapy", "Occupational Therapy", "Speech Therapy",
            "Cardiac Rehabilitation", "Pulmonary Rehabilitation", "Dialysis", "Infusion Therapy",
            "Wound Care", "Pain Management", "Behavioral Health", "Telehealth"
        ])
        
        self.accreditations = self.network_config.get("accreditations", [
            "Joint Commission", "NCQA", "AAAHC", "DNV GL", "CARF", "URAC", "ACHC", "CHAP"
        ])
        
        self.relationship_types = self.network_config.get("relationship_types", [
            "referral", "collaboration", "coverage", "consultation", "supervision"
        ])
        
        self.cities = self.network_config.get("cities", [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
            "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
            "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle",
            "Denver", "Boston"
        ])
        
        self.states = self.network_config.get("states", [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ])
        
        self.languages = self.network_config.get("languages", [
            "English", "Spanish", "Chinese", "French", "Tagalog", "Vietnamese",
            "Korean", "German", "Arabic", "Russian", "Italian", "Portuguese",
            "Hindi", "Polish", "Japanese", "Persian", "Gujarati", "Bengali"
        ])
        
    def generate_providers(self, count: int) -> List[Provider]:
        """
        Generate synthetic providers.
        
        Args:
            count: Number of providers to generate
            
        Returns:
            List of generated Provider objects
        """
        providers = []
        
        for _ in range(count):
            provider = Provider()
            
            # Set basic info
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            credentials = random.choice(self.credentials)
            gender = "M" if first_name in self.first_names[:10] else "F"
            
            provider.set_basic_info(first_name, last_name, credentials, gender)
            
            # Set specialty
            specialty = random.choice(self.specialties)
            subspecialty = None
            if specialty in self.subspecialties and random.random() < 0.7:
                subspecialty = random.choice(self.subspecialties[specialty])
                
            provider.set_specialty(specialty, subspecialty)
            
            # Set network status
            network_status = random.choices(
                ["in-network", "out-of-network", "preferred"],
                weights=[0.7, 0.2, 0.1]
            )[0]
            accepting_new_patients = random.random() < 0.8
            
            provider.set_network_status(network_status, accepting_new_patients)
            
            # Add languages
            provider.add_language("English")
            if random.random() < 0.3:
                provider.add_language(random.choice(self.languages[1:]))
            
            # Set contact info
            phone = f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            fax = f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            provider.set_contact_info(phone, email, fax)
            
            providers.append(provider)
        
        return providers
    
    def generate_facilities(self, count: int) -> List[Facility]:
        """
        Generate synthetic facilities.
        
        Args:
            count: Number of facilities to generate
            
        Returns:
            List of generated Facility objects
        """
        facilities = []
        
        for _ in range(count):
            facility = Facility()
            
            # Set basic info
            facility_type = random.choice(self.facility_types)
            name_prefix = random.choice(self.facility_names)
            name_suffix = facility_type
            city_name = random.choice(self.cities)
            
            name = f"{name_prefix} {city_name} {name_suffix}"
            
            facility.set_basic_info(name, facility_type)
            
            # Set address
            street = f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr', 'Rd'])}"
            city = city_name
            state = random.choice(self.states)
            zip_code = f"{random.randint(10000, 99999)}"
            
            facility.set_address(street, city, state, zip_code)
            
            # Set contact info
            phone = f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
            email = f"info@{name_prefix.lower()}{city_name.lower().replace(' ', '')}.example.com"
            website = f"https://www.{name_prefix.lower()}{city_name.lower().replace(' ', '')}.example.com"
            
            facility.set_contact_info(phone, email, website)
            
            # Set network status
            network_status = random.choices(
                ["in-network", "out-of-network", "preferred"],
                weights=[0.8, 0.1, 0.1]
            )[0]
            
            facility.set_network_status(network_status)
            
            # Add specialties
            specialty_count = random.randint(3, 10)
            specialties = random.sample(self.specialties, min(specialty_count, len(self.specialties)))
            
            for specialty in specialties:
                facility.add_specialty(specialty)
            
            # Add services
            service_count = random.randint(5, 15)
            services = random.sample(self.facility_services, min(service_count, len(self.facility_services)))
            
            for service in services:
                facility.add_service(service)
            
            # Add accreditations
            accreditation_count = random.randint(1, 3)
            accreditations = random.sample(self.accreditations, min(accreditation_count, len(self.accreditations)))
            
            for accreditation in accreditations:
                accreditation_date = datetime.now() - timedelta(days=random.randint(30, 1095))
                facility.add_accreditation(accreditation, accreditation_date)
            
            facilities.append(facility)
        
        return facilities
    
    def assign_practice_locations(self, providers: List[Provider], facilities: List[Facility]) -> None:
        """
        Assign practice locations to providers.
        
        Args:
            providers: List of providers
            facilities: List of facilities
        """
        for provider in providers:
            # Determine number of practice locations
            location_count = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            
            # Select random facilities
            selected_facilities = random.sample(facilities, min(location_count, len(facilities)))
            
            for facility in selected_facilities:
                # Create practice location
                location = {
                    "facility_id": facility.id,
                    "facility_name": facility.name,
                    "primary": len(provider.practice_locations) == 0,  # First location is primary
                    "address": facility.address.copy()
                }
                
                provider.add_practice_location(location)
                
                # Add provider to facility's affiliated providers
                affiliation_type = random.choice(["employed", "contracted", "admitting"])
                facility.add_affiliated_provider(provider.id, affiliation_type)
                
                # Add facility to provider's affiliations
                provider.add_affiliation(facility.id, affiliation_type)
    
    def generate_relationships(self, providers: List[Provider]) -> List[ProviderRelationship]:
        """
        Generate relationships between providers.
        
        Args:
            providers: List of providers
            
        Returns:
            List of generated ProviderRelationship objects
        """
        relationships = []
        provider_ids = [provider.id for provider in providers]
        provider_specialties = {provider.id: provider.specialty for provider in providers}
        
        # Create a set to track existing relationships
        existing_relationships: Set[Tuple[str, str]] = set()
        
        # Generate relationships based on specialty patterns
        for source_provider in providers:
            # Primary care providers refer to specialists
            if source_provider.specialty == "Primary Care":
                # Determine number of specialist relationships
                relationship_count = random.randint(5, 15)
                
                # Find specialists
                specialists = [p for p in providers if p.id != source_provider.id and p.specialty != "Primary Care"]
                
                if specialists:
                    # Select random specialists
                    selected_specialists = random.sample(specialists, min(relationship_count, len(specialists)))
                    
                    for target_provider in selected_specialists:
                        if (source_provider.id, target_provider.id) not in existing_relationships:
                            relationship = ProviderRelationship(
                                source_provider.id,
                                target_provider.id,
                                "referral"
                            )
                            
                            # Set referral count
                            referral_count = random.randint(1, 50)
                            relationship.set_referral_count(referral_count)
                            
                            # Add attributes
                            relationship.add_attribute("preferred", random.random() < 0.3)
                            relationship.add_attribute("reason", f"Referrals for {target_provider.specialty} care")
                            
                            relationships.append(relationship)
                            existing_relationships.add((source_provider.id, target_provider.id))
            
            # Specialists refer to other specialists
            else:
                # Determine number of relationships
                relationship_count = random.randint(3, 8)
                
                # Find other providers (excluding self)
                other_providers = [p for p in providers if p.id != source_provider.id]
                
                if other_providers:
                    # Select random providers
                    selected_providers = random.sample(other_providers, min(relationship_count, len(other_providers)))
                    
                    for target_provider in selected_providers:
                        if (source_provider.id, target_provider.id) not in existing_relationships:
                            # Determine relationship type
                            if target_provider.specialty == source_provider.specialty:
                                rel_type = random.choice(["collaboration", "coverage", "consultation"])
                            else:
                                rel_type = "referral"
                            
                            relationship = ProviderRelationship(
                                source_provider.id,
                                target_provider.id,
                                rel_type
                            )
                            
                            # Set referral count for referral relationships
                            if rel_type == "referral":
                                referral_count = random.randint(1, 30)
                                relationship.set_referral_count(referral_count)
                            
                            # Add attributes
                            if rel_type == "collaboration":
                                relationship.add_attribute("joint_cases", random.randint(1, 20))
                            elif rel_type == "coverage":
                                relationship.add_attribute("coverage_type", random.choice(["on-call", "vacation", "weekend"]))
                            elif rel_type == "consultation":
                                relationship.add_attribute("consultation_count", random.randint(1, 15))
                            
                            relationships.append(relationship)
                            existing_relationships.add((source_provider.id, target_provider.id))
        
        return relationships
    
    def generate(self, provider_count: int, facility_count: int) -> Dict[str, Any]:
        """
        Generate a synthetic provider network.
        
        Args:
            provider_count: Number of providers to generate
            facility_count: Number of facilities to generate
            
        Returns:
            Dictionary containing the generated provider network
        """
        # Generate providers
        providers = self.generate_providers(provider_count)
        
        # Generate facilities
        facilities = self.generate_facilities(facility_count)
        
        # Assign practice locations
        self.assign_practice_locations(providers, facilities)
        
        # Generate relationships
        relationships = self.generate_relationships(providers)
        
        # Convert to dictionaries
        provider_dicts = [provider.to_dict() for provider in providers]
        facility_dicts = [facility.to_dict() for facility in facilities]
        relationship_dicts = [relationship.to_dict() for relationship in relationships]
        
        return {
            "providers": provider_dicts,
            "facilities": facility_dicts,
            "relationships": relationship_dicts
        }