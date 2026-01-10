from typing import List
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from database.repositories import UserRepository, CourseRepository, PaymentRepository
from config import config

router = APIRouter()


def check_admin(telegram_id: int) -> bool:
    """Admin tekshirish"""
    return telegram_id in config.admin_ids


class StatsResponse(BaseModel):
    users_count: int
    courses_count: int
    today_users: int


class CourseCreateRequest(BaseModel):
    title: str
    description: str
    price: float
    stars_price: int = 100
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
