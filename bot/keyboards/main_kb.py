from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import config


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy klaviatura - Professional dizayn"""
    
    builder = ReplyKeyboardBuilder()
    # 1-qator: Kurslarni ko'rish (Mini App)
    builder.button(text="📚 Kurslarni ko'rish", web_app=WebAppInfo(url=config.mini_app_url))
    # 2-qator: Mening kurslarim va Profil
    builder.button(text="🎓 Mening kurslarim", web_app=WebAppInfo(url=f"{config.mini_app_url}/my-courses"))
    builder.button(text="👤 Profil", web_app=WebAppInfo(url=f"{config.mini_app_url}/profile"))
    # 3-qator: Qo'shimcha
    builder.button(text="💬 Qo'llab-quvvatlash")
    builder.button(text="📢 Kanal")
    builder.adjust(1, 2, 2)
    
    return builder.as_markup(resize_keyboard=True)


def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """Start xabaridagi inline tugmalar"""
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Kurslarni ko'rish",
        web_app=WebAppInfo(url=config.mini_app_url)
    )
    builder.button(
        text="🎓 Mening kurslarim",
        web_app=WebAppInfo(url=f"{config.mini_app_url}/my-courses")
    )
    builder.button(text="📢 Kanalga obuna bo'lish", url="https://t.me/daromatx")
    builder.adjust(1, 1, 1)
    
    return builder.as_markup()


def get_mini_app_keyboard(page: str = "") -> InlineKeyboardMarkup:
    """Mini App ochish tugmasi"""
    
    url = config.mini_app_url
    if page:
        url = f"{url}/{page}"
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Mini App'ni ochish",
        web_app=WebAppInfo(url=url)
    )
    
    return builder.as_markup()


def get_course_keyboard(course_id: int) -> InlineKeyboardMarkup:
    """Kurs uchun klaviatura"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Batafsil", callback_data=f"course_{course_id}")
    builder.button(text="💳 Sotib olish", callback_data=f"buy_{course_id}")
    builder.adjust(2)
    
    return builder.as_markup()


def get_payment_keyboard(course_id: int) -> InlineKeyboardMarkup:
    """To'lov usullari"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Telegram Stars", callback_data=f"buy_stars_{course_id}")
    builder.button(text="💳 Click", callback_data=f"pay_click_{course_id}")
    builder.button(text="💳 Payme", callback_data=f"pay_payme_{course_id}")
    builder.button(text="💎 TON", callback_data=f"pay_ton_{course_id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"course_{course_id}")
    builder.adjust(2, 2, 1)
    
    return builder.as_markup()
