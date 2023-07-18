import os
from dotenv import load_dotenv

load_dotenv()


NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 4000))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.9))
OPENAI_STOP_SEQ = os.getenv('OPENAI_STOP_SEQ', '\n')