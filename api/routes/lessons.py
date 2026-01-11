from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import os
import time
import hashlib

from database.repositories import LessonRepository, UserRepository
from database.models import LessonProgress

router = APIRouter()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
VIDEO_TOKEN_SECRET = os.getenv("VIDEO_TOKEN_SECRET", "daromatx_video_secret_2026")


class LessonResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    video_file_id: Optional[str]
    video_url: Optional[str]
    duration: int
    order: int
    is_free: bool
    
    class Config:
        from_attributes = True


class LessonWithProgressResponse(LessonResponse):
    is_completed: bool = False
    watched_seconds: int = 0


@router.get("/course/{course_id}", response_model=List[LessonResponse])
async def get_course_lessons(course_id: int):
    """Kurs darslari"""
    
    lesson_repo = LessonRepository()
    lessons = await lesson_repo.get_lessons_by_course(course_id)
    
    return [
        LessonResponse(
            id=lesson.id,
            course_id=lesson.course_id,
            title=lesson.title,
            description=lesson.description,
            video_file_id=lesson.video_file_id,
            video_url=lesson.video_url,
            duration=lesson.duration,
            order=lesson.order,
            is_free=lesson.is_free
        )
        for lesson in lessons
    ]


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Bitta darsni olish"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    lesson_repo = LessonRepository()
    lesson = await lesson_repo.get_lesson_by_id(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    
    # Kursni sotib olganligini tekshirish
    if not lesson.is_free:
        user_repo = UserRepository()
        user = await user_repo.get_user_by_telegram_id(telegram_id)
        
        if user:
            has_access = any(
                uc.course_id == lesson.course_id 
                for uc in (user.purchased_courses or [])
            )
            
            if not has_access:
                raise HTTPException(status_code=403, detail="Bu darsga kirishingiz yo'q. Kursni sotib oling.")
    
    return LessonResponse(
        id=lesson.id,
        course_id=lesson.course_id,
        title=lesson.title,
        description=lesson.description,
        video_file_id=lesson.video_file_id,
        video_url=lesson.video_url,
        duration=lesson.duration,
        order=lesson.order,
        is_free=lesson.is_free
    )


class UpdateProgressRequest(BaseModel):
    watched_seconds: int
    is_completed: bool = False


@router.post("/{lesson_id}/progress")
async def update_lesson_progress(
    lesson_id: int,
    request: UpdateProgressRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Dars progressini yangilash"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    # TODO: LessonProgress ni yangilash
    
    return {"success": True, "lesson_id": lesson_id}


def generate_video_token(lesson_id: int, telegram_id: int, expires: int) -> str:
    """Video uchun vaqtinchalik token yaratish"""
    data = f"{lesson_id}:{telegram_id}:{expires}:{VIDEO_TOKEN_SECRET}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def verify_video_token(lesson_id: int, telegram_id: int, expires: int, token: str) -> bool:
    """Tokenni tekshirish"""
    if time.time() > expires:
        return False
    expected = generate_video_token(lesson_id, telegram_id, expires)
    return token == expected


@router.get("/{lesson_id}/video-url")
async def get_video_url(
    lesson_id: int,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Video stream URL olish (1 soat amal qiladi)"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    lesson_repo = LessonRepository()
    lesson = await lesson_repo.get_lesson_by_id(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    
    # Kursni sotib olganligini tekshirish
    if not lesson.is_free:
        user_repo = UserRepository()
        user = await user_repo.get_user_by_telegram_id(telegram_id)
        
        if not user:
            raise HTTPException(status_code=403, detail="Foydalanuvchi topilmadi")
        
        has_access = any(
            uc.course_id == lesson.course_id 
            for uc in (user.purchased_courses or [])
        )
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Bu darsga kirishingiz yo'q")
    
    # Agar video_url bo'lsa, to'g'ridan-to'g'ri qaytarish
    if lesson.video_url:
        return {"video_url": lesson.video_url, "type": "direct"}
    
    # Telegram file_id bo'lsa, stream URL yaratish
    if lesson.video_file_id and BOT_TOKEN:
        try:
            # Telegram API'dan file path olish
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
                    params={"file_id": lesson.video_file_id},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        file_path = data["result"]["file_path"]
                        
                        # Vaqtinchalik token yaratish (1 soat)
                        expires = int(time.time()) + 3600
                        token = generate_video_token(lesson_id, telegram_id, expires)
                        
                        # Telegram file URL (bu URL 1 soat amal qiladi)
                        video_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                        
                        return {
                            "video_url": video_url,
                            "type": "telegram",
                            "expires": expires,
                            "token": token,
                            "watermark": f"@{user_data.get('username', telegram_id)}"
                        }
                        
        except Exception as e:
            print(f"Telegram API error: {e}")
            raise HTTPException(status_code=500, detail="Video yuklanmadi")
    
    raise HTTPException(status_code=404, detail="Video topilmadi")
