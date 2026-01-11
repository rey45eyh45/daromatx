from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import hashlib
import hmac

from database.repositories import UserRepository
from config import config

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: str
    balance: float
    purchased_courses_count: int = 0
    
    class Config:
        from_attributes = True


class PurchasedCourseResponse(BaseModel):
    id: int
    course_id: int
    course_title: str
    progress: int
    
    class Config:
        from_attributes = True


def validate_telegram_data(init_data: str) -> Optional[dict]:
    """Telegram WebApp ma'lumotlarini tekshirish"""
    try:
        # Init data ni parse qilish
        data_parts = dict(x.split('=') for x in init_data.split('&'))
        
        # Hash ni olish
        received_hash = data_parts.pop('hash', None)
        if not received_hash:
            return None
        
        # Ma'lumotlarni saralash
        data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data_parts.items()))
        
        # Secret key yaratish
        secret_key = hmac.new(
            b'WebAppData',
            config.bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Hash ni hisoblash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if calculated_hash == received_hash:
            return data_parts
        
        return None
    except Exception:
        return None


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Joriy foydalanuvchi ma'lumotlari"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
        first_name = user_data.get('first_name', 'Foydalanuvchi')
        last_name = user_data.get('last_name', '')
        username = user_data.get('username')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="User ID not found")
    
    user_repo = UserRepository()
    user = await user_repo.get_user_by_telegram_id(telegram_id)
    
    # Agar foydalanuvchi topilmasa, avtomatik yaratish
    if not user:
        full_name = f"{first_name} {last_name}".strip()
        user = await user_repo.create_or_update_user(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name
        )
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        balance=user.balance,
        purchased_courses_count=len(user.purchased_courses) if user.purchased_courses else 0
    )


@router.get("/me/courses", response_model=List[PurchasedCourseResponse])
async def get_my_courses(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Foydalanuvchi sotib olgan kurslar"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    user_repo = UserRepository()
    user = await user_repo.get_user_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    result = []
    if user.purchased_courses:
        for uc in user.purchased_courses:
            result.append(PurchasedCourseResponse(
                id=uc.id,
                course_id=uc.course_id,
                course_title=uc.course.title if uc.course else "Noma'lum",
                progress=uc.progress
            ))
    
    return result


@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int):
    """Foydalanuvchi ma'lumotlari"""
    
    user_repo = UserRepository()
    user = await user_repo.get_user_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        balance=user.balance,
        purchased_courses_count=len(user.purchased_courses) if user.purchased_courses else 0
    )
