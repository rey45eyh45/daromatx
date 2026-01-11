from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories import UserRepository, CourseRepository
from keyboards.main_kb import get_main_keyboard, get_mini_app_keyboard

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep_link(message: Message, command: CommandObject, bot: Bot):
    """Start komandasi deep link bilan"""
    
    # Foydalanuvchini bazaga saqlash
    user_repo = UserRepository()
    await user_repo.create_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    args = command.args
    
    # Kurs sotib olish deep link
    if args and args.startswith("buy_"):
        course_id = int(args.replace("buy_", ""))
        
        course_repo = CourseRepository()
        course = await course_repo.get_course_by_id(course_id)
        
        if not course:
            await message.answer("❌ Kurs topilmadi!")
            return
        
        # Telegram Stars invoice yuborish
        await bot.send_invoice(
            chat_id=message.from_user.id,
            title=course.title,
            description=course.description[:255] if course.description else "Kurs",
            payload=f"course_{course_id}",
            provider_token="",  # Stars uchun bo'sh
            currency="XTR",  # Telegram Stars valyutasi
            prices=[LabeledPrice(label=course.title, amount=course.stars_price)],
            start_parameter=f"course_{course_id}"
        )
        return
    
    # Oddiy start
    await cmd_start_normal(message)


@router.message(CommandStart())
async def cmd_start_normal(message: Message):
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
