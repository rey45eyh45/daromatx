from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
import json
from urllib.parse import unquote

from database.repositories import CourseRepository, UserRepository

router = APIRouter()


class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration: int
    order: int
    is_free: bool
    
    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    stars_price: int
    ton_price: float = 0
    thumbnail: Optional[str]
    category: str
    duration: int
    is_active: bool
    lessons_count: int = 0
    is_purchased: bool = False
    
    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    lessons: List[LessonResponse] = []


@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    category: Optional[str] = Query(None, description="Kategoriya bo'yicha filter"),
    search: Optional[str] = Query(None, description="Qidiruv so'zi")
):
    """Barcha kurslarni olish"""
    course_repo = CourseRepository()
    
    if category:
        courses = await course_repo.get_courses_by_category(category)
    else:
        courses = await course_repo.get_all_active_courses()
    
    result = []
    for course in courses:
        if search and search.lower() not in course.title.lower():
            continue
        
        course_data = CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            price=course.price,
            stars_price=course.stars_price,
            thumbnail=course.thumbnail,
            category=course.category,
            duration=course.duration,
            is_active=course.is_active,
            lessons_count=len(course.lessons) if course.lessons else 0
        )
        result.append(course_data)
    
    return result


@router.get("/categories")
async def get_categories():
    """Kategoriyalar ro'yxati"""
    return {
        "categories": [
            {"id": "dasturlash", "name": "Dasturlash", "icon": "💻"},
            {"id": "dizayn", "name": "Dizayn", "icon": "🎨"},
            {"id": "marketing", "name": "Marketing", "icon": "📈"},
            {"id": "biznes", "name": "Biznes", "icon": "💼"},
            {"id": "tillar", "name": "Tillar", "icon": "🌍"},
            {"id": "boshqa", "name": "Boshqa", "icon": "📚"},
        ]
    }


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: int,
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
):
    """Bitta kursni olish"""
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    
    # Foydalanuvchi sotib olganmi tekshirish
    is_purchased = False
    if x_telegram_init_data:
        try:
            data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
            user_data = json.loads(unquote(data_parts.get('user', '{}')))
            telegram_id = user_data.get('id')
            
            if telegram_id:
                user_repo = UserRepository()
                user = await user_repo.get_user_by_telegram_id(telegram_id)
                if user and user.purchased_courses:
                    is_purchased = any(pc.course_id == course_id for pc in user.purchased_courses)
        except:
            pass
    
    lessons = []
    for lesson in course.lessons:
        lessons.append(LessonResponse(
            id=lesson.id,
            title=lesson.title,
            description=lesson.description,
            duration=lesson.duration,
            order=lesson.order,
            is_free=lesson.is_free
        ))
    
    return CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        price=course.price,
        stars_price=course.stars_price,
        thumbnail=course.thumbnail,
        category=course.category,
        duration=course.duration,
        is_active=course.is_active,
        lessons_count=len(lessons),
        lessons=lessons,
        is_purchased=is_purchased
    )
