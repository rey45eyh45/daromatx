from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories import UserRepository
from keyboards.main_kb import get_main_keyboard, get_mini_app_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start komandasi"""
    
    # Foydalanuvchini bazaga saqlash
    user_repo = UserRepository()
    await user_repo.create_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    welcome_text = f"""
🎓 <b>DAROMATX Academy</b>ga xush kelibsiz!

Salom, <b>{message.from_user.first_name}</b>! 👋

Bu yerda siz:
📚 Professional kurslarni sotib olishingiz
🎥 Video darslarni ko'rishingiz
📜 Sertifikat olishingiz mumkin!

⬇️ Boshlash uchun quyidagi tugmani bosing:
"""
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam komandasi"""
    
    help_text = """
📖 <b>Yordam</b>

🔹 /start - Botni qayta ishga tushirish
🔹 /courses - Kurslar ro'yxati
🔹 /my_courses - Mening kurslarim
🔹 /profile - Profil
🔹 /help - Yordam

❓ Savollar bo'lsa: @daromatx_support
"""
    
    await message.answer(help_text)


@router.message(F.text == "📚 Kurslar")
async def show_courses_button(message: Message):
    """Kurslar tugmasi"""
    await message.answer(
        "🎓 Kurslarni ko'rish uchun Mini App'ni oching:",
        reply_markup=get_mini_app_keyboard("courses")
    )


@router.message(F.text == "👤 Profil")
async def show_profile_button(message: Message):
    """Profil tugmasi"""
    await message.answer(
        "👤 Profilingizni ko'rish uchun Mini App'ni oching:",
        reply_markup=get_mini_app_keyboard("profile")
    )


@router.message(F.text == "📖 Mening kurslarim")
async def show_my_courses_button(message: Message):
    """Mening kurslarim tugmasi"""
    await message.answer(
        "📖 Sotib olingan kurslarni ko'rish:",
        reply_markup=get_mini_app_keyboard("my-courses")
    )
