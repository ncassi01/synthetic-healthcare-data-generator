"""
Script to update patient-generated data to match the expected format for the web frontend.
"""

import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_patient_data():
    """Update patient-generated data to match the expected format for the web frontend."""
    # Define paths
    processed_dir = os.path.join('output', 'processed')
    raw_dir = os.path.join('output', 'raw')
    
    # Check if the processed directory exists
    if not os.path.exists(processed_dir):
        logger.error(f"Processed directory not found: {processed_dir}")
        return
    
    # Load patient-generated data
    pgd_path = os.path.join(processed_dir, 'patient_generated_data.json')
    if not os.path.exists(pgd_path):
        logger.error(f"Patient-generated data file not found: {pgd_path}")
        return
    
    try:
        with open(pgd_path, 'r') as f:
            pgd_data = json.load(f)
        
        logger.info(f"Loaded {len(pgd_data)} patient-generated data entries")
        
        # Update each entry to match the expected format
        updated_data = []
        for entry in pgd_data:
            updated_entry = {
                "id": entry.get("id", ""),
                "member_id": entry.get("member_id", ""),
                "date": entry.get("date", ""),
                "data_type": entry.get("type", ""),  # Rename 'type' to 'data_type'
                "notes": entry.get("notes", "")
            }
            
            # Add 'value' field based on the data type
            if entry.get("type") == "symptom_tracking":
                symptoms = entry.get("symptoms", {})
                if symptoms:
                    symptom_names = list(symptoms.keys())
                    updated_entry["value"] = ", ".join(symptom_names)
                else:
                    updated_entry["value"] = "No symptoms reported"
            
            elif entry.get("type") == "mood_journal":
                mood = entry.get("mood", "")
                intensity = entry.get("intensity", "")
                updated_entry["value"] = f"{mood} ({intensity}/10)" if mood and intensity else "Mood not specified"
            
            elif entry.get("type") == "exercise_log":
                exercise_type = entry.get("exercise_type", "")
                duration = entry.get("duration_minutes", "")
                updated_entry["value"] = f"{exercise_type} for {duration} minutes" if exercise_type and duration else "Exercise not specified"
            
            elif entry.get("type") == "medication_adherence":
                medications = entry.get("medications", {})
                if medications:
                    med_names = list(medications.keys())
                    taken_count = sum(1 for med in medications.values() if med.get("taken", False))
                    updated_entry["value"] = f"{taken_count}/{len(medications)} medications taken"
                else:
                    updated_entry["value"] = "No medications reported"
            
            elif entry.get("type") == "food_diary":
                meal_type = entry.get("meal_type", "")
                total_calories = entry.get("total_calories", "")
                updated_entry["value"] = f"{meal_type}: {total_calories} calories" if meal_type and total_calories else "Meal not specified"
            
            else:
                updated_entry["value"] = "Data not available"
            
            updated_data.append(updated_entry)
        
        logger.info(f"Updated {len(updated_data)} patient-generated data entries")
        
        # Save updated data
        with open(pgd_path, 'w') as f:
            json.dump(updated_data, f, indent=2)
        
        logger.info(f"Saved updated patient-generated data to {pgd_path}")
        
        # Also update the raw data if it exists
        raw_pgd_path = os.path.join(raw_dir, 'patient_generated_data.json')
        if os.path.exists(raw_pgd_path):
            with open(raw_pgd_path, 'w') as f:
                json.dump(updated_data, f, indent=2)
            logger.info(f"Saved updated patient-generated data to {raw_pgd_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating patient-generated data: {e}")
        return False

if __name__ == "__main__":
    update_patient_data()