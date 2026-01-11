from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import config


class Base(DeclarativeBase):
    """Base model"""
    pass


engine = create_async_engine(config.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Database yaratish"""
    from database.models import User, Course, Lesson, Payment, UserCourse
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Session olish"""
    async with async_session() as session:
        yield session
