from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from pydantic import BaseModel
import os
import uuid
import aiofiles

from database.repositories import UserRepository, CourseRepository, PaymentRepository, LessonRepository
from config import config

router = APIRouter()

# Upload papkasi
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def check_admin(telegram_id: int) -> bool:
    """Admin tekshirish"""
    return telegram_id in config.admin_ids


class StatsResponse(BaseModel):
    users_count: int
    courses_count: int
    today_users: int


class AnalyticsResponse(BaseModel):
    # Asosiy statistika
    total_users: int
    total_courses: int
    total_lessons: int
    total_payments: int
    
    # Bugungi
    today_users: int
    today_payments: int
    today_revenue: float
    
    # Haftalik
    weekly_users: int
    weekly_payments: int
    weekly_revenue: float
    
    # Oylik
    monthly_users: int
    monthly_payments: int
    monthly_revenue: float
    
    # O'sish foizlari
    users_growth: float  # Haftalik o'sish %
    revenue_growth: float  # Haftalik daromad o'sishi %
    
    # Top kurslar
    top_courses: list


class CourseCreateRequest(BaseModel):
    title: str
    description: str
    price: float
    stars_price: int = 100
    ton_price: float = 0
    category: str = "Boshqa"


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Admin statistika"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    user_repo = UserRepository()
    course_repo = CourseRepository()
    
    return StatsResponse(
        users_count=await user_repo.get_users_count(),
        courses_count=await course_repo.get_courses_count(),
        today_users=await user_repo.get_today_users_count()
    )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Kengaytirilgan admin analitika"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    user_repo = UserRepository()
    course_repo = CourseRepository()
    payment_repo = PaymentRepository()
    
    # Asosiy statistika
    total_users = await user_repo.get_users_count()
    total_courses = await course_repo.get_courses_count()
    total_lessons = await course_repo.get_lessons_count()
    total_payments = await payment_repo.get_payments_count()
    
    # Bugungi
    today_users = await user_repo.get_today_users_count()
    today_stats = await payment_repo.get_today_payments_stats()
    
    # Haftalik
    weekly_users = await user_repo.get_weekly_users_count()
    weekly_stats = await payment_repo.get_weekly_payments_stats()
    
    # Oylik
    monthly_users = await user_repo.get_monthly_users_count()
    monthly_stats = await payment_repo.get_monthly_payments_stats()
    
    # O'sish hisoblash
    prev_week_users = await user_repo.get_previous_week_users_count()
    prev_week_revenue = await payment_repo.get_previous_week_revenue()
    
    users_growth = 0.0
    if prev_week_users > 0:
        users_growth = ((weekly_users - prev_week_users) / prev_week_users) * 100
    elif weekly_users > 0:
        users_growth = 100.0
    
    revenue_growth = 0.0
    if prev_week_revenue > 0:
        revenue_growth = ((weekly_stats["revenue"] - prev_week_revenue) / prev_week_revenue) * 100
    elif weekly_stats["revenue"] > 0:
        revenue_growth = 100.0
    
    # Top kurslar
    top_courses = await course_repo.get_top_courses(5)
    
    return AnalyticsResponse(
        total_users=total_users,
        total_courses=total_courses,
        total_lessons=total_lessons,
        total_payments=total_payments,
        today_users=today_users,
        today_payments=today_stats["count"],
        today_revenue=today_stats["revenue"],
        weekly_users=weekly_users,
        weekly_payments=weekly_stats["count"],
        weekly_revenue=weekly_stats["revenue"],
        monthly_users=monthly_users,
        monthly_payments=monthly_stats["count"],
        monthly_revenue=monthly_stats["revenue"],
        users_growth=round(users_growth, 1),
        revenue_growth=round(revenue_growth, 1),
        top_courses=top_courses
    )


@router.post("/courses")
async def create_course(
    request: CourseCreateRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Kurs yaratish"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    course_repo = CourseRepository()
    course = await course_repo.create_course(
        title=request.title,
        description=request.description,
        price=request.price,
        stars_price=request.stars_price,
        ton_price=request.ton_price,
        category=request.category,
        author_id=telegram_id
    )
    
    return {"success": True, "course_id": course.id}


@router.get("/users")
async def get_users(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    limit: int = 100,
    offset: int = 0
):
    """Foydalanuvchilar ro'yxati"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    user_repo = UserRepository()
    users = await user_repo.get_all_users(limit=limit, offset=offset)
    
    return {
        "users": [
            {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]
    }


def get_telegram_id_from_header(x_telegram_init_data: str) -> int:
    """Header'dan telegram_id olish"""
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        return user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")


@router.get("/courses")
async def get_all_courses(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Admin uchun barcha kurslar"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    course_repo = CourseRepository()
    courses = await course_repo.get_all_courses()
    
    return {
        "courses": [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": course.price,
                "stars_price": course.stars_price,
                "ton_price": getattr(course, 'ton_price', 0),
                "thumbnail": course.thumbnail,
                "category": course.category,
                "is_active": course.is_active,
                "lessons_count": len(course.lessons) if course.lessons else 0,
                "created_at": course.created_at.isoformat()
            }
            for course in courses
        ]
    }


@router.get("/courses/{course_id}")
async def get_course_detail(
    course_id: int,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Kurs detallari - darslar bilan"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "price": course.price,
        "stars_price": course.stars_price,
        "ton_price": getattr(course, 'ton_price', 0),
        "thumbnail": course.thumbnail,
        "category": course.category,
        "is_active": course.is_active,
        "lessons": [
            {
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "order": lesson.order,
                "duration": lesson.duration,
                "is_free": lesson.is_free,
                "video_file_id": lesson.video_file_id,
                "has_video": bool(lesson.video_file_id or lesson.video_url)
            }
            for lesson in (course.lessons or [])
        ]
    }


class LessonCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0
    duration: int = 0
    is_free: bool = False


@router.post("/courses/{course_id}/lessons")
async def create_lesson(
    course_id: int,
    request: LessonCreateRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Kursga yangi dars qo'shish"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    # Kurs mavjudligini tekshirish
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    
    # Order avtomatik aniqlash
    order = request.order
    if order == 0 and course.lessons:
        order = max(l.order for l in course.lessons) + 1
    elif order == 0:
        order = 1
    
    lesson_repo = LessonRepository()
    lesson = await lesson_repo.create_lesson(
        course_id=course_id,
        title=request.title,
        description=request.description,
        order=order,
        duration=request.duration,
        is_free=request.is_free
    )
    
    return {"success": True, "lesson_id": lesson.id, "order": order}


@router.post("/courses/{course_id}/thumbnail")
async def upload_thumbnail(
    course_id: int,
    file: UploadFile = File(...),
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Kursga thumbnail yuklash"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    # Fayl turini tekshirish
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Faqat JPG, PNG, WEBP formatlar ruxsat etilgan")
    
    # Fayl nomini yaratish
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"course_{course_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Faylni saqlash
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Database'ni yangilash
    course_repo = CourseRepository()
    thumbnail_url = f"/uploads/{filename}"
    await course_repo.update_course_thumbnail(course_id, thumbnail_url)
    
    return {"success": True, "thumbnail": thumbnail_url}


class VideoLinkRequest(BaseModel):
    video_file_id: Optional[str] = None
    video_url: Optional[str] = None
    duration: int = 0


@router.post("/lessons/{lesson_id}/video")
async def set_lesson_video(
    lesson_id: int,
    request: VideoLinkRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Darsga video qo'shish (Telegram file_id yoki URL)"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    if not request.video_file_id and not request.video_url:
        raise HTTPException(status_code=400, detail="video_file_id yoki video_url kerak")
    
    lesson_repo = LessonRepository()
    lesson = await lesson_repo.get_lesson_by_id(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    
    await lesson_repo.update_lesson_video(
        lesson_id=lesson_id,
        video_file_id=request.video_file_id,
        video_url=request.video_url,
        duration=request.duration
    )
    
    return {"success": True, "lesson_id": lesson_id}


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Kursni o'chirish"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    course_repo = CourseRepository()
    await course_repo.delete_course(course_id)
    
    return {"success": True}


@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Darsni o'chirish"""
    
    telegram_id = get_telegram_id_from_header(x_telegram_init_data)
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    lesson_repo = LessonRepository()
    await lesson_repo.delete_lesson(lesson_id)
    
    return {"success": True}
