from dotenv import load_dotenv
import os

class Settings:
    """Configuration settings for the application."""
    
    def __init__(self):
        load_dotenv()

        # Database configuration
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_NAME = os.getenv("DB_NAME")

settings = Settings()