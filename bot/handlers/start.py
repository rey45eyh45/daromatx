from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories import UserRepository, CourseRepository
from keyboards.main_kb import get_main_keyboard, get_start_inline_keyboard

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
🎓 <b>DAROMATX Academy</b>

Assalomu alaykum, <b>{message.from_user.first_name}</b>! 👋

Bizning platformada:
• 📚 Professional video kurslar
• 🎯 Amaliy bilimlar
• 📜 Sertifikatlar
• 💬 Mentor yordami

<i>O'z sohasida professional bo'ling!</i>
"""
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard()
    )
    
    # Inline tugmalar bilan qo'shimcha xabar
    await message.answer(
        text="⬇️ Boshlash uchun quyidagilardan birini tanlang:",
        reply_markup=get_start_inline_keyboard()
    )


# Qo'llab-quvvatlash tugmasi handler
@router.message(F.text == "💬 Qo'llab-quvvatlash")
async def support_handler(message: Message):
    """Qo'llab-quvvatlash"""
    
    support_text = """
💬 <b>Qo'llab-quvvatlash</b>

Savollaringiz bo'lsa, biz bilan bog'laning:

📩 Admin: @daromatx_admin
📧 Email: support@daromatx.uz
⏰ Ish vaqti: 9:00 - 21:00

Yoki quyidagi savollar bo'yicha yordam oling:

❓ <b>Ko'p so'raladigan savollar:</b>
• To'lov qanday amalga oshiriladi?
• Kurslarni qanday ko'raman?
• Sertifikat qachon beriladi?
"""
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="📩 Admin bilan bog'lanish", url="https://t.me/daromatx_admin")
    builder.button(text="❓ Ko'p so'raladigan savollar", callback_data="faq")
    builder.adjust(1)
    
    await message.answer(text=support_text, reply_markup=builder.as_markup())


# Kanal tugmasi handler
@router.message(F.text == "📢 Kanal")
async def channel_handler(message: Message):
    """Kanal haqida ma'lumot"""
    
    channel_text = """
📢 <b>DAROMATX rasmiy kanali</b>

Kanalimizga obuna bo'ling va:
• 🎁 Maxsus chegirmalardan xabardor bo'ling
• 📚 Bepul darslarni oling
• 💡 Foydali ma'lumotlarni bilib turing
• 🔔 Yangi kurslardan birinchi bo'lib xabar toping
"""
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Kanalga obuna bo'lish", url="https://t.me/daromatx")
    builder.button(text="📣 Instagram", url="https://instagram.com/daromatx")
    builder.button(text="🎬 YouTube", url="https://youtube.com/@daromatx")
    builder.adjust(1)
    
    await message.answer(text=channel_text, reply_markup=builder.as_markup())


# FAQ callback
@router.callback_query(F.data == "faq")
async def faq_callback(callback: CallbackQuery):
    """Ko'p so'raladigan savollar"""
    
    faq_text = """
❓ <b>Ko'p so'raladigan savollar</b>

<b>1. To'lov qanday amalga oshiriladi?</b>
Kursni tanlang → To'lov usulini tanlang (Stars, Click, Payme, TON) → To'lovni tasdiqlang.

<b>2. Kurslarni qanday ko'raman?</b>
"Mening kurslarim" bo'limiga o'ting → Kursni tanlang → Darslarni ko'ring.

<b>3. Sertifikat qachon beriladi?</b>
Kursni 100% tugatganingizda sertifikat avtomatik beriladi.

<b>4. Pulni qaytarib olsam bo'ladimi?</b>
Kursning 20% dan ko'prog'ini ko'rmagan bo'lsangiz, 3 kun ichida pulni qaytaramiz.

<b>5. Darslar qancha vaqt ochiq turadi?</b>
Bir marta sotib olgan kurslaringiz umrbod sizniki!
"""
    
    await callback.message.edit_text(text=faq_text)
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam komandasi"""
    
    help_text = """
📖 <b>Yordam</b>

<b>🔹 Asosiy komandalar:</b>
/start - Botni qayta ishga tushirish
/help - Yordam

<b>🔹 Tugmalar:</b>
📚 Kurslarni ko'rish - Barcha kurslar
🎓 Mening kurslarim - Sotib olingan kurslar
👤 Profil - Shaxsiy kabinet
💬 Qo'llab-quvvatlash - Yordam olish
📢 Kanal - Rasmiy kanal

<b>❓ Savol bo'lsa:</b> @daromatx_admin
"""
    
    await message.answer(help_text)
