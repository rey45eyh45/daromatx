from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from database.base import async_session
from database.models import User, Course, Lesson, Payment, UserCourse, LessonProgress


class UserRepository:
    """Foydalanuvchi uchun repository"""
    
    async def create_or_update_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        full_name: str = ""
    ) -> User:
        """Foydalanuvchi yaratish yoki yangilash"""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.username = username
                user.full_name = full_name
                user.updated_at = datetime.utcnow()
            else:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name
                )
                session.add(user)
            
            await session.commit()
            await session.refresh(user)
            return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Telegram ID bo'yicha foydalanuvchi olish"""
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.purchased_courses).selectinload(UserCourse.course))
                .where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def get_users_count(self) -> int:
        """Foydalanuvchilar soni"""
        async with async_session() as session:
            result = await session.execute(select(func.count(User.id)))
            return result.scalar() or 0
    
    async def get_today_users_count(self) -> int:
        """Bugungi foydalanuvchilar soni"""
        async with async_session() as session:
            today = date.today()
            result = await session.execute(
                select(func.count(User.id))
                .where(func.date(User.created_at) == today)
            )
            return result.scalar() or 0
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Barcha foydalanuvchilar"""
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .order_by(User.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all())
    
    async def get_weekly_users_count(self) -> int:
        """Haftalik foydalanuvchilar soni"""
        async with async_session() as session:
            from datetime import timedelta
            week_ago = date.today() - timedelta(days=7)
            result = await session.execute(
                select(func.count(User.id))
                .where(func.date(User.created_at) >= week_ago)
            )
            return result.scalar() or 0
    
    async def get_monthly_users_count(self) -> int:
        """Oylik foydalanuvchilar soni"""
        async with async_session() as session:
            from datetime import timedelta
            month_ago = date.today() - timedelta(days=30)
            result = await session.execute(
                select(func.count(User.id))
                .where(func.date(User.created_at) >= month_ago)
            )
            return result.scalar() or 0
    
    async def get_previous_week_users_count(self) -> int:
        """O'tgan haftalik foydalanuvchilar (o'sish hisoblash uchun)"""
        async with async_session() as session:
            from datetime import timedelta
            week_ago = date.today() - timedelta(days=7)
            two_weeks_ago = date.today() - timedelta(days=14)
            result = await session.execute(
                select(func.count(User.id))
                .where(
                    func.date(User.created_at) >= two_weeks_ago,
                    func.date(User.created_at) < week_ago
                )
            )
            return result.scalar() or 0
    
    async def add_purchased_course(self, telegram_id: int, course_id: int) -> UserCourse:
        """Kursni sotib olish"""
        async with async_session() as session:
            # Foydalanuvchini topish
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("Foydalanuvchi topilmadi")
            
            # Allaqachon sotib olinganligini tekshirish
            result = await session.execute(
                select(UserCourse)
                .where(UserCourse.user_id == user.id, UserCourse.course_id == course_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                return existing
            
            user_course = UserCourse(user_id=user.id, course_id=course_id)
            session.add(user_course)
            await session.commit()
            await session.refresh(user_course)
            return user_course


class CourseRepository:
    """Kurs uchun repository"""
    
    async def create_course(
        self,
        title: str,
        description: str,
        price: float,
        stars_price: int = 100,
        ton_price: float = 0,
        thumbnail: Optional[str] = None,
        category: str = "Boshqa",
        author_id: Optional[int] = None
    ) -> Course:
        """Yangi kurs yaratish"""
        async with async_session() as session:
            course = Course(
                title=title,
                description=description,
                price=price,
                stars_price=stars_price,
                ton_price=ton_price,
                thumbnail=thumbnail,
                category=category,
                author_id=author_id
            )
            session.add(course)
            await session.commit()
            await session.refresh(course)
            return course
    
    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """ID bo'yicha kurs olish"""
        async with async_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.lessons))
                .where(Course.id == course_id)
            )
            return result.scalar_one_or_none()
    
    async def get_all_courses(self) -> List[Course]:
        """Barcha kurslar"""
        async with async_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.lessons))
                .order_by(Course.order, Course.created_at.desc())
            )
            return list(result.scalars().all())
    
    async def get_all_active_courses(self) -> List[Course]:
        """Barcha faol kurslar"""
        async with async_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.lessons))
                .where(Course.is_active == True)
                .order_by(Course.order, Course.created_at.desc())
            )
            return list(result.scalars().all())
    
    async def get_courses_by_category(self, category: str) -> List[Course]:
        """Kategoriya bo'yicha kurslar"""
        async with async_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.lessons))
                .where(Course.category == category, Course.is_active == True)
                .order_by(Course.order)
            )
            return list(result.scalars().all())
    
    async def get_courses_count(self) -> int:
        """Kurslar soni"""
        async with async_session() as session:
            result = await session.execute(select(func.count(Course.id)))
            return result.scalar() or 0
    
    async def get_lessons_count(self) -> int:
        """Jami darslar soni"""
        async with async_session() as session:
            result = await session.execute(select(func.count(Lesson.id)))
            return result.scalar() or 0
    
    async def get_top_courses(self, limit: int = 5) -> list:
        """Top kurslar (eng ko'p sotilgan)"""
        async with async_session() as session:
            result = await session.execute(
                select(
                    Course.id,
                    Course.title,
                    func.count(UserCourse.id).label('sales_count')
                )
                .outerjoin(UserCourse, Course.id == UserCourse.course_id)
                .group_by(Course.id, Course.title)
                .order_by(func.count(UserCourse.id).desc())
                .limit(limit)
            )
            rows = result.all()
            return [{"id": r[0], "title": r[1], "sales": r[2]} for r in rows]
    
    async def update_course(self, course_id: int, **kwargs) -> Optional[Course]:
        """Kursni yangilash"""
        async with async_session() as session:
            result = await session.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            
            if course:
                for key, value in kwargs.items():
                    if hasattr(course, key):
                        setattr(course, key, value)
                course.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(course)
            
            return course
    
    async def delete_course(self, course_id: int) -> bool:
        """Kursni o'chirish (barcha bog'liq ma'lumotlar bilan)"""
        async with async_session() as session:
            try:
                # 1. Darslarning progress'ini o'chirish
                lessons_result = await session.execute(
                    select(Lesson.id).where(Lesson.course_id == course_id)
                )
                lesson_ids = [row[0] for row in lessons_result.fetchall()]
                
                if lesson_ids:
                    await session.execute(
                        delete(LessonProgress).where(LessonProgress.lesson_id.in_(lesson_ids))
                    )
                
                # 2. Darslarni o'chirish
                await session.execute(
                    delete(Lesson).where(Lesson.course_id == course_id)
                )
                
                # 3. Kursni sotib olganlarni o'chirish
                await session.execute(
                    delete(UserCourse).where(UserCourse.course_id == course_id)
                )
                
                # 4. To'lovlarni o'chirish
                await session.execute(
                    delete(Payment).where(Payment.course_id == course_id)
                )
                
                # 5. Kursni o'chirish
                result = await session.execute(
                    select(Course).where(Course.id == course_id)
                )
                course = result.scalar_one_or_none()
                
                if course:
                    await session.delete(course)
                    await session.commit()
                    return True
                
                return False
            except Exception as e:
                await session.rollback()
                raise e
    
    async def update_course_thumbnail(self, course_id: int, thumbnail_url: str) -> Optional[Course]:
        """Kurs thumbnailini yangilash"""
        async with async_session() as session:
            result = await session.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            
            if course:
                course.thumbnail = thumbnail_url
                course.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(course)
            
            return course


class LessonRepository:
    """Dars uchun repository"""
    
    async def create_lesson(
        self,
        course_id: int,
        title: str,
        description: Optional[str] = None,
        video_file_id: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: int = 0,
        order: int = 0,
        is_free: bool = False
    ) -> Lesson:
        """Yangi dars yaratish"""
        async with async_session() as session:
            # Tartib raqamini aniqlash
            if order == 0:
                result = await session.execute(
                    select(func.max(Lesson.order)).where(Lesson.course_id == course_id)
                )
                max_order = result.scalar() or 0
                order = max_order + 1
            
            lesson = Lesson(
                course_id=course_id,
                title=title,
                description=description,
                video_file_id=video_file_id,
                video_url=video_url,
                duration=duration,
                order=order,
                is_free=is_free
            )
            session.add(lesson)
            await session.commit()
            await session.refresh(lesson)
            
            # Kurs davomiyligini yangilash
            await self._update_course_duration(session, course_id)
            
            return lesson
    
    async def _update_course_duration(self, session, course_id: int):
        """Kurs davomiyligini yangilash"""
        result = await session.execute(
            select(func.sum(Lesson.duration)).where(Lesson.course_id == course_id)
        )
        total_seconds = result.scalar() or 0
        
        result = await session.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        if course:
            course.duration = total_seconds // 3600  # Soatlarga aylantirish
            await session.commit()
    
    async def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """ID bo'yicha dars olish"""
        async with async_session() as session:
            result = await session.execute(
                select(Lesson).where(Lesson.id == lesson_id)
            )
            return result.scalar_one_or_none()
    
    async def get_lessons_by_course(self, course_id: int) -> List[Lesson]:
        """Kurs darslari"""
        async with async_session() as session:
            result = await session.execute(
                select(Lesson)
                .where(Lesson.course_id == course_id)
                .order_by(Lesson.order)
            )
            return list(result.scalars().all())
    
    async def update_lesson_video(
        self,
        lesson_id: int,
        video_file_id: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: int = 0
    ) -> Optional[Lesson]:
        """Dars videosini yangilash"""
        async with async_session() as session:
            result = await session.execute(
                select(Lesson).where(Lesson.id == lesson_id)
            )
            lesson = result.scalar_one_or_none()
            
            if lesson:
                if video_file_id:
                    lesson.video_file_id = video_file_id
                if video_url:
                    lesson.video_url = video_url
                if duration > 0:
                    lesson.duration = duration
                
                await session.commit()
                await session.refresh(lesson)
                
                # Kurs davomiyligini yangilash
                await self._update_course_duration(session, lesson.course_id)
            
            return lesson
    
    async def delete_lesson(self, lesson_id: int) -> bool:
        """Darsni o'chirish"""
        async with async_session() as session:
            result = await session.execute(
                select(Lesson).where(Lesson.id == lesson_id)
            )
            lesson = result.scalar_one_or_none()
            
            if lesson:
                course_id = lesson.course_id
                await session.delete(lesson)
                await session.commit()
                
                # Kurs davomiyligini yangilash
                await self._update_course_duration(session, course_id)
                return True
            
            return False


class PaymentRepository:
    """To'lov uchun repository"""
    
    async def create_payment(
        self,
        user_telegram_id: int,
        course_id: int,
        amount: float,
        currency: str = "UZS",
        payment_type: str = "click",
        status: str = "pending",
        transaction_id: Optional[str] = None
    ) -> Payment:
        """Yangi to'lov yaratish"""
        async with async_session() as session:
            # Foydalanuvchini topish
            result = await session.execute(
                select(User).where(User.telegram_id == user_telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("Foydalanuvchi topilmadi")
            
            payment = Payment(
                user_id=user.id,
                course_id=course_id,
                amount=amount,
                currency=currency,
                payment_type=payment_type,
                status=status,
                transaction_id=transaction_id
            )
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            return payment
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """ID bo'yicha to'lov olish"""
        async with async_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            return result.scalar_one_or_none()
    
    async def get_user_payments(self, user_telegram_id: int) -> List[Payment]:
        """Foydalanuvchi to'lovlari"""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return []
            
            result = await session.execute(
                select(Payment)
                .where(Payment.user_id == user.id)
                .order_by(Payment.created_at.desc())
            )
            return list(result.scalars().all())
    
    async def update_payment_status(
        self, 
        payment_id: int, 
        status: str,
        transaction_id: Optional[str] = None
    ) -> Optional[Payment]:
        """To'lov statusini yangilash"""
        async with async_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one_or_none()
            
            if payment:
                payment.status = status
                if transaction_id:
                    payment.transaction_id = transaction_id
                payment.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(payment)
            
            return payment
    
    async def get_payments_count(self) -> int:
        """Jami to'lovlar soni"""
        async with async_session() as session:
            result = await session.execute(
                select(func.count(Payment.id))
                .where(Payment.status == "completed")
            )
            return result.scalar() or 0
    
    async def get_today_payments_stats(self) -> dict:
        """Bugungi to'lovlar statistikasi"""
        async with async_session() as session:
            today = date.today()
            result = await session.execute(
                select(
                    func.count(Payment.id),
                    func.coalesce(func.sum(Payment.amount), 0)
                )
                .where(
                    Payment.status == "completed",
                    func.date(Payment.created_at) == today
                )
            )
            row = result.one()
            return {"count": row[0] or 0, "revenue": float(row[1] or 0)}
    
    async def get_weekly_payments_stats(self) -> dict:
        """Haftalik to'lovlar statistikasi"""
        async with async_session() as session:
            from datetime import timedelta
            week_ago = date.today() - timedelta(days=7)
            result = await session.execute(
                select(
                    func.count(Payment.id),
                    func.coalesce(func.sum(Payment.amount), 0)
                )
                .where(
                    Payment.status == "completed",
                    func.date(Payment.created_at) >= week_ago
                )
            )
            row = result.one()
            return {"count": row[0] or 0, "revenue": float(row[1] or 0)}
    
    async def get_monthly_payments_stats(self) -> dict:
        """Oylik to'lovlar statistikasi"""
        async with async_session() as session:
            from datetime import timedelta
            month_ago = date.today() - timedelta(days=30)
            result = await session.execute(
                select(
                    func.count(Payment.id),
                    func.coalesce(func.sum(Payment.amount), 0)
                )
                .where(
                    Payment.status == "completed",
                    func.date(Payment.created_at) >= month_ago
                )
            )
            row = result.one()
            return {"count": row[0] or 0, "revenue": float(row[1] or 0)}
    
    async def get_previous_week_revenue(self) -> float:
        """O'tgan haftalik daromad (o'sish hisoblash uchun)"""
        async with async_session() as session:
            from datetime import timedelta
            week_ago = date.today() - timedelta(days=7)
            two_weeks_ago = date.today() - timedelta(days=14)
            result = await session.execute(
                select(func.coalesce(func.sum(Payment.amount), 0))
                .where(
                    Payment.status == "completed",
                    func.date(Payment.created_at) >= two_weeks_ago,
                    func.date(Payment.created_at) < week_ago
                )
            )
            return float(result.scalar() or 0)
