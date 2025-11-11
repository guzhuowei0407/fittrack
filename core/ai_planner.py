"""
AI Planner module for generating personalized fitness plans.
This module uses Google Gemini API for fitness plan generation.
"""
import google.generativeai as genai
import os
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
        
        # 5. Construct the prompt (same as your original prompt engineering)
        prompt = f"""
You are an expert AI personal trainer and nutritionist named FitTrack AI. Your task is to create a comprehensive, personalized, and actionable 4-week training and diet plan based on the user's detailed profile and recent activity. The plan should be scientific, safe, and tailored to help the user achieve their goals.

### User Profile
* **Gender:** {user_gender}
* **Age:** {user_age}
* **Height:** {user_height} cm
* **Weight:** {user_weight} kg
* **Fitness Level:** {user_fitness_level}
* **Primary Goal:** {detailed_goal}

### Recent Training History (Summary of the last month)
{training_history_summary}

### Your Task: Generate the 4-Week Plan

Based on all the information provided, generate a detailed 4-week plan.

**1. The 4-Week Training Plan:**
* **Structure:** Create a weekly split that balances intensity and recovery, for example, a Push/Pull/Legs or an Upper/Lower split.
* **Progressive Overload:** The plan must incorporate the principle of progressive overload. Show how the user can increase weight, reps, or intensity from Week 1 to Week 4.
* **Clarity:** For each training day, provide specific exercises (e.g., Bench Press, Barbell Squats, Lat Pulldowns), including the number of sets and repetitions (e.g., 3 sets of 8-12 reps).
* **Cardio:** Integrate 1-2 cardio sessions per week, specifying the type (e.g., LISS - Low-Intensity Steady State, or HIIT) and duration.
* **Rest:** Explicitly schedule at least two rest days per week.
* **Format:** Present the weekly schedule in a clear, easy-to-read table format for each of the 4 weeks.

**2. The 4-Week Diet Plan:**
* **Caloric & Macro Targets:** First, calculate and state the recommended daily calorie intake and macronutrient split (Protein, Carbs, Fat in grams) for the user's goal.
* **Nutritional Principles:** Provide 3-5 key nutritional guidelines for the user to follow (e.g., prioritize protein, choose complex carbs, stay hydrated).
* **Sample Meal Ideas:** Do not create a rigid daily meal plan. Instead, provide a list of healthy and easy-to-prepare sample meal ideas for Breakfast, Lunch, Dinner, and Snacks. This gives the user flexibility.
* **Integration:** The diet plan should directly support the energy demands of the training plan.

Please generate the complete, detailed plan now.
"""
        
        # 6. Call the Generative AI Model (Gemini)
        # Try gemini-2.5-flash first, fallback to gemini-1.5-flash if not available
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception:
            # Fallback to gemini-1.5-flash if 2.5 is not available
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        return result_text
        
    except ValueError as ve:
        # API key or configuration error
        return f"Configuration Error: {str(ve)}\n\nPlease check:\n1. Create a .env file in the project root\n2. Add: GEMINI_API_KEY=your_api_key_here\n3. Get your API key from: https://makersuite.google.com/app/apikey"
    except Exception as e:
        # Other errors (API errors, network errors, etc.)
        error_type = type(e).__name__
        return f"Error generating plan ({error_type}): {str(e)}\n\nPlease check:\n1. Your internet connection\n2. Your Gemini API key is valid\n3. You have API quota remaining"

