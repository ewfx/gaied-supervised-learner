import google.generativeai as genai

# Replace with your actual API key
GOOGLE_API_KEY = "AIzaSyBW5ra-05J0z7_a6Ia-U9hS636Bq-HzEfA"

# Configure the API
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini model (free version is typically Gemini 1.5 Flash or Pro)
model = genai.GenerativeModel("gemini-2.0-flash")

# Send a prompt
response = model.generate_content("Write a poem about the moon in the style of Shakespeare.")

# Print the response
print(response.text)
