"""
AI Planner module for generating personalized fitness plans.
This module uses Google Gemini API for fitness plan generation.
"""
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def generate_fitness_plan_from_profile(user_profile, training_history_summary=""):
    """
    Generates a personalized fitness plan based on user profile using Gemini API.
    
    Args:
        user_profile: UserProfile model instance
        training_history_summary: Optional string containing training history
    
    Returns:
        str: Generated fitness plan text
    """
    try:
        # 1. Configure API Key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file. Please set your Gemini API key.")
        
        genai.configure(api_key=api_key)
        
        # 2. Extract user information from profile
        user_gender = user_profile.get_gender_display() if user_profile.gender else "Not specified"
        user_age = user_profile.age if user_profile.age else 25
        user_height = user_profile.height_cm if user_profile.height_cm else 170
        user_weight = user_profile.weight_kg if user_profile.weight_kg else 70
        user_fitness_level = user_profile.get_fitness_level_display() if user_profile.fitness_level else "Beginner"
        user_primary_goal_choice = user_profile.get_primary_goal_choice_display() if user_profile.primary_goal_choice else "General Fitness"
        
        # 3. Map goal choice to detailed goal
        if "Muscle" in user_primary_goal_choice or "Gain" in user_primary_goal_choice:
            detailed_goal = "Build lean muscle mass with a focus on hypertrophy, aiming to gain 1-2 kg of muscle."
        elif "Fat" in user_primary_goal_choice or "Loss" in user_primary_goal_choice:
            detailed_goal = "Lose body fat while preserving as much muscle as possible, aiming to lose 2-3 kg of fat."
        else:
            detailed_goal = "Improve overall fitness and health."
        
        # 4. Default training history if not provided
        if not training_history_summary:
            training_history_summary = """
* **Workout Frequency:** Based on your fitness level, we recommend starting with 3-4 times per week.
* **Workout Types:** A balanced mix of strength training and cardio.
"""
        
        # 5. Construct the prompt
        prompt = f"""
You are an expert AI personal trainer and nutritionist named FitTrack AI. Your task is to create a comprehensive, personalized, and actionable 4-week training and diet plan based on the user's detailed profile.

### User Profile
* **Gender:** {user_gender}
* **Age:** {user_age}
* **Height:** {user_height} cm
* **Weight:** {user_weight} kg
* **Fitness Level:** {user_fitness_level}
* **Primary Goal:** {detailed_goal}

### Recent Training History
{training_history_summary}

### Your Task
Generate a detailed 4-week plan in strict JSON format. Do not include any markdown formatting (like ```json) or explanatory text outside the JSON object. The JSON structure must be exactly as follows:

{{
  "training_plan": {{
    "summary": "Brief overview of the training strategy (1-2 sentences).",
    "weeks": [
      {{
        "week_number": 1,
        "focus": "Theme of the week (e.g., Foundation & Form)",
        "schedule": [
          {{
            "day": "Day 1",
            "type": "Workout Type (e.g., Upper Body Push)",
            "exercises": [
              {{
                "name": "Exercise Name",
                "sets": "3",
                "reps": "8-12",
                "notes": "Brief tip (optional)"
              }}
            ],
            "cardio": "Cardio details if applicable, else null"
          }},
          ... (cover 7 days, use "Rest Day" for type if resting)
        ]
      }},
      ... (Repeat for weeks 2, 3, 4)
    ]
  }},
  "diet_plan": {{
    "calories": "Daily target (e.g., 2500 kcal)",
    "macros": {{
      "protein": "Target in grams",
      "carbs": "Target in grams",
      "fats": "Target in grams"
    }},
    "guidelines": [
      "Guideline 1",
      "Guideline 2",
      "Guideline 3"
    ],
    "meals": [
      {{
        "type": "Breakfast",
        "options": ["Option 1", "Option 2"]
      }},
      {{
        "type": "Lunch",
        "options": ["Option 1", "Option 2"]
      }},
      {{
        "type": "Dinner",
        "options": ["Option 1", "Option 2"]
      }},
      {{
        "type": "Snacks",
        "options": ["Option 1", "Option 2"]
      }}
    ]
  }}
}}
"""
        
        # 6. Call the Generative AI Model (Gemini)
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        # Clean up the response to ensure it's valid JSON
        # Remove markdown code blocks if present
        clean_json = re.sub(r'```json\s*|\s*```', '', result_text).strip()
        
        # Parse JSON to ensure validity, then return the object (not string)
        # The view will handle passing this object to the template
        try:
            plan_data = json.loads(clean_json)
            return plan_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails - return text but wrapped in a structure
            return {"error": "Failed to parse AI response as JSON", "raw_text": result_text}
        
    except ValueError as ve:
        # API key or configuration error
        return {"error": f"Configuration Error: {str(ve)}", "details": "Please check your .env file and API key."}
    except Exception as e:
        # Other errors (API errors, network errors, etc.)
        error_type = type(e).__name__
        return {"error": f"Error generating plan ({error_type}): {str(e)}", "details": "Please check your internet connection and API quota."}

