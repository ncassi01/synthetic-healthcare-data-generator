"""
Patient-generated health data generator for the synthetic healthcare data generator.

This module provides functionality to generate synthetic patient-generated health data
such as symptom tracking, daily logs, health journals, and other self-reported information.
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


class PatientGeneratedHealthDataGenerator(BaseGenerator):
    """Generator for synthetic patient-generated health data."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the patient-generated health data generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        super().__init__(config, seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # Extract configuration
        self.pgd_config = config.get('patient_generated_data_config', {})
        
    def generate(self, count: int, member_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic patient-generated health data.
        
        Args:
            count: Number of entries to generate.
            member_ids: Optional list of member IDs to associate with the data.
                If not provided, random IDs will be generated.
                
        Returns:
            List of generated patient-generated health data entries.
        """
        self.logger.info(f"Generating {count} patient-generated health data entries")
        
        if member_ids is None:
            # Generate random member IDs if not provided
            member_ids = [f"MEM{i:08d}" for i in range(count)]
        
        # If fewer member IDs than count, repeat member IDs
        if len(member_ids) < count:
            member_ids = (member_ids * (count // len(member_ids) + 1))[:count]
        
        entries = []
        
        # Generate different types of patient-generated data
        data_types = ['symptom_tracking', 'mood_journal', 'exercise_log', 'medication_adherence', 'food_diary']
        
        for i in range(count):
            data_type = random.choice(data_types)
            
            if data_type == 'symptom_tracking':
                entry = self._generate_symptom_tracking(member_ids[i])
            elif data_type == 'mood_journal':
                entry = self._generate_mood_journal(member_ids[i])
            elif data_type == 'exercise_log':
                entry = self._generate_exercise_log(member_ids[i])
            elif data_type == 'medication_adherence':
                entry = self._generate_medication_adherence(member_ids[i])
            elif data_type == 'food_diary':
                entry = self._generate_food_diary(member_ids[i])
            
            entries.append(entry)
            
        self.logger.info(f"Generated {len(entries)} patient-generated health data entries")
        return entries
    
    def _generate_symptom_tracking(self, member_id: str) -> Dict[str, Any]:
        """Generate a symptom tracking entry."""
        # Common symptoms
        symptoms = [
            "Headache", "Fatigue", "Nausea", "Dizziness", "Cough", 
            "Shortness of breath", "Chest pain", "Abdominal pain", 
            "Joint pain", "Muscle aches", "Fever", "Chills", 
            "Sore throat", "Runny nose", "Congestion"
        ]
        
        # Generate random date within the last 30 days
        entry_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Select 1-3 symptoms
        num_symptoms = random.randint(1, 3)
        selected_symptoms = random.sample(symptoms, num_symptoms)
        
        # Generate severity for each symptom (1-10 scale)
        symptom_details = {}
        for symptom in selected_symptoms:
            symptom_details[symptom] = {
                "severity": random.randint(1, 10),
                "duration": f"{random.randint(1, 24)} hours",
                "notes": self.faker.sentence() if random.random() > 0.5 else ""
            }
        
        # Create symptom value string
        symptom_value = ", ".join(selected_symptoms)
        
        return {
            "id": f"PGST{random.randint(10000, 99999)}",
            "member_id": member_id,
            "type": "symptom_tracking",
            "date": entry_date.strftime("%Y-%m-%d"),
            "time": entry_date.strftime("%H:%M"),
            "symptoms": symptom_details,
            "overall_feeling": random.choice(["Better", "Worse", "Same"]),
            "notes": f"Tracking symptoms: {', '.join(selected_symptoms)}. Overall feeling: {random.choice(['Better', 'Worse', 'Same'])}." if random.random() > 0.3 else "",
            # Add fields expected by web frontend
            "data_type": "symptom_tracking",
            "value": symptom_value
        }
    
    def _generate_mood_journal(self, member_id: str) -> Dict[str, Any]:
        """Generate a mood journal entry."""
        # Mood options
        moods = ["Happy", "Sad", "Anxious", "Calm", "Irritable", "Energetic", "Tired", "Stressed", "Relaxed"]
        
        # Generate random date within the last 30 days
        entry_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Select primary mood and intensity (1-10)
        primary_mood = random.choice(moods)
        mood_intensity = random.randint(1, 10)
        
        # Potential triggers
        triggers = [
            "Work stress", "Family conflict", "Financial concerns", "Health issues",
            "Lack of sleep", "Social interaction", "Exercise", "Weather", 
            "Medication change", "Diet", "None identified"
        ]
        
        selected_triggers = []
        if random.random() > 0.3:  # 70% chance of having triggers
            num_triggers = random.randint(1, 3)
            selected_triggers = random.sample(triggers, num_triggers)
        
        # Coping strategies
        coping_strategies = [
            "Deep breathing", "Meditation", "Exercise", "Talking with friend",
            "Therapy session", "Medication", "Journaling", "Music", 
            "Reading", "Outdoor activity", "None used"
        ]
        
        selected_strategies = []
        if random.random() > 0.4:  # 60% chance of using coping strategies
            num_strategies = random.randint(1, 3)
            selected_strategies = random.sample(coping_strategies, num_strategies)
        
        # Create mood value string
        mood_value = f"{primary_mood} ({mood_intensity}/10)"
        
        return {
            "id": f"PGMJ{random.randint(10000, 99999)}",
            "member_id": member_id,
            "type": "mood_journal",
            "date": entry_date.strftime("%Y-%m-%d"),
            "time": entry_date.strftime("%H:%M"),
            "mood": primary_mood,
            "intensity": mood_intensity,
            "secondary_moods": random.sample([m for m in moods if m != primary_mood], random.randint(0, 2)),
            "triggers": selected_triggers,
            "coping_strategies": selected_strategies,
            "sleep_hours": random.randint(4, 10) if random.random() > 0.2 else None,
            "notes": f"Feeling {primary_mood.lower()} today with intensity {mood_intensity}/10. " +
                    (f"Triggered by: {', '.join(selected_triggers)}. " if selected_triggers else "") +
                    (f"Coping with: {', '.join(selected_strategies)}." if selected_strategies else ""),
            # Add fields expected by web frontend
            "data_type": "mood_journal",
            "value": mood_value
        }
    
    def _generate_exercise_log(self, member_id: str) -> Dict[str, Any]:
        """Generate an exercise log entry."""
        # Exercise types
        exercise_types = [
            "Walking", "Running", "Cycling", "Swimming", "Weight training",
            "Yoga", "Pilates", "HIIT", "Elliptical", "Rowing", 
            "Basketball", "Tennis", "Soccer", "Hiking", "Dancing"
        ]
        
        # Generate random date within the last 30 days
        entry_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Select exercise type
        exercise_type = random.choice(exercise_types)
        
        # Generate duration (5-120 minutes)
        duration = random.randint(5, 120)
        
        # Generate intensity (1-10)
        intensity = random.randint(1, 10)
        
        # Generate calories burned (based on duration and intensity)
        calories = int(duration * intensity * random.uniform(2, 5))
        
        # Generate heart rate data
        heart_rate = {
            "average": random.randint(80, 160),
            "peak": random.randint(120, 190)
        }
        
        # Generate steps (if applicable)
        steps = None
        if exercise_type in ["Walking", "Running", "Hiking"]:
            steps = random.randint(1000, 15000)
        
        # Create exercise value string
        exercise_value = f"{exercise_type} for {duration} minutes"
        
        return {
            "id": f"PGEL{random.randint(10000, 99999)}",
            "member_id": member_id,
            "type": "exercise_log",
            "date": entry_date.strftime("%Y-%m-%d"),
            "time": entry_date.strftime("%H:%M"),
            "exercise_type": exercise_type,
            "duration_minutes": duration,
            "intensity": intensity,
            "calories_burned": calories,
            "heart_rate": heart_rate,
            "steps": steps,
            "distance_km": round(random.uniform(0.5, 15), 2) if exercise_type in ["Walking", "Running", "Cycling", "Swimming", "Hiking"] else None,
            "notes": f"Completed {exercise_type} workout for {duration} minutes at intensity level {intensity}/10. " +
                    f"Burned approximately {calories} calories. " +
                    (f"Took {steps} steps. " if steps else "") +
                    f"Average heart rate: {heart_rate['average']} bpm.",
            # Add fields expected by web frontend
            "data_type": "exercise_log",
            "value": exercise_value
        }
    
    def _generate_medication_adherence(self, member_id: str) -> Dict[str, Any]:
        """Generate a medication adherence entry."""
        # Common medications
        medications = [
            "Lisinopril", "Metformin", "Albuterol", "Atorvastatin", 
            "Levothyroxine", "Amlodipine", "Omeprazole", "Sertraline",
            "Ibuprofen", "Acetaminophen", "Losartan", "Simvastatin",
            "Metoprolol", "Hydrochlorothiazide", "Gabapentin"
        ]
        
        # Generate random date within the last 30 days
        entry_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Select 1-3 medications
        num_medications = random.randint(1, 3)
        selected_medications = random.sample(medications, num_medications)
        
        # Generate adherence data for each medication
        medication_details = {}
        for medication in selected_medications:
            taken = random.random() > 0.2  # 80% chance of taking medication
            medication_details[medication] = {
                "taken": taken,
                "scheduled_time": f"{random.randint(6, 22):02d}:00",
                "actual_time": f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}" if taken else None,
                "dose": f"{random.randint(1, 4)} {random.choice(['mg', 'g', 'mcg', 'tablet', 'capsule', 'ml'])}",
                "reason_if_missed": self.faker.sentence() if not taken else None
            }
        
        # Calculate how many medications were taken
        taken_count = sum(1 for med in medication_details.values() if med.get("taken", False))
        
        # Create medication value string
        medication_value = f"{taken_count}/{len(medication_details)} medications taken"
        
        return {
            "id": f"PGMA{random.randint(10000, 99999)}",
            "member_id": member_id,
            "type": "medication_adherence",
            "date": entry_date.strftime("%Y-%m-%d"),
            "medications": medication_details,
            "side_effects": self.faker.sentence() if random.random() > 0.7 else None,
            "notes": f"Medication adherence report: " +
                    f"Took {taken_count} out of {len(medication_details)} prescribed medications. " +
                    (f"Side effects: {self.faker.sentence()}" if random.random() > 0.7 else "No side effects reported."),
            # Add fields expected by web frontend
            "data_type": "medication_adherence",
            "value": medication_value
        }
    
    def _generate_food_diary(self, member_id: str) -> Dict[str, Any]:
        """Generate a food diary entry."""
        # Meal types
        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        
        # Generate random date within the last 30 days
        entry_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Select meal type
        meal_type = random.choice(meal_types)
        
        # Common food items by meal type
        food_items = {
            "Breakfast": [
                "Oatmeal", "Eggs", "Toast", "Cereal", "Yogurt", "Fruit", 
                "Smoothie", "Pancakes", "Waffles", "Bacon", "Sausage"
            ],
            "Lunch": [
                "Sandwich", "Salad", "Soup", "Wrap", "Leftovers", "Pasta",
                "Rice bowl", "Burger", "Pizza", "Sushi"
            ],
            "Dinner": [
                "Chicken", "Fish", "Beef", "Pork", "Pasta", "Rice", "Vegetables",
                "Stir fry", "Casserole", "Tacos", "Curry", "Pizza"
            ],
            "Snack": [
                "Fruit", "Nuts", "Yogurt", "Chips", "Crackers", "Granola bar",
                "Cheese", "Popcorn", "Cookies", "Candy"
            ]
        }
        
        # Select 1-4 food items for the meal
        num_items = random.randint(1, 4)
        selected_items = random.sample(food_items[meal_type], min(num_items, len(food_items[meal_type])))
        
        # Generate portion sizes and calories
        food_details = {}
        total_calories = 0
        
        for item in selected_items:
            calories = random.randint(50, 500)
            total_calories += calories
            
            food_details[item] = {
                "portion": f"{random.randint(1, 3)} {random.choice(['cup', 'oz', 'tbsp', 'serving', 'piece'])}",
                "calories": calories,
                "carbs_g": random.randint(0, 50),
                "protein_g": random.randint(0, 30),
                "fat_g": random.randint(0, 20)
            }
        
        # Generate hunger and fullness ratings (1-10)
        hunger_before = random.randint(1, 10)
        fullness_after = random.randint(1, 10)
        
        # Create food diary value string
        food_value = f"{meal_type}: {total_calories} calories"
        
        return {
            "id": f"PGFD{random.randint(10000, 99999)}",
            "member_id": member_id,
            "type": "food_diary",
            "date": entry_date.strftime("%Y-%m-%d"),
            "time": entry_date.strftime("%H:%M"),
            "meal_type": meal_type,
            "food_items": food_details,
            "total_calories": total_calories,
            "hunger_before": hunger_before,
            "fullness_after": fullness_after,
            "mood": random.choice(["Happy", "Sad", "Neutral", "Stressed", "Relaxed"]),
            "location": random.choice(["Home", "Work", "Restaurant", "Friend's house", "On the go"]),
            "notes": f"{meal_type} meal with {len(food_details)} items, totaling {total_calories} calories. " +
                    f"Hunger before: {hunger_before}/10, fullness after: {fullness_after}/10. " +
                    f"Mood: {random.choice(['Happy', 'Sad', 'Neutral', 'Stressed', 'Relaxed'])}. " +
                    f"Location: {random.choice(['Home', 'Work', 'Restaurant', 'Friend house', 'On the go'])}.",
            # Add fields expected by web frontend
            "data_type": "food_diary",
            "value": food_value
        }