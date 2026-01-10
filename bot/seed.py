import asyncio
from database.base import init_db, async_session
from database.models import Course, Lesson

async def main():
    await init_db()
    async with async_session() as s:
        c1 = Course(title="Python kurs", description="Python organing", price=299000, stars_price=150, category="Dasturlash", duration=1440, is_active=True)
        c2 = Course(title="Dizayn kurs", description="UI/UX dizayn", price=199000, stars_price=100, category="Dizayn", duration=960, is_active=True)
        c3 = Course(title="SMM kurs", description="Marketing", price=149000, stars_price=75, category="Marketing", duration=720, is_active=True)
        s.add_all([c1, c2, c3])
        await s.commit()
        print("3 ta kurs qoshildi")

asyncio.run(main())
