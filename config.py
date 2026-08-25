import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Required
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        
        # Optional - AI Services
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY')
        self.STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
        
        # Database
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///promocanvas.db')
        
        # Redis (optional, for caching)
        self.REDIS_URL = os.getenv('REDIS_URL')
        
        # Server
        self.PORT = int(os.getenv('PORT', 5000))
        self.WEBHOOK_URL = os.getenv('WEBHOOK_URL')
        
        # Validate required config
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required. Get it from @BotFather.")
