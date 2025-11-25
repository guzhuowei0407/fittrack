import google.generativeai as genai

# 1. Configure your API key
api_key = 'AIzaSyALFlkVqMr8OM7OULxHc7oox59b0xeEDBM'  # Replace with your own API key
genai.configure(api_key=api_key)

# 2. Create model instance
# We use 'gemini-1.5-flash-latest'
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. Call the model to generate content
try:
    prompt = "Explain how AI works in a few words"
    response = model.generate_content(prompt)

    # 4. Print the result
    print(response.text)

except Exception as e:
    print(f"Error: {e}")
