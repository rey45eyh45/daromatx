from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from database.repositories import LessonRepository, UserRepository
from database.models import LessonProgress

router = APIRouter()


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
