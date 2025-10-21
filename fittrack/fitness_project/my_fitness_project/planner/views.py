from django.shortcuts import render
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file in your project root
load_dotenv()

def generate_plan(request):
    result_text = None
    error_text = None

    if request.method == 'POST':
        try:
            # --- API Call Logic Starts Here ---
            
            # 1. Configure API Key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file.")
                
            genai.configure(api_key=api_key)

            # 2. Define User Profile and Goals (as in your original script)
            user_gender = "Male"
            user_age = 28
            user_height = 175  # unit: cm
            user_weight = 80   # unit: kg
            user_fitness_level = "Intermediate" # Choices: Beginner, Intermediate, Advanced
            user_primary_goal_choice = "Fat loss" # Fat loss or Muscle Building

            # 3. Define Recent Training History
            training_history_summary = """
            * **Workout Frequency:** Averages 3-4 times per week.
            * **Workout Types:** Mix of full-body strength training and HIIT cardio.
            * **Sample Workouts:**
                * **2025-09-15:** Full Body Strength Training, 60 mins, 450 kcal, Avg Heart Rate: 135 bpm (Moderate Intensity)
                * **2025-09-17:** HIIT on Treadmill, 30 mins, 350 kcal, Avg Heart Rate: 155 bpm (High Intensity)
                * **2025-09-19:** Upper Body Strength (Push/Pull), 55 mins, 400 kcal, Avg Heart Rate: 130 bpm (Moderate Intensity)
                * **2025-09-22:** Lower Body Strength (Squats/Deadlifts), 60 mins, 500 kcal, Avg Heart Rate: 140 bpm (Moderate-High Intensity)
            """

            if user_primary_goal_choice == "Muscle building":
                detailed_goal = "Build lean muscle mass with a focus on hypertrophy, aiming to gain 1-2 kg of muscle."
            elif user_primary_goal_choice == "Fat loss":
                detailed_goal = "Lose body fat while preserving as much muscle as possible, aiming to lose 2-3 kg of fat."
            else:
                detailed_goal = "Improve overall fitness and health." 

            # 4. Construct the Full Prompt
            prompt = f"""
            You are an expert AI personal trainer and nutritionist named FitTrack AI. Your task is to create a comprehensive, 
            personalized, and actionable 4-week training and diet plan based on the user's detailed profile and recent activity. 
            The plan should be scientific, safe, and tailored to help the user achieve their goals.

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

            # 5. Call the Generative AI Model
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            result_text = response.text
            
            # --- API Call Logic Ends Here ---
        
        except Exception as e:
            # Store any errors to display on the webpage
            error_text = f"An error occurred while generating the plan: {e}"

    # 6. Prepare the context dictionary to pass data to the HTML template
    context = {
        'result': result_text,
        'error': error_text
    }
    
    # 7. Render the HTML page, passing the context to it
    return render(request, 'planner/index.html', context)