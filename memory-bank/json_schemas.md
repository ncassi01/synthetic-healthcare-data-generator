# JSON File Schemas and Reference Guide

## Purpose

This document provides:
1. Examples of the structure of each JSON file in the output/processed directory
2. Instructions for the LLM to reference these examples instead of loading the full JSON files
3. Guidance on how to work with these files efficiently without hitting token limits

## Instructions for LLMs

When working with the JSON files in this project:

1. **DO NOT** attempt to load the full JSON files into your context, as they are very large and will exceed token limits
2. **INSTEAD**, refer to the schema examples in this document to understand the structure of each file
3. If you need to access specific data from these files:
   - Use the web application's API endpoints to query the data
   - Write Python code that loads and processes the files in chunks
   - Use database queries if the data has been loaded into a database
4. When generating code that works with these files, ensure it handles streaming or chunked processing

## JSON File Schemas

### authorizations.json

This file contains prior authorization requests for medical services.

```json
[
  {
    "id": "AUTH00000000",
    "member_id": "MEM00000018",
    "provider_id": "PRV85682",
    "date_requested": "2025-02-15",
    "status": "submitted",
    "service_lines": [
      {
        "service_code": "45378",
        "description": "Colonoscopy, diagnostic",
        "service_type": "outpatient",
        "quantity": 1,
        "unit_price": 627.57,
        "total_price": 627.57
      }
    ],
    "diagnosis_codes": ["M19.90", "J30.9", "E03.9"],
    "clinical_justification": "Patient with osteoarthritis requires outpatient due to persistent symptoms of back pain despite conservative management.",
    "authorization_type": "procedure",
    "date_decision": null,
    "decision_rationale": null,
    "expiration_date": null
  }
]
```

### authorization_rationales.json

This file contains detailed rationales for authorization decisions.

```json
[
  {
    "authorization_id": "AUTH00000003",
    "decision": "approved",
    "clinical_criteria_met": [
      "Documented failure of conservative treatment for 6 weeks",
      "Imaging confirms diagnosis",
      "Symptoms significantly impact daily activities"
    ],
    "guidelines_referenced": [
      "MCG Care Guidelines, 26th Edition",
      "Organization-specific criteria for migraine treatment"
    ],
    "reviewer_notes": "Patient meets all clinical criteria for inpatient admission with severe migraine complications including numbness and back pain.",
    "appeal_rights": null
  }
]
```

### authorization_rationales_stats.json

This file contains statistics about authorization rationales.

```json
{
  "total_rationales": 500,
  "by_decision": {
    "approved": 350,
    "denied": 100,
    "modified": 50
  },
  "top_clinical_criteria_met": [
    "Documented failure of conservative treatment",
    "Imaging confirms diagnosis",
    "Symptoms significantly impact daily activities"
  ],
  "top_guidelines_referenced": [
    "MCG Care Guidelines, 26th Edition",
    "Organization-specific criteria"
  ]
}
```

### care_plans.json

This file contains care plans for members.

```json
[
  {
    "id": "CP00000001",
    "member_id": "MEM00000042",
    "created_date": "2024-11-15",
    "updated_date": "2025-02-20",
    "care_manager_id": "CM00000023",
    "status": "active",
    "goals": [
      {
        "description": "Reduce HbA1c to below 7.0 within 6 months",
        "status": "in_progress",
        "target_date": "2025-05-15",
        "progress_notes": "Current HbA1c is 8.2, down from 9.1 at initial assessment"
      }
    ],
    "interventions": [
      {
        "type": "education",
        "description": "Diabetes self-management education",
        "frequency": "weekly",
        "status": "active",
        "notes": "Patient attending group sessions with good engagement"
      }
    ],
    "barriers": [
      "Transportation limitations",
      "Financial constraints for medication"
    ],
    "next_review_date": "2025-03-20"
  }
]
```

### care_plans_stats.json

This file contains statistics about care plans.

```json
{
  "total_care_plans": 350,
  "by_status": {
    "active": 275,
    "completed": 50,
    "discontinued": 25
  },
  "average_goals_per_plan": 3.2,
  "top_interventions": [
    "Medication management",
    "Education",
    "Referral to specialist"
  ],
  "top_barriers": [
    "Transportation limitations",
    "Financial constraints",
    "Low health literacy"
  ]
}
```

### claims.json

This file contains healthcare claims.

```json
[
  {
    "id": "CLM00000001",
    "member_id": "MEM00000056",
    "provider_id": "PRV00000078",
    "date_of_service": "2025-01-15",
    "date_received": "2025-01-20",
    "status": "paid",
    "claim_type": "professional",
    "diagnosis_codes": ["E11.9", "I10"],
    "service_lines": [
      {
        "service_code": "99214",
        "description": "Office visit, established patient, moderate complexity",
        "quantity": 1,
        "charge_amount": 165.00,
        "allowed_amount": 120.50,
        "paid_amount": 96.40,
        "member_responsibility": 24.10,
        "adjustment_reason": "contracted rate"
      }
    ],
    "total_charge": 165.00,
    "total_allowed": 120.50,
    "total_paid": 96.40,
    "total_member_responsibility": 24.10,
    "payment_date": "2025-02-01",
    "related_authorization_id": null
  }
]
```

### clinical_notes.json

This file contains clinical notes from healthcare providers.

```json
[
  {
    "id": "CN00000001",
    "member_id": "MEM00000029",
    "provider_id": "PRV00000045",
    "encounter_id": "ENC00000112",
    "date": "2025-02-10",
    "note_type": "progress_note",
    "chief_complaint": "Persistent cough for 2 weeks with fever",
    "history_of_present_illness": "Patient reports cough began 2 weeks ago, initially dry but now productive with yellow sputum. Fever up to 101°F, worse in evenings. Some shortness of breath with exertion. No chest pain.",
    "review_of_systems": "Respiratory: As above. Cardiovascular: No chest pain or palpitations. GI: No nausea, vomiting, or diarrhea. Constitutional: Fatigue, fever.",
    "physical_exam": "Vitals: Temp 100.2°F, HR 88, RR 18, BP 128/76, O2 97% RA. General: Alert, mild distress with coughing. HEENT: Oropharynx mildly erythematous. Lungs: Rhonchi in right middle lobe, no wheezes. Cardiac: Regular rate and rhythm, no murmurs.",
    "assessment": "1. Acute bronchitis, likely viral. 2. Hypertension, well-controlled.",
    "plan": "1. Symptomatic treatment with OTC cough suppressant at night, expectorant during day. 2. Increase fluid intake. 3. Rest for 2-3 days, then gradual return to activities. 4. Return if symptoms worsen or fever persists beyond 5 days. 5. Continue current hypertension medications.",
    "medications_prescribed": [
      {
        "name": "Guaifenesin",
        "dosage": "400mg",
        "frequency": "Every 4 hours as needed",
        "duration": "7 days"
      }
    ],
    "follow_up": "As needed, sooner if symptoms worsen"
  }
]
```

### clinical_notes_stats.json

This file contains statistics about clinical notes.

```json
{
  "total_notes": 1200,
  "by_note_type": {
    "progress_note": 750,
    "consultation": 250,
    "discharge_summary": 100,
    "procedure_note": 100
  },
  "average_length": 2500,
  "top_chief_complaints": [
    "Cough",
    "Back pain",
    "Headache",
    "Fever"
  ],
  "top_diagnoses": [
    "Hypertension",
    "Type 2 diabetes",
    "Acute bronchitis",
    "Low back pain"
  ]
}
```

### communications.json

This file contains communications between healthcare providers and members.

```json
[
  {
    "id": "COM00000001",
    "member_id": "MEM00000078",
    "provider_id": "PRV00000034",
    "date": "2025-01-22",
    "communication_type": "secure_message",
    "direction": "provider_to_member",
    "subject": "Your recent lab results",
    "content": "Hello Ms. Johnson, I've reviewed your recent lab work and I'm pleased to see your cholesterol levels have improved. Your LDL is now 110, down from 145 three months ago. This shows the medication and lifestyle changes are working well. Please continue with your current regimen, and we'll recheck in 6 months unless you have concerns before then.",
    "read_status": "read",
    "read_date": "2025-01-22",
    "response_id": "COM00000002"
  }
]
```

### communications_stats.json

This file contains statistics about communications.

```json
{
  "total_communications": 3500,
  "by_type": {
    "secure_message": 2000,
    "phone_call": 1000,
    "video_visit": 500
  },
  "by_direction": {
    "provider_to_member": 1800,
    "member_to_provider": 1700
  },
  "average_response_time_hours": 8.5,
  "top_subjects": [
    "Medication questions",
    "Lab results",
    "Appointment scheduling",
    "Symptom reporting"
  ]
}
```

### eobs.json

This file contains Explanation of Benefits (EOB) documents.

```json
[
  {
    "id": "EOB00000001",
    "member_id": "MEM00000056",
    "claim_id": "CLM00000001",
    "date_issued": "2025-02-02",
    "service_date_start": "2025-01-15",
    "service_date_end": "2025-01-15",
    "provider_name": "Dr. Sarah Williams",
    "provider_id": "PRV00000078",
    "service_lines": [
      {
        "service_description": "Office visit, established patient, moderate complexity",
        "service_code": "99214",
        "billed_amount": 165.00,
        "allowed_amount": 120.50,
        "not_covered_amount": 0.00,
        "discount_amount": 44.50,
        "deductible_amount": 0.00,
        "copay_amount": 20.00,
        "coinsurance_amount": 4.10,
        "plan_paid_amount": 96.40,
        "remark_codes": ["PR-2", "CO-42"]
      }
    ],
    "total_billed": 165.00,
    "total_allowed": 120.50,
    "total_not_covered": 0.00,
    "total_discount": 44.50,
    "total_deductible": 0.00,
    "total_copay": 20.00,
    "total_coinsurance": 4.10,
    "total_plan_paid": 96.40,
    "total_member_responsibility": 24.10,
    "year_to_date_deductible": 350.00,
    "year_to_date_out_of_pocket": 475.00,
    "appeal_rights": "You have the right to appeal this decision within 180 days."
  }
]
```

### insurance_communications.json

This file contains communications between insurance companies and members.

```json
[
  {
    "id": "INS_COM00000001",
    "member_id": "MEM00000042",
    "date": "2025-01-05",
    "communication_type": "letter",
    "subject": "Prior Authorization Decision",
    "content": "Dear Mr. Smith, We have reviewed your provider's request for prior authorization for an MRI of the lumbar spine. Based on the clinical information provided, this service has been approved. This authorization is valid for 60 days from the date of this letter. Please contact us if you have any questions.",
    "related_authorization_id": "AUTH00000025",
    "sent_status": "delivered",
    "delivery_date": "2025-01-08"
  }
]
```

### members.json

This file contains member demographic and insurance information.

```json
[
  {
    "id": "MEM00000001",
    "first_name": "John",
    "last_name": "Smith",
    "date_of_birth": "1975-06-15",
    "gender": "male",
    "address": {
      "street": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "zip": "62704"
    },
    "phone": "555-123-4567",
    "email": "john.smith@example.com",
    "insurance": {
      "plan_id": "PLN00000023",
      "plan_name": "Premium PPO",
      "member_id": "ABC123456789",
      "group_number": "GRP5555",
      "effective_date": "2024-01-01",
      "end_date": null
    },
    "primary_care_provider": {
      "id": "PRV00000045",
      "name": "Dr. Sarah Johnson"
    },
    "risk_score": 0.72,
    "conditions": [
      {
        "code": "I10",
        "description": "Essential hypertension",
        "onset_date": "2020-03-10"
      },
      {
        "code": "E78.5",
        "description": "Hyperlipidemia, unspecified",
        "onset_date": "2021-05-22"
      }
    ]
  }
]
```

### mental_health_narratives.json

This file contains mental health assessment narratives.

```json
[
  {
    "id": "MHN00000001",
    "member_id": "MEM00000033",
    "provider_id": "PRV00000089",
    "date": "2025-01-18",
    "assessment_type": "initial_evaluation",
    "presenting_problem": "Patient presents with symptoms of depression including persistent low mood, anhedonia, sleep disturbance, and difficulty concentrating for the past 3 months. Reports onset following job loss.",
    "mental_status_exam": "Appearance: Well-groomed, appropriately dressed. Behavior: Psychomotor retardation noted. Speech: Slow rate, low volume. Mood: 'Sad and empty.' Affect: Constricted, congruent with mood. Thought Process: Linear, logical. Thought Content: No SI/HI, no psychotic features. Cognition: Intact, though reports difficulty concentrating. Insight: Good. Judgment: Good.",
    "diagnosis": {
      "primary": {
        "code": "F32.1",
        "description": "Major depressive disorder, single episode, moderate"
      },
      "secondary": [
        {
          "code": "Z56.0",
          "description": "Unemployment, unspecified"
        }
      ]
    },
    "treatment_plan": "1. Individual therapy weekly for 12 weeks using CBT approach. 2. Consider antidepressant medication if symptoms don't improve within 4 weeks. 3. Sleep hygiene education. 4. Referral to employment support services.",
    "prognosis": "Good with treatment adherence. Patient demonstrates good insight and motivation for treatment."
  }
]
```

### patient_generated_data.json

This file contains data generated by patients, such as health diary entries.

```json
[
  {
    "id": "PGD00000001",
    "member_id": "MEM00000056",
    "date": "2025-02-10",
    "data_type": "symptom_diary",
    "content": "My blood pressure this morning was 142/88, which is higher than usual. I had a headache when I woke up that lasted about 2 hours. I took my medications as prescribed. I did notice I had more salt than usual yesterday at dinner. I'll make sure to watch my sodium intake today and see if my readings improve tomorrow.",
    "tags": ["blood_pressure", "headache", "medication_adherence"],
    "shared_with_provider": true,
    "provider_id": "PRV00000078",
    "provider_reviewed": true,
    "provider_review_date": "2025-02-11"
  }
]
```

### plans.json

This file contains insurance plan details.

```json
[
  {
    "id": "PLN00000001",
    "name": "Premium PPO",
    "type": "PPO",
    "year": 2025,
    "deductible": {
      "individual": 1000.00,
      "family": 2000.00
    },
    "out_of_pocket_max": {
      "individual": 5000.00,
      "family": 10000.00
    },
    "copays": {
      "primary_care": 20.00,
      "specialist": 40.00,
      "emergency_room": 250.00,
      "urgent_care": 50.00
    },
    "coinsurance": 0.20,
    "requires_referrals": false,
    "formulary_id": "FORM00000001",
    "network_id": "NET00000001",
    "benefits": [
      {
        "service_type": "preventive_care",
        "coverage": 1.00,
        "limitations": "As defined by ACA guidelines"
      },
      {
        "service_type": "hospitalization",
        "coverage": 0.80,
        "limitations": "Pre-authorization required for non-emergency admissions"
      }
    ]
  }
]
```

### provider_communications.json

This file contains communications between healthcare providers.

```json
[
  {
    "id": "PROV_COM00000001",
    "from_provider_id": "PRV00000045",
    "to_provider_id": "PRV00000089",
    "member_id": "MEM00000033",
    "date": "2025-01-15",
    "communication_type": "referral",
    "subject": "Referral for mental health evaluation",
    "content": "Dear Dr. Thompson, I'm referring Mr. Davis for evaluation of depressive symptoms. Patient reports persistent low mood, anhedonia, and sleep disturbance for approximately 3 months following job loss. No prior psychiatric history. Physical exam and lab work unremarkable. No evidence of thyroid dysfunction or other medical contributors. Patient is open to mental health treatment. Please evaluate and recommend appropriate treatment plan. Thank you.",
    "attachments": [
      {
        "type": "lab_results",
        "date": "2025-01-10",
        "description": "CBC, CMP, TSH results"
      }
    ],
    "urgency": "routine",
    "response_requested": true,
    "response_id": "PROV_COM00000002"
  }
]
```

### telehealth_documentation.json

This file contains documentation from telehealth visits.

```json
[
  {
    "id": "TH00000001",
    "member_id": "MEM00000042",
    "provider_id": "PRV00000045",
    "date": "2025-02-05",
    "visit_type": "video",
    "duration_minutes": 20,
    "chief_complaint": "Follow-up for diabetes management",
    "subjective": "Patient reports generally feeling well. Blood glucose readings ranging from 110-140 mg/dL fasting, 130-180 mg/dL postprandial. No hypoglycemic episodes. Following diet recommendations most days. Exercising 3 times per week for 30 minutes. No new symptoms.",
    "objective": "Appears well on video. No apparent distress. Home BP reading today: 132/78. Weight: 182 lbs (self-reported, down 3 lbs from last visit).",
    "assessment": "1. Type 2 diabetes mellitus, improving control. 2. Hypertension, well-controlled. 3. Hyperlipidemia, stable on therapy.",
    "plan": "1. Continue current medications. 2. Increase exercise goal to 45 minutes, 4 times weekly. 3. Lab work due - ordered A1C, lipid panel, CMP. 4. Follow up in 3 months.",
    "prescriptions_renewed": [
      {
        "medication": "Metformin",
        "dosage": "1000mg",
        "frequency": "twice daily",
        "quantity": 180,
        "refills": 3
      }
    ],
    "technical_quality": "good",
    "technical_issues": null
  }
]
```

### care_episodes.json

This file contains care episodes, which represent sequences of related healthcare events for a member.

```json
[
  {
    "id": "EP1A2B3C4D",
    "member_id": "MEM00000042",
    "episode_type": "chronic",
    "start_date": "2025-01-15T00:00:00",
    "end_date": null,
    "status": "active",
    "primary_condition": {
      "category": "Endocrine",
      "code": "E11.9",
      "name": "Type 2 Diabetes",
      "severity": "moderate",
      "is_primary": true
    },
    "events": [
      {
        "id": "EV1A2B3C4D",
        "type": "office_visit",
        "date": "2025-01-15T09:30:00",
        "provider_id": "PRV12345",
        "location": "Clinic",
        "notes": "Patient received office_visit service."
      },
      {
        "id": "EV2B3C4D5E",
        "type": "lab_test",
        "date": "2025-01-22T10:15:00",
        "provider_id": "PRV23456",
        "location": "Clinic",
        "notes": "Patient received lab_test service."
      }
    ],
    "providers": [
      {
        "id": "PRV12345",
        "name": "Dr. Smith",
        "specialty": "Endocrinology",
        "role": "attending"
      }
    ],
    "care_team": [
      {
        "id": "CTM12345",
        "name": "Jane Johnson",
        "role": "Care Manager",
        "start_date": "2025-01-15T00:00:00"
      }
    ],
    "goals": [
      {
        "id": "GL1A2B3C4D",
        "type": "disease_management",
        "description": "Maintain blood pressure below 140/90",
        "status": "active",
        "target_date": "2025-07-15T00:00:00"
      }
    ],
    "outcomes": []
  }
]
```

### sdoh_assessments.json

This file contains Social Determinants of Health (SDOH) assessments.

```json
[
  {
    "id": "SDOH1A2B3C4D",
    "member_id": "MEM00000056",
    "assessment_date": "2025-02-10T00:00:00",
    "provider_id": "PRV34567",
    "domains": {
      "economic_stability": {
        "score": 3,
        "notes": "Patient has some financial concerns. Employment is stable but income is limited. Occasionally struggles with expenses."
      },
      "education": {
        "score": 4,
        "notes": "College educated. Good health literacy. No educational barriers identified."
      },
      "healthcare_access": {
        "score": 2,
        "notes": "Some barriers to healthcare access. Insurance coverage with high out-of-pocket costs. Limited provider options."
      },
      "neighborhood": {
        "score": 3,
        "notes": "Moderately safe neighborhood. Some access to resources. Minor environmental concerns."
      },
      "social_context": {
        "score": 2,
        "notes": "Some social support. Moderate community engagement. Some social connections."
      },
      "food_security": {
        "score": 4,
        "notes": "Food secure. Regular access to nutritious food. No significant concerns about food access."
      },
      "transportation": {
        "score": 1,
        "notes": "No reliable transportation. Difficulty attending appointments. Limited mobility."
      },
      "housing": {
        "score": 3,
        "notes": "Housing is stable but may have some concerns (cost burden, maintenance issues, etc.)."
      }
    },
    "risk_factors": [
      {
        "category": "transportation",
        "description": "No reliable transportation",
        "severity": "high"
      },
      {
        "category": "healthcare",
        "description": "Delayed seeking care due to cost",
        "severity": "moderate"
      }
    ],
    "interventions": [
      {
        "type": "transportation_assistance",
        "description": "Arrangement for medical transportation service",
        "status": "recommended",
        "date_recommended": "2025-02-10T00:00:00"
      }
    ],
    "referrals": [
      {
        "service_type": "transportation_service",
        "organization": "Community Action Agency",
        "status": "pending",
        "date_referred": "2025-02-10T00:00:00"
      }
    ],
    "overall_risk_level": "moderate"
  }
]
```

### risk_assessments.json

This file contains comprehensive risk assessments for members.

```json
[
  {
    "id": "RA1A2B3C4D",
    "member_id": "MEM00000029",
    "assessment_date": "2025-02-15T00:00:00",
    "clinical_risk": {
      "score": 65.5,
      "level": "moderate",
      "factors": [
        {
          "type": "chronic_conditions",
          "description": "Multiple chronic conditions requiring complex management",
          "impact": "high",
          "modifiable": false
        },
        {
          "type": "medication_adherence",
          "description": "Poor adherence to prescribed medications",
          "impact": "high",
          "modifiable": true
        }
      ]
    },
    "financial_risk": {
      "score": 45.2,
      "level": "moderate",
      "factors": [
        {
          "type": "high_cost_claims",
          "description": "Recent high-cost claim > $50,000",
          "impact": "high",
          "modifiable": false
        }
      ]
    },
    "care_management_risk": {
      "score": 58.7,
      "level": "moderate",
      "factors": [
        {
          "type": "care_coordination_needs",
          "description": "Multiple providers requiring coordination",
          "impact": "moderate",
          "modifiable": true
        },
        {
          "type": "social_determinants",
          "description": "Transportation barriers to appointments",
          "impact": "moderate",
          "modifiable": true
        }
      ]
    },
    "overall_risk": {
      "score": 59.8,
      "level": "moderate",
      "stratification": "tier_3",
      "weights": {
        "clinical": 0.5,
        "financial": 0.2,
        "care_management": 0.3
      }
    },
    "risk_trends": [
      {
        "date": "2024-11-15T00:00:00",
        "score": 68.2,
        "level": "moderate"
      },
      {
        "date": "2024-12-15T00:00:00",
        "score": 65.5,
        "level": "moderate"
      },
      {
        "date": "2025-01-15T00:00:00",
        "score": 62.1,
        "level": "moderate"
      }
    ],
    "recommended_interventions": [
      {
        "category": "medication_management",
        "description": "Implement medication adherence program",
        "priority": "high",
        "status": "recommended",
        "date_recommended": "2025-02-15T00:00:00"
      },
      {
        "category": "care_coordination",
        "description": "Assign dedicated care manager",
        "priority": "high",
        "status": "recommended",
        "date_recommended": "2025-02-15T00:00:00"
      }
    ]
  }
]
```

### provider_network.json

This file contains provider network information, including providers, facilities, and relationships.

```json
{
  "providers": [
    {
      "id": "PRV1A2B3C4D",
      "npi": "1234567890",
      "first_name": "Sarah",
      "last_name": "Williams",
      "credentials": "MD",
      "specialty": "Cardiology",
      "subspecialty": "Interventional Cardiology",
      "practice_locations": [
        {
          "facility_id": "FAC1A2B3C4D",
          "facility_name": "Community Medical Center",
          "primary": true,
          "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62704"
          }
        }
      ],
      "affiliations": [
        {
          "organization_id": "FAC1A2B3C4D",
          "type": "employed",
          "start_date": "2023-06-15T00:00:00"
        }
      ],
      "network_status": "in-network",
      "accepting_new_patients": true,
      "languages": ["English", "Spanish"],
      "gender": "F",
      "contact_info": {
        "phone": "(555) 123-4567",
        "email": "sarah.williams@example.com",
        "fax": "(555) 123-4568"
      }
    }
  ],
  "facilities": [
    {
      "id": "FAC1A2B3C4D",
      "name": "Community Medical Center",
      "type": "Hospital",
      "address": {
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62704"
      },
      "contact_info": {
        "phone": "(555) 987-6543",
        "email": "info@communitymed.example.com",
        "website": "https://www.communitymed.example.com"
      },
      "network_status": "in-network",
      "specialties": ["Cardiology", "Orthopedics", "Neurology", "Oncology"],
      "services": ["Emergency Services", "Inpatient Care", "Outpatient Surgery", "Diagnostic Imaging"],
      "accreditations": [
        {
          "name": "Joint Commission",
          "date": "2024-05-10T00:00:00"
        }
      ],
      "affiliated_providers": [
        {
          "provider_id": "PRV1A2B3C4D",
          "type": "employed"
        }
      ]
    }
  ],
  "relationships": [
    {
      "id": "REL1A2B3C4D",
      "source_id": "PRV1A2B3C4D",
      "target_id": "PRV2B3C4D5E",
      "relationship_type": "referral",
      "start_date": "2024-06-15T00:00:00",
      "strength": 0.85,
      "referral_count": 42,
      "attributes": {
        "preferred": true,
        "reason": "Referrals for Neurology care"
      }
    }
  ]
}
```

### pharmacy_benefit.json

This file contains pharmacy benefit information, including medications, formulary, and pharmacy claims.

```json
{
  "medications": [
    {
      "id": "MED1A2B3C4D",
      "name": "Lisinopril",
      "generic_name": "Lisinopril",
      "ndc": "12345-678-90",
      "drug_class": "Antihypertensives",
      "therapeutic_class": "ACE Inhibitors",
      "form": "Tablet",
      "strength": "10 mg",
      "route": "Oral",
      "tier": 1,
      "prior_auth_required": false,
      "quantity_limits": null,
      "step_therapy": false,
      "specialty": false
    }
  ],
  "formulary": {
    "id": "FORM1A2B3C4D",
    "name": "Standard Formulary",
    "effective_date": "2025-01-01T00:00:00",
    "tier_structure": {
      "1": {
        "name": "Tier 1 - Generic",
        "description": "Lowest cost generic medications",
        "copay": 10,
        "coinsurance": 0
      },
      "2": {
        "name": "Tier 2 - Preferred Brand",
        "description": "Preferred brand-name medications",
        "copay": 30,
        "coinsurance": 0
      },
      "3": {
        "name": "Tier 3 - Non-Preferred Brand",
        "description": "Non-preferred brand-name medications",
        "copay": 60,
        "coinsurance": 0
      },
      "4": {
        "name": "Tier 4 - Specialty",
        "description": "High-cost specialty medications",
        "copay": 0,
        "coinsurance": 0.3
      }
    },
    "medications": [
      {
        "id": "MED1A2B3C4D",
        "name": "Lisinopril",
        "generic_name": "Lisinopril",
        "ndc": "12345-678-90",
        "drug_class": "Antihypertensives",
        "therapeutic_class": "ACE Inhibitors",
        "form": "Tablet",
        "strength": "10 mg",
        "route": "Oral",
        "tier": 1,
        "prior_auth_required": false,
        "quantity_limits": null,
        "step_therapy": false,
        "specialty": false
      }
    ],
    "exclusions": [
      {
        "medication_id": "MED2B3C4D5E",
        "reason": "Therapeutic alternative available"
      }
    ]
  },
  "pharmacy_claims": [
    {
      "id": "RX1A2B3C4D",
      "member_id": "MEM00000056",
      "medication_id": "MED1A2B3C4D",
      "pharmacy_id": "PHARM1A2B3C4D",
      "prescriber_id": "PRV12345",
      "fill_date": "2025-02-10T00:00:00",
      "days_supply": 30,
      "quantity": 30,
      "refill_number": 0,
      "total_refills": 3,
      "ndc": "12345-678-90",
      "drug_name": "Lisinopril",
      "drug_tier": 1,
      "total_cost": 15.50,
      "member_cost": 10.00,
      "plan_paid": 5.50,
      "status": "paid",
      "rejection_reason": null
    }
  ]
}
```

### authorization_rules.json

This file contains authorization rules and decisions.

```json
{
  "rules": [
    {
      "id": "RULE1A2B3C4D",
      "name": "Imaging MRI Authorization",
      "description": "Authorization rule for MRI imaging studies",
      "service_type": "imaging",
      "service_codes": ["70551", "72148", "73721", "74183", "70553"],
      "effective_date": "2025-01-01T00:00:00",
      "end_date": null,
      "criteria": {
        "high_radiation": {
          "description": "Authorization required for high-radiation imaging studies",
          "condition": {
            "operator": "in",
            "field": "service_code",
            "value": ["70551", "72148", "73721", "74183", "70553"]
          }
        }
      },
      "exceptions": [
        {
          "name": "emergency_exception",
          "description": "No authorization required for emergency imaging",
          "condition": {
            "operator": "equals",
            "field": "is_emergency",
            "value": true
          }
        }
      ],
      "approval_criteria": {
        "appropriate_indication": {
          "description": "Imaging is appropriate for the clinical indication",
          "condition": {
            "operator": "equals",
            "field": "has_appropriate_indication",
            "value": true
          }
        },
        "follows_guidelines": {
          "description": "Imaging request follows clinical guidelines",
          "condition": {
            "operator": "equals",
            "field": "follows_guidelines",
            "value": true
          }
        }
      },
      "denial_criteria": {
        "repeat_study": {
          "description": "Repeat study without change in clinical status",
          "condition": {
            "operator": "all",
            "conditions": [
              {
                "operator": "equals",
                "field": "is_repeat_study",
                "value": true
              },
              {
                "operator": "equals",
                "field": "has_clinical_change",
                "value": false
              }
            ]
          }
        }
      },
      "review_type": "radiology"
    }
  ],
  "decisions": [
    {
      "id": "DEC1A2B3C4D",
      "authorization_id": "AUTH00000025",
      "rule_id": "RULE1A2B3C4D",
      "decision": "approved",
      "decision_date": "2025-01-05T00:00:00",
      "rationale": "All approval criteria were met",
      "criteria_met": [
        {
          "name": "appropriate_indication",
          "details": "Approval criterion met"
        },
        {
          "name": "follows_guidelines",
          "details": "Approval criterion met"
        }
      ],
      "criteria_not_met": [],
      "reviewer_id": "REV12345",
      "reviewer_notes": "Patient meets all clinical criteria for MRI of lumbar spine."
    }
  ]
}
```

### validation_results.json

This file contains data consistency validation results.

```json
{
  "member_validation": {
    "errors": [
      {
        "type": "invalid_date_of_birth",
        "entity_type": "member",
        "entity_id": "MEM00000123",
        "field": "date_of_birth",
        "message": "Member MEM00000123 has a date of birth in the future: 2026-01-01"
      }
    ],
    "warnings": [
      {
        "type": "missing_insurance",
        "entity_type": "member",
        "entity_id": "MEM00000456",
        "field": "insurance",
        "message": "Member MEM00000456 has no insurance information"
      }
    ],
    "info": [
      {
        "type": "no_risk_factors",
        "entity_type": "member",
        "entity_id": "MEM00000789",
        "field": "risk_factors",
        "message": "Member MEM00000789 has no risk factors"
      }
    ]
  },
  "claims_validation": {
    "errors": [
      {
        "type": "invalid_member_reference",
        "entity_type": "claim",
        "entity_id": "CLM00000123",
        "field": "member_id",
        "message": "Claim CLM00000123 references non-existent member: MEM99999999"
      }
    ],
    "warnings": [
      {
        "type": "no_service_lines",
        "entity_type": "claim",
        "entity_id": "CLM00000456",
        "field": "service_lines",
        "message": "Claim CLM00000456 has no service lines"
      }
    ],
    "info": []
  },
  "enhanced_validation": {
    "errors": [
      {
        "type": "invalid_member_reference",
        "entity_type": "care_episode",
        "entity_id": "EP00000123",
        "field": "member_id",
        "message": "Care episode EP00000123 references non-existent member: MEM99999999"
      }
    ],
    "warnings": [
      {
        "type": "missing_required_field",
        "entity_type": "provider",
        "entity_id": "PRV00000456",
        "field": "specialty",
        "message": "Provider PRV00000456 is missing required field: specialty"
      }
    ],
    "info": []
  },
  "cross_domain_validation": {
    "errors": [],
    "warnings": [
      {
        "type": "missing_authorization",
        "entity_type": "claim",
        "entity_id": "CLM00000789",
        "field": "service_type",
        "message": "Claim CLM00000789 for service type 'imaging' has no matching authorization"
      }
    ],
    "info": [
      {
        "type": "note_without_claim",
        "entity_type": "clinical_note",
        "entity_id": "CN00000123",
        "field": "date",
        "message": "Clinical note CN00000123 has no matching claim on the same date"
      }
    ]
  }
}
```

## Working with Large JSON Files

### Python Code Example: Processing Files in Chunks

```python
import json

def process_json_in_chunks(file_path, chunk_size=1000):
    """Process a large JSON file in chunks."""
    with open(file_path, 'r') as f:
        # Assuming the file contains a JSON array
        f.read(1)  # Skip the opening '['
        
        chunk = []
        for line in f:
            if line.strip() in ('[', ']'):
                continue
                
            # Remove trailing comma if present
            if line.rstrip().endswith(','):
                line = line.rstrip()[:-1]
                
            try:
                # Try to parse this line as a complete JSON object
                item = json.loads(line)
                chunk.append(item)
                
                if len(chunk) >= chunk_size:
                    process_chunk(chunk)
                    chunk = []
            except json.JSONDecodeError:
                # If this line isn't a complete JSON object, it might be part of a multi-line object
                # In a real implementation, you'd need to handle this case
                pass
                
        # Process any remaining items
        if chunk:
            process_chunk(chunk)

def process_chunk(chunk):
    """Process a chunk of JSON data."""
    # Replace this with your actual processing logic
    print(f"Processing chunk with {len(chunk)} items")
    for item in chunk:
        # Do something with each item
        pass

# Example usage
process_json_in_chunks('output/processed/authorizations.json')
```

### Web API Example: Querying Data

```python
import requests

def get_authorizations_for_member(member_id, api_base_url="http://localhost:5000/api"):
    """Get authorizations for a specific member using the web API."""
    url = f"{api_base_url}/members/{member_id}/authorizations"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
authorizations = get_authorizations_for_member("MEM00000042")
if authorizations:
    for auth in authorizations:
        print(f"Authorization ID: {auth['id']}, Status: {auth['status']}")
```

## Best Practices for LLMs

1. **Schema Understanding**: Use the schemas in this document to understand the structure of each JSON file
2. **Selective Access**: Only access the specific data you need, not entire files
3. **Chunked Processing**: Process large files in chunks or streams
4. **API First**: Use the web application's API endpoints when available
5. **Memory Efficiency**: Be mindful of memory usage when working with large datasets
6. **Error Handling**: Include robust error handling for file operations
7. **Validation**: Validate data against expected schemas
8. **Documentation**: Document any assumptions about the data structure

## Update History

[2025-03-20 11:38:00] - Added schemas for enhanced data models (Phase 7)
[2025-03-20 08:48:00] - Created initial JSON schemas reference document