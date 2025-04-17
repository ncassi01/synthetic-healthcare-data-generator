-- Clinical Domain Database Schema

-- Clinical Encounters Table
CREATE TABLE IF NOT EXISTS clinical_encounters (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    class_type VARCHAR(50) NOT NULL,
    priority VARCHAR(50),
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP,
    length_of_stay INTEGER,
    admission_type VARCHAR(50),
    discharge_disposition VARCHAR(50),
    readmission BOOLEAN DEFAULT FALSE,
    chief_complaint TEXT,
    reason_code VARCHAR(50),
    service_type VARCHAR(50),
    account_number VARCHAR(50),
    visit_number VARCHAR(50),
    episode_of_care_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Encounter Participants Table
CREATE TABLE IF NOT EXISTS encounter_participants (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    participant_type VARCHAR(50) NOT NULL,
    participant_id VARCHAR(50) NOT NULL,
    role VARCHAR(50),
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    primary_participant BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Locations Table
CREATE TABLE IF NOT EXISTS encounter_locations (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    facility_id VARCHAR(50),
    department_id VARCHAR(50),
    location_type VARCHAR(50),
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    status VARCHAR(50),
    bed_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Diagnoses Table
CREATE TABLE IF NOT EXISTS encounter_diagnoses (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    condition_id VARCHAR(50),
    diagnosis_code VARCHAR(50) NOT NULL,
    diagnosis_description TEXT,
    diagnosis_type VARCHAR(50),
    present_on_admission BOOLEAN DEFAULT FALSE,
    rank INTEGER,
    provider_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Procedures Table
CREATE TABLE IF NOT EXISTS encounter_procedures (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    procedure_id VARCHAR(50),
    procedure_code VARCHAR(50) NOT NULL,
    procedure_description TEXT,
    datetime TIMESTAMP,
    duration_minutes INTEGER,
    provider_id VARCHAR(50),
    location_id VARCHAR(50),
    status VARCHAR(50),
    primary_procedure BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Clinical Notes Table (if not already exists)
CREATE TABLE IF NOT EXISTS clinical_notes (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50),
    member_id VARCHAR(50) NOT NULL,
    note_type VARCHAR(50),
    author_id VARCHAR(50),
    datetime TIMESTAMP,
    content TEXT,
    status VARCHAR(50),
    signed BOOLEAN DEFAULT FALSE,
    signed_datetime TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Services Table
CREATE TABLE IF NOT EXISTS encounter_services (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    service_id VARCHAR(50),
    service_code VARCHAR(50),
    service_description TEXT,
    provider_id VARCHAR(50),
    datetime TIMESTAMP,
    quantity INTEGER,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Assessments Table
CREATE TABLE IF NOT EXISTS encounter_assessments (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    assessment_type VARCHAR(50),
    datetime TIMESTAMP,
    provider_id VARCHAR(50),
    result JSONB,
    interpretation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Medications Table
CREATE TABLE IF NOT EXISTS encounter_medications (
    id VARCHAR(50) PRIMARY KEY,
    encounter_id VARCHAR(50) NOT NULL,
    medication_id VARCHAR(50),
    order_id VARCHAR(50),
    datetime TIMESTAMP,
    dose VARCHAR(50),
    route VARCHAR(50),
    provider_id VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES clinical_encounters(id)
);

-- Encounter Transitions Table
CREATE TABLE IF NOT EXISTS encounter_transitions (
    id VARCHAR(50) PRIMARY KEY,
    from_encounter_id VARCHAR(50) NOT NULL,
    to_encounter_id VARCHAR(50) NOT NULL,
    transition_type VARCHAR(50),
    datetime TIMESTAMP,
    reason TEXT,
    authorizing_provider_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_encounter_id) REFERENCES clinical_encounters(id),
    FOREIGN KEY (to_encounter_id) REFERENCES clinical_encounters(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_clinical_encounters_member_id ON clinical_encounters(member_id);
CREATE INDEX IF NOT EXISTS idx_clinical_encounters_type ON clinical_encounters(type);
CREATE INDEX IF NOT EXISTS idx_clinical_encounters_status ON clinical_encounters(status);
CREATE INDEX IF NOT EXISTS idx_clinical_encounters_start_datetime ON clinical_encounters(start_datetime);
CREATE INDEX IF NOT EXISTS idx_clinical_encounters_end_datetime ON clinical_encounters(end_datetime);

CREATE INDEX IF NOT EXISTS idx_encounter_participants_encounter_id ON encounter_participants(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_participants_participant_id ON encounter_participants(participant_id);

CREATE INDEX IF NOT EXISTS idx_encounter_locations_encounter_id ON encounter_locations(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_locations_facility_id ON encounter_locations(facility_id);

CREATE INDEX IF NOT EXISTS idx_encounter_diagnoses_encounter_id ON encounter_diagnoses(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_diagnoses_diagnosis_code ON encounter_diagnoses(diagnosis_code);

CREATE INDEX IF NOT EXISTS idx_encounter_procedures_encounter_id ON encounter_procedures(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_procedures_procedure_code ON encounter_procedures(procedure_code);

CREATE INDEX IF NOT EXISTS idx_clinical_notes_encounter_id ON clinical_notes(encounter_id);
CREATE INDEX IF NOT EXISTS idx_clinical_notes_member_id ON clinical_notes(member_id);

CREATE INDEX IF NOT EXISTS idx_encounter_services_encounter_id ON encounter_services(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_assessments_encounter_id ON encounter_assessments(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_medications_encounter_id ON encounter_medications(encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_transitions_from_encounter_id ON encounter_transitions(from_encounter_id);
CREATE INDEX IF NOT EXISTS idx_encounter_transitions_to_encounter_id ON encounter_transitions(to_encounter_id);