"""
Data models for the synthetic healthcare data generator.

This module contains data models for representing healthcare entities.
"""

# Import clinical domain models
from .clinical import (
    ClinicalEncounter,
    EncounterParticipant,
    EncounterLocation,
    EncounterDiagnosis,
    EncounterProcedure,
    ClinicalNote,
    EncounterService,
    EncounterAssessment,
    EncounterMedication,
    EncounterTransition,
    # Enums
    EncounterType,
    EncounterStatus,
    EncounterClass,
    EncounterPriority,
    AdmissionType,
    DischargeDisposition,
    ServiceType,
    ParticipantType,
    ProviderRole,
    LocationType,
    LocationStatus,
    DiagnosisType,
    ProcedureStatus,
    NoteType,
    NoteStatus,
    ServiceStatus,
    AssessmentType,
    MedicationRoute,
    MedicationStatus,
    TransitionType,
    ValidationSeverity,
    ValidationResult
)