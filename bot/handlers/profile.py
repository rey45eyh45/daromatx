from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories import UserRepository, PaymentRepository

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Profil ko'rish"""
    
    user_repo = UserRepository()
    user = await user_repo.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("❌ Profil topilmadi. /start buyrug'ini yuboring.")
        return
    
    # Sotib olingan kurslar soni
    purchased_count = len(user.purchased_courses) if user.purchased_courses else 0
    username_display = user.username or "yo'q"
    created_date = user.created_at.strftime('%d.%m.%Y')
    
    text = f"""
👤 <b>Sizning profilingiz</b>

📛 Ism: {user.full_name}
🆔 Username: @{username_display}
📅 Ro'yxatdan o'tgan: {created_date}

📚 Sotib olingan kurslar: {purchased_count}
💰 Balans: {user.balance:,} so'm
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Mening kurslarim", callback_data="my_courses")
    builder.button(text="💳 To'lovlar tarixi", callback_data="payment_history")
    builder.button(text="⚙️ Sozlamalar", callback_data="settings")
    builder.adjust(1)
    
    await message.answer(text=text, reply_markup=builder.as_markup())


@router.message(Command("my_courses"))
async def cmd_my_courses(message: Message):
    """Mening kurslarim"""
    
    user_repo = UserRepository()
    user = await user_repo.get_user_by_telegram_id(message.from_user.id)
    
    if not user or not user.purchased_courses:
        await message.answer(
            "📚 Siz hali hech qanday kurs sotib olmagansiz.\n\n"
            "Kurslarni ko'rish uchun /courses buyrug'ini yuboring."
        )
        return
    
    text = "📖 <b>Mening kurslarim:</b>\n\n"
    
    for purchase in user.purchased_courses:
        course = purchase.course
        progress = purchase.progress or 0
        text += f"🎓 <b>{course.title}</b>\n"
        text += f"📊 Progress: {progress}%\n"
        text += f"{'▓' * (progress // 10)}{'░' * (10 - progress // 10)}\n\n"
    
    await message.answer(text)


@router.callback_query(F.data == "my_courses")
async def my_courses_callback(callback: CallbackQuery):
    """Mening kurslarim callback"""
    await cmd_my_courses(callback.message)
    await callback.answer()


@router.callback_query(F.data == "payment_history")
async def payment_history_callback(callback: CallbackQuery):
    """To'lovlar tarixi"""
    
    payment_repo = PaymentRepository()
    payments = await payment_repo.get_user_payments(callback.from_user.id)
    
    if not payments:
        await callback.answer("To'lovlar tarixi bo'sh", show_alert=True)
        return
    
    text = "💳 <b>To'lovlar tarixi:</b>\n\n"
    
    for payment in payments[-10:]:  # Oxirgi 10 ta
        status_emoji = "✅" if payment.status == "completed" else "⏳"
        text += f"{status_emoji} {payment.amount:,} so'm - {payment.created_at.strftime('%d.%m.%Y')}\n"
    
    await callback.message.edit_text(text)
    await callback.answer()
