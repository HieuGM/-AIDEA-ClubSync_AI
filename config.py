import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'clubsync.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # NVIDIA API Configuration
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL') or 'meta/llama3-8b-instruct'
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '4000'))  # Tăng lên 4000