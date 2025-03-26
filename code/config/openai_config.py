from dotenv import load_dotenv
import os

load_dotenv()

class OpenAIConfig:
    API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4')
    TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0'))

    @classmethod
    def validate_config(cls):
        if not cls.API_KEY:
            raise ValueError("OpenAI API key is not set. Please set OPENAI_API_KEY in .env file") 