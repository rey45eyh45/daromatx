from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories import CourseRepository
from keyboards.main_kb import get_mini_app_keyboard

router = Router()


@router.message(Command("courses"))
async def cmd_courses(message: Message):
    """Kurslar ro'yxati"""
    
    course_repo = CourseRepository()
    courses = await course_repo.get_all_active_courses()
    
    if not courses:
        await message.answer(
            "📚 Hozircha kurslar mavjud emas.\n"
            "Tez orada yangi kurslar qo'shiladi!"
        )
        return
    
    text = "📚 <b>Mavjud kurslar:</b>\n\n"
    
    for course in courses:
        text += f"🎓 <b>{course.title}</b>\n"
        text += f"💰 Narxi: {course.price:,} so'm\n"
        text += f"📝 {course.description[:100]}...\n\n"
    
    await message.answer(
        text=text,
        reply_markup=get_mini_app_keyboard("courses")
    )


@router.callback_query(F.data.startswith("course_"))
async def course_detail_callback(callback: CallbackQuery):
    """Kurs tafsilotlari"""
    
    course_id = int(callback.data.split("_")[1])
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    if not course:
        await callback.answer("Kurs topilmadi!", show_alert=True)
        return
    
    text = f"""
🎓 <b>{course.title}</b>

📝 {course.description}

📚 Darslar soni: {len(course.lessons)}
⏱ Davomiyligi: {course.duration} soat
💰 Narxi: {course.price:,} so'm

⭐ Telegram Stars: {course.stars_price} ⭐
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Sotib olish", callback_data=f"buy_{course_id}")
    builder.button(text="⭐ Stars bilan", callback_data=f"buy_stars_{course_id}")
    builder.button(text="⬅️ Orqaga", callback_data="courses_list")
    builder.adjust(2, 1)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()
