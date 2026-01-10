import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Bot configuration"""
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: list[int] = None
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_secret_key: str = os.getenv("API_SECRET_KEY", "secret")
    mini_app_url: str = os.getenv("MINI_APP_URL", "https://your-domain.com")
    
    def __post_init__(self):
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]


config = Config()
