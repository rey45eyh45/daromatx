from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database.repositories import CourseRepository, UserRepository, LessonRepository
from keyboards.main_kb import get_mini_app_keyboard

router = Router()


class AddCourseStates(StatesGroup):
    """Kurs qo'shish holatlari"""
    title = State()
    description = State()
    price = State()
    stars_price = State()
    thumbnail = State()
    category = State()


class AddLessonStates(StatesGroup):
    """Dars qo'shish holatlari"""
    course_id = State()
    title = State()
    description = State()
    video_file_id = State()
    order = State()


def is_admin(user_id: int) -> bool:
    """Admin tekshirish"""
    return user_id in config.admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    user_repo = UserRepository()
    course_repo = CourseRepository()
    
    users_count = await user_repo.get_users_count()
    courses_count = await course_repo.get_courses_count()
    
    text = f"""
🔐 <b>Admin Panel</b>

📊 <b>Statistika:</b>
👥 Foydalanuvchilar: {users_count}
📚 Kurslar: {courses_count}

⚙️ <b>Boshqaruv:</b>
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Kurs qo'shish", callback_data="admin_add_course")
    builder.button(text="📚 Kurslarni boshqarish", callback_data="admin_courses")
    builder.button(text="➕ Dars qo'shish", callback_data="admin_add_lesson")
    builder.button(text="👥 Foydalanuvchilar", callback_data="admin_users")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.button(text="📢 Xabar yuborish", callback_data="admin_broadcast")
    builder.adjust(2)
    
    await message.answer(text=text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "admin_add_course")
async def admin_add_course(callback: CallbackQuery, state: FSMContext):
    """Kurs qo'shish boshlash"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📚 <b>Yangi kurs qo'shish</b>\n\n"
        "Kurs nomini kiriting:"
    )
    await state.set_state(AddCourseStates.title)
    await callback.answer()


@router.message(AddCourseStates.title)
async def process_course_title(message: Message, state: FSMContext):
    """Kurs nomi"""
    await state.update_data(title=message.text)
    await message.answer("📝 Kurs tavsifini kiriting:")
    await state.set_state(AddCourseStates.description)


@router.message(AddCourseStates.description)
async def process_course_description(message: Message, state: FSMContext):
    """Kurs tavsifi"""
    await state.update_data(description=message.text)
    await message.answer("💰 Kurs narxini kiriting (so'mda):")
    await state.set_state(AddCourseStates.price)


@router.message(AddCourseStates.price)
async def process_course_price(message: Message, state: FSMContext):
    """Kurs narxi"""
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        await state.update_data(price=price)
        await message.answer("⭐ Telegram Stars narxini kiriting:")
        await state.set_state(AddCourseStates.stars_price)
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:")


@router.message(AddCourseStates.stars_price)
async def process_course_stars_price(message: Message, state: FSMContext):
    """Stars narxi"""
    try:
        stars_price = int(message.text)
        await state.update_data(stars_price=stars_price)
        await message.answer("🖼 Kurs rasmini yuboring (yoki 'skip' yozing):")
        await state.set_state(AddCourseStates.thumbnail)
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:")


@router.message(AddCourseStates.thumbnail)
async def process_course_thumbnail(message: Message, state: FSMContext):
    """Kurs rasmi"""
    
    if message.text and message.text.lower() == "skip":
        thumbnail = None
    elif message.photo:
        thumbnail = message.photo[-1].file_id
    else:
        thumbnail = None
    
    await state.update_data(thumbnail=thumbnail)
    
    builder = InlineKeyboardBuilder()
    categories = ["Dasturlash", "Dizayn", "Marketing", "Biznes", "Tillar", "Boshqa"]
    for cat in categories:
        builder.button(text=cat, callback_data=f"cat_{cat}")
    builder.adjust(2)
    
    await message.answer(
        "📂 Kategoriyani tanlang:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddCourseStates.category)


@router.callback_query(F.data.startswith("cat_"), AddCourseStates.category)
async def process_course_category(callback: CallbackQuery, state: FSMContext):
    """Kategoriya tanlash va kursni saqlash"""
    
    category = callback.data.replace("cat_", "")
    data = await state.get_data()
    
    course_repo = CourseRepository()
    course = await course_repo.create_course(
        title=data["title"],
        description=data["description"],
        price=data["price"],
        stars_price=data["stars_price"],
        thumbnail=data.get("thumbnail"),
        category=category,
        author_id=callback.from_user.id
    )
    
    await callback.message.edit_text(
        f"✅ <b>Kurs muvaffaqiyatli qo'shildi!</b>\n\n"
        f"📚 Nomi: {course.title}\n"
        f"💰 Narxi: {course.price:,} so'm\n"
        f"⭐ Stars: {course.stars_price}\n"
        f"📂 Kategoriya: {category}\n\n"
        f"Endi darslarni qo'shishingiz mumkin."
    )
    
    await state.clear()
    await callback.answer("✅ Kurs qo'shildi!")


@router.callback_query(F.data == "admin_add_lesson")
async def admin_add_lesson(callback: CallbackQuery, state: FSMContext):
    """Dars qo'shish"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_repo = CourseRepository()
    courses = await course_repo.get_all_courses()
    
    if not courses:
        await callback.answer("❌ Avval kurs qo'shing!", show_alert=True)
        return
    
    builder = InlineKeyboardBuilder()
    for course in courses:
        builder.button(text=course.title, callback_data=f"lesson_course_{course.id}")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "📚 Qaysi kursga dars qo'shmoqchisiz?",
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddLessonStates.course_id)
    await callback.answer()


@router.callback_query(F.data.startswith("lesson_course_"), AddLessonStates.course_id)
async def select_course_for_lesson(callback: CallbackQuery, state: FSMContext):
    """Kursni tanlash"""
    
    course_id = int(callback.data.replace("lesson_course_", ""))
    await state.update_data(course_id=course_id)
    
    await callback.message.edit_text("📝 Dars nomini kiriting:")
    await state.set_state(AddLessonStates.title)
    await callback.answer()


@router.message(AddLessonStates.title)
async def process_lesson_title(message: Message, state: FSMContext):
    """Dars nomi"""
    await state.update_data(title=message.text)
    await message.answer("📄 Dars tavsifini kiriting:")
    await state.set_state(AddLessonStates.description)


@router.message(AddLessonStates.description)
async def process_lesson_description(message: Message, state: FSMContext):
    """Dars tavsifi"""
    await state.update_data(description=message.text)
    await message.answer("🎥 Video faylni yuboring:")
    await state.set_state(AddLessonStates.video_file_id)


@router.message(AddLessonStates.video_file_id, F.video)
async def process_lesson_video(message: Message, state: FSMContext):
    """Video fayl"""
    
    video_file_id = message.video.file_id
    data = await state.get_data()
    
    lesson_repo = LessonRepository()
    lesson = await lesson_repo.create_lesson(
        course_id=data["course_id"],
        title=data["title"],
        description=data["description"],
        video_file_id=video_file_id,
        duration=message.video.duration
    )
    
    await message.answer(
        f"✅ <b>Dars muvaffaqiyatli qo'shildi!</b>\n\n"
        f"📝 Nomi: {lesson.title}\n"
        f"⏱ Davomiyligi: {lesson.duration // 60} daqiqa"
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Statistika"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    user_repo = UserRepository()
    course_repo = CourseRepository()
    
    users_count = await user_repo.get_users_count()
    courses_count = await course_repo.get_courses_count()
    today_users = await user_repo.get_today_users_count()
    
    text = f"""
📊 <b>Statistika</b>

👥 <b>Foydalanuvchilar:</b>
├ Jami: {users_count}
└ Bugun: {today_users}

📚 <b>Kurslar:</b>
└ Jami: {courses_count}
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_courses")
async def admin_courses(callback: CallbackQuery):
    """Kurslar ro'yxati"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_repo = CourseRepository()
    courses = await course_repo.get_all_courses()
    
    if not courses:
        await callback.answer("❌ Hali kurslar yo'q!", show_alert=True)
        return
    
    builder = InlineKeyboardBuilder()
    for course in courses:
        status = "✅" if course.is_active else "❌"
        builder.button(
            text=f"{status} {course.title}", 
            callback_data=f"admin_course_{course.id}"
        )
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "📚 <b>Kurslar ro'yxati</b>\n\n"
        "Boshqarish uchun kursni tanlang:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_course_"))
async def admin_course_detail(callback: CallbackQuery):
    """Kurs tafsilotlari"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_id = int(callback.data.replace("admin_course_", ""))
    course_repo = CourseRepository()
    lesson_repo = LessonRepository()
    
    course = await course_repo.get_course_by_id(course_id)
    if not course:
        await callback.answer("❌ Kurs topilmadi!", show_alert=True)
        return
    
    lessons = await lesson_repo.get_lessons_by_course(course_id)
    lessons_count = len(lessons) if lessons else 0
    
    status = "✅ Faol" if course.is_active else "❌ Nofaol"
    
    text = f"""
📚 <b>{course.title}</b>

📝 {course.description[:200]}...

💰 Narxi: {course.price:,} so'm
⭐ Stars: {course.stars_price}
📂 Kategoriya: {course.category or 'Belgilanmagan'}
🎬 Darslar: {lessons_count} ta
📊 Holat: {status}
"""
    
    builder = InlineKeyboardBuilder()
    
    if course.is_active:
        builder.button(text="❌ Nofaol qilish", callback_data=f"course_deactivate_{course_id}")
    else:
        builder.button(text="✅ Faol qilish", callback_data=f"course_activate_{course_id}")
    
    builder.button(text="🎬 Darslar", callback_data=f"course_lessons_{course_id}")
    builder.button(text="🗑 O'chirish", callback_data=f"course_delete_{course_id}")
    builder.button(text="🔙 Orqaga", callback_data="admin_courses")
    builder.adjust(2)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("course_activate_"))
async def course_activate(callback: CallbackQuery):
    """Kursni faollashtirish"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_id = int(callback.data.replace("course_activate_", ""))
    course_repo = CourseRepository()
    
    await course_repo.update_course(course_id, is_active=True)
    await callback.answer("✅ Kurs faollashtirildi!")
    
    # Refresh page
    callback.data = f"admin_course_{course_id}"
    await admin_course_detail(callback)


@router.callback_query(F.data.startswith("course_deactivate_"))
async def course_deactivate(callback: CallbackQuery):
    """Kursni nofaol qilish"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_id = int(callback.data.replace("course_deactivate_", ""))
    course_repo = CourseRepository()
    
    await course_repo.update_course(course_id, is_active=False)
    await callback.answer("❌ Kurs nofaol qilindi!")
    
    # Refresh page
    callback.data = f"admin_course_{course_id}"
    await admin_course_detail(callback)


@router.callback_query(F.data.startswith("course_delete_"))
async def course_delete_confirm(callback: CallbackQuery):
    """Kursni o'chirish tasdiqlash"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_id = int(callback.data.replace("course_delete_", ""))
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"course_delete_confirm_{course_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"admin_course_{course_id}")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "⚠️ <b>Diqqat!</b>\n\n"
        "Rostdan ham bu kursni o'chirmoqchimisiz?\n"
        "Bu amalni ortga qaytarib bo'lmaydi!",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("course_delete_confirm_"))
async def course_delete(callback: CallbackQuery):
    """Kursni o'chirish"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_id = int(callback.data.replace("course_delete_confirm_", ""))
    course_repo = CourseRepository()
    
    await course_repo.delete_course(course_id)
    await callback.answer("🗑 Kurs o'chirildi!")
    
    # Go back to courses list
    callback.data = "admin_courses"
    await admin_courses(callback)


@router.callback_query(F.data.startswith("course_lessons_"))
async def course_lessons(callback: CallbackQuery):
    """Kurs darslari"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    course_id = int(callback.data.replace("course_lessons_", ""))
    lesson_repo = LessonRepository()
    course_repo = CourseRepository()
    
    course = await course_repo.get_course_by_id(course_id)
    lessons = await lesson_repo.get_lessons_by_course(course_id)
    
    if not lessons:
        builder = InlineKeyboardBuilder()
        builder.button(text="➕ Dars qo'shish", callback_data="admin_add_lesson")
        builder.button(text="🔙 Orqaga", callback_data=f"admin_course_{course_id}")
        builder.adjust(1)
        
        await callback.message.edit_text(
            f"🎬 <b>{course.title}</b> - Darslar\n\n"
            "❌ Hali darslar yo'q",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return
    
    text = f"🎬 <b>{course.title}</b> - Darslar\n\n"
    
    for i, lesson in enumerate(lessons, 1):
        duration = f"{lesson.duration // 60}:{lesson.duration % 60:02d}" if lesson.duration else "0:00"
        text += f"{i}. {lesson.title} ({duration})\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Dars qo'shish", callback_data="admin_add_lesson")
    builder.button(text="🔙 Orqaga", callback_data=f"admin_course_{course_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Foydalanuvchilar ro'yxati"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    user_repo = UserRepository()
    users = await user_repo.get_all_users(limit=20)
    
    if not users:
        await callback.answer("❌ Hali foydalanuvchilar yo'q!", show_alert=True)
        return
    
    text = "👥 <b>Foydalanuvchilar</b> (oxirgi 20 ta)\n\n"
    
    for i, user in enumerate(users, 1):
        name = user.full_name or user.username or f"User {user.telegram_id}"
        text += f"{i}. {name}\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


class BroadcastStates(StatesGroup):
    """Xabar yuborish holatlari"""
    message = State()
    confirm = State()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Xabar yuborish boshlash"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="admin_back")
    
    await callback.message.edit_text(
        "📢 <b>Ommaviy xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:\n\n"
        "<i>Rasm, video yoki matn yuborishingiz mumkin</i>",
        reply_markup=builder.as_markup()
    )
    await state.set_state(BroadcastStates.message)
    await callback.answer()


@router.message(BroadcastStates.message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Xabarni saqlash"""
    
    if not is_admin(message.from_user.id):
        return
    
    # Save message data
    message_data = {
        "text": message.text or message.caption,
        "photo": message.photo[-1].file_id if message.photo else None,
        "video": message.video.file_id if message.video else None,
    }
    
    await state.update_data(message_data=message_data)
    
    user_repo = UserRepository()
    users_count = await user_repo.get_users_count()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yuborish", callback_data="broadcast_confirm")
    builder.button(text="❌ Bekor qilish", callback_data="admin_back")
    builder.adjust(2)
    
    await message.answer(
        f"📢 <b>Xabarni tasdiqlang</b>\n\n"
        f"👥 {users_count} ta foydalanuvchiga yuboriladi.\n\n"
        f"Davom etasizmi?",
        reply_markup=builder.as_markup()
    )
    await state.set_state(BroadcastStates.confirm)


@router.callback_query(F.data == "broadcast_confirm", BroadcastStates.confirm)
async def broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    """Xabarni yuborish"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    data = await state.get_data()
    message_data = data.get("message_data", {})
    
    user_repo = UserRepository()
    users = await user_repo.get_all_users(limit=10000)
    
    await callback.message.edit_text("📤 Xabar yuborilmoqda...")
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            if message_data.get("photo"):
                await callback.bot.send_photo(
                    user.telegram_id,
                    photo=message_data["photo"],
                    caption=message_data.get("text")
                )
            elif message_data.get("video"):
                await callback.bot.send_video(
                    user.telegram_id,
                    video=message_data["video"],
                    caption=message_data.get("text")
                )
            else:
                await callback.bot.send_message(
                    user.telegram_id,
                    text=message_data.get("text", "")
                )
            success += 1
        except Exception:
            failed += 1
    
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Admin panel", callback_data="admin_back")
    
    await callback.message.edit_text(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"📤 Muvaffaqiyatli: {success}\n"
        f"❌ Xatolik: {failed}",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    """Admin panelga qaytish"""
    
    await state.clear()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    user_repo = UserRepository()
    course_repo = CourseRepository()
    
    users_count = await user_repo.get_users_count()
    courses_count = await course_repo.get_courses_count()
    
    text = f"""
🔐 <b>Admin Panel</b>

📊 <b>Statistika:</b>
👥 Foydalanuvchilar: {users_count}
📚 Kurslar: {courses_count}

⚙️ <b>Boshqaruv:</b>
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Kurs qo'shish", callback_data="admin_add_course")
    builder.button(text="📚 Kurslarni boshqarish", callback_data="admin_courses")
    builder.button(text="➕ Dars qo'shish", callback_data="admin_add_lesson")
    builder.button(text="👥 Foydalanuvchilar", callback_data="admin_users")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.button(text="📢 Xabar yuborish", callback_data="admin_broadcast")
    builder.adjust(2)
    
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()
