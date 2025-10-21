import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

def load_model_and_tokenizer(model_name):
    """
    Loads the tokenizer and model from Hugging Face.
    Sets the model to evaluation mode and moves it to the appropriate device (GPU or CPU).
    """
    print(f"Loading model: {model_name}...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    # Set a padding token if it's not already set. This is good practice for some models.
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    model = GPT2LMHeadModel.from_pretrained(model_name)
    model.to(device)
    model.eval()
    
    print("Model and tokenizer loaded successfully.")
    return model, tokenizer, device

def generate_fitness_plan(prompt, model, tokenizer, device):
    """
    Generates a response from the model based on the input prompt.
    """
    print("Generating a personalized fitness plan for you, please wait...")
    try:
        # Encode the input prompt
        input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)

        # Generate text
        # max_new_tokens determines how many new words the model can generate after your prompt.
        # Adjust this value if the plan gets cut off.
        output_ids = model.generate(
            input_ids,
            max_new_tokens=1500,  # Increased token limit for a detailed plan
            num_return_sequences=1,
            no_repeat_ngram_size=2, # Helps prevent repetitive phrases
            early_stopping=True,
            temperature=0.7,      # Lower value makes the output more deterministic
            top_k=50              # Considers the 50 most likely next words
        )

        # Decode the generated ids to text
        full_response = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # The model's output includes the original prompt, so we remove it.
        generated_plan = full_response[len(prompt):].strip()
        
        return generated_plan

    except Exception as e:
        return f"\nError generating plan: {e}"

# --- Main execution ---
if __name__ == "__main__":
    # 1. Load the local model
    MODEL_NAME = "Lukamac/PlayPart-AI-Personal-Trainer"
    model, tokenizer, device = load_model_and_tokenizer(MODEL_NAME)

    # 2. Define User Profile and Goals (This part is unchanged)
    user_gender = "Male"
    user_age = 28
    user_height = 175  # unit: cm
    user_weight = 80   # unit: kg
    user_fitness_level = "Intermediate" # Choices: Beginner, Intermediate, Advanced
    user_primary_goal_choice = "Fat loss" # Fat loss or Muscle Building

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

    # 3. Construct the same detailed prompt (This part is unchanged)
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

    # 4. Generate the plan using the local model
    final_plan = generate_fitness_plan(prompt, model, tokenizer, device)

    # 5. Print the result
    print("\nYour exclusive plan has been generated!\n" + "="*40)
    print(final_plan)
    print("="*40)