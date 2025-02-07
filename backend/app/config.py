import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    DATABASE_URL = os.getenv("DATABASE_URL")

    def __init__(self):
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET or not self.DATABASE_URL:
            raise ValueError("Missing environment variables. Please check your .env file.")

settings = Settings()
