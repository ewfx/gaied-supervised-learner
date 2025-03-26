from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

class GeminiConfig:
    API_KEY = os.getenv('GOOGLE_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-2.0-flash')
    TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0'))

    @classmethod
    def initialize_gemini(cls):
        if not cls.API_KEY:
            raise ValueError("Google API key is not set. Please set GOOGLE_API_KEY in .env file")
        
        genai.configure(api_key=cls.API_KEY)
        return genai.GenerativeModel(model_name=cls.MODEL_NAME,
                                   generation_config={
                                       "temperature": cls.TEMPERATURE
                                   }) 