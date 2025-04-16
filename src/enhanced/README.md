# Enhanced Data Model Components (Phase 7)

This directory contains the enhanced data model components implemented as part of Phase 7 of the synthetic healthcare data generator project.

## Overview

The enhanced data model extends the existing data generation capabilities with more sophisticated healthcare data models, including care episodes, social determinants of health assessments, risk assessments, provider networks, pharmacy benefits, authorization rules, and data consistency validation.

## Components

### Care Episodes Generator (`care_episodes.py`)

Generates care episodes, which represent sequences of related healthcare events for a member. Each care episode includes:

- A primary condition or reason for the episode
- A start and end date
- A sequence of related healthcare events (encounters, procedures, etc.)
- Outcomes and status
- Associated providers and care team members

### SDOH Assessment Generator (`sdoh.py`)

Generates Social Determinants of Health (SDOH) assessments, which capture various social and environmental factors that affect health outcomes. Each SDOH assessment includes:

- Economic stability (employment, income, expenses, debt, medical bills)
- Education access and quality
- Healthcare access and quality
- Neighborhood and built environment
- Social and community context
- Food security
- Transportation access
- Housing stability

### Risk Assessment Generator (`risk_assessment.py`)

Generates comprehensive risk assessments for members, including clinical, financial, and care management risks. Each risk assessment includes:

- Clinical risk factors and scores
- Financial risk factors and scores
- Care management risk factors and scores
- Overall risk scores and stratification
- Risk trends over time
- Recommended interventions based on risk

### Provider Network Generator (`provider_network.py`)

Generates provider networks, including providers, facilities, and relationships between them. The provider network includes:

- Individual providers with specialties and credentials
- Healthcare facilities with services and specialties
- Relationships between providers (referrals, collaborations, etc.)
- Affiliations between providers and facilities

### Pharmacy Benefit Generator (`pharmacy.py`)

Generates pharmacy benefits and claims, including formularies, medication lists, and pharmacy-related claims. The pharmacy benefit includes:

- Medications with classifications and forms
- Formulary with tier structure and exclusions
- Pharmacy claims with fill information and costs

### Authorization Rules Engine (`auth_rules.py`)

Generates and applies authorization rules for healthcare services, determining when prior authorization is required and the criteria for approval or denial. The authorization rules engine includes:

- Rules for different service types
- Criteria for when authorization is required
- Exceptions to authorization requirements
- Approval and denial criteria
- Authorization decisions based on rules

### Data Consistency Validator (`consistency.py`)

Validates the consistency of generated data across different domains, ensuring that the data is realistic and coherent. The data consistency validator includes:

- Validation for member data
- Validation for claims data
- Validation for enhanced data models
- Cross-domain validation

## Usage

The enhanced data model components can be used through the `main_enhanced.py` module, which provides functions for generating and saving the enhanced data models. The `run_enhanced.py` script in the project root directory provides a convenient way to run the data generation process with the enhanced data models.

```bash
python run_enhanced.py --config config/config.json --output output
```

## Configuration

The enhanced data model components use the same configuration file as the rest of the project. The configuration file should include sections for each enhanced data model component, such as:

```json
{
  "care_episode_config": {
    "episodes_per_member": {
      "min": 0,
      "max": 3,
      "mean": 1
    }
  },
  "sdoh_config": {
    "assessments_per_member": {
      "min": 0,
      "max": 2,
      "mean": 1
    }
  },
  "risk_assessment_config": {
    "assessments_per_member": {
      "min": 1,
      "max": 3,
      "mean": 1
    }
  },
  "provider_network_config": {
    "provider_count": 100,
    "facility_count": 20
  },
  "pharmacy_benefit_config": {
    "medication_count": 200,
    "claims_per_member": {
      "min": 0,
      "max": 10,
      "mean": 3
    }
  },
  "authorization_rules_config": {
    "rule_count": 50,
    "decisions_per_member": {
      "min": 0,
      "max": 3,
      "mean": 1
    }
  },
  "consistency_validation_config": {
    "enabled": true
  }
}
```

## Integration with Existing System

The enhanced data model components are designed to work alongside the existing data generation system. They can be used independently or as part of the complete data generation process. The `run_enhanced.py` script demonstrates how to integrate the enhanced data models with the existing system.

## Future Extensions

The enhanced data model components provide a foundation for future extensions, such as:

- Database integration (Phase 8)
- RAG testing support (Phase 9)
- Scaling and optimization (Phase 10)

These extensions can build on the modular architecture established in Phase 7.