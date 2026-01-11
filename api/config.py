import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Database URL olish va formatlash"""
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db")
    
    # Railway PostgreSQL URL'ni asyncpg formatiga o'zgartirish
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return url


@dataclass
class Config:
    """Bot configuration"""
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: list[int] = None
    database_url: str = None
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_secret_key: str = os.getenv("API_SECRET_KEY", "secret")
    mini_app_url: str = os.getenv("MINI_APP_URL", "https://your-domain.com")
    
    def __post_init__(self):
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
        self.database_url = get_database_url()


config = Config()
