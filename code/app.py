from flask import Flask
from api.routes import api_blueprint
from dotenv import load_dotenv
import os
from config.openai_config import OpenAIConfig

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Validate OpenAI configuration on startup
#OpenAIConfig.validate_config()

app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True) 