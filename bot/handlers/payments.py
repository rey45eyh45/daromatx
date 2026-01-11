from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database.repositories import CourseRepository, PaymentRepository, UserRepository

router = Router()


# ============ TELEGRAM STARS TO'LOVI ============

@router.callback_query(F.data.startswith("buy_stars_"))
async def buy_with_stars(callback: CallbackQuery, bot: Bot):
    """Telegram Stars bilan sotib olish"""
    
    course_id = int(callback.data.replace("buy_stars_", ""))
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    if not course:
        await callback.answer("❌ Kurs topilmadi!", show_alert=True)
        return
    
    # Telegram Stars invoice yuborish
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=course.title,
        description=course.description[:255],
        payload=f"course_{course_id}",
        provider_token="",  # Stars uchun bo'sh
        currency="XTR",  # Telegram Stars valyutasi
        prices=[LabeledPrice(label=course.title, amount=course.stars_price)],
        start_parameter=f"course_{course_id}"
    )
    
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """To'lovni tasdiqlash"""
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Muvaffaqiyatli to'lov"""
    
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload
    
    if payload.startswith("course_"):
        course_id = int(payload.replace("course_", ""))
        
        # To'lovni saqlash
        payment_repo = PaymentRepository()
        await payment_repo.create_payment(
            user_telegram_id=message.from_user.id,
            course_id=course_id,
            amount=payment_info.total_amount,
            currency=payment_info.currency,
            payment_type="telegram_stars",
            status="completed",
            transaction_id=payment_info.telegram_payment_charge_id
        )
        
        # Kursni foydalanuvchiga biriktirish
        user_repo = UserRepository()
        await user_repo.add_purchased_course(
            telegram_id=message.from_user.id,
            course_id=course_id
        )
        
        course_repo = CourseRepository()
        course = await course_repo.get_course_by_id(course_id)
        
        # Mini App tugmasi bilan javob
        builder = InlineKeyboardBuilder()
        builder.button(
            text="📚 Kursni ko'rish",
            web_app=WebAppInfo(url=f"{config.mini_app_url}/courses/{course_id}")
        )
        builder.button(
            text="📖 Barcha kurslarim",
            web_app=WebAppInfo(url=f"{config.mini_app_url}/my-courses")
        )
        builder.adjust(1)
        
        await message.answer(
            f"🎉 <b>Tabriklaymiz!</b>\n\n"
            f"Siz «{course.title}» kursini muvaffaqiyatli sotib oldingiz!\n\n"
            f"📚 Quyidagi tugmani bosib kursni ko'rishingiz mumkin:",
            reply_markup=builder.as_markup()
        )


# ============ CLICK/PAYME TO'LOVI ============

@router.callback_query(F.data.startswith("buy_"))
async def buy_course(callback: CallbackQuery):
    """Kursni sotib olish - to'lov usulini tanlash"""
    
    # Stars bilan to'lovni o'tkazib yuborish
    if "stars" in callback.data:
        return
    
    course_id = int(callback.data.replace("buy_", ""))
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    if not course:
        await callback.answer("❌ Kurs topilmadi!", show_alert=True)
        return
    
    text = f"""
💳 <b>To'lov usulini tanlang</b>

📚 Kurs: {course.title}
💰 Narx: {course.price:,} so'm

Quyidagi usullardan birini tanlang:
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Telegram Stars", callback_data=f"buy_stars_{course_id}")
    builder.button(text="💳 Click", callback_data=f"pay_click_{course_id}")
    builder.button(text="💳 Payme", callback_data=f"pay_payme_{course_id}")
    builder.button(text="💎 TON Crypto", callback_data=f"pay_ton_{course_id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"course_{course_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("pay_click_"))
async def pay_with_click(callback: CallbackQuery):
    """Click orqali to'lov"""
    
    course_id = int(callback.data.replace("pay_click_", ""))
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    # Click to'lov havolasini yaratish
    # Bu yerda Click API integratsiyasi bo'ladi
    
    payment_repo = PaymentRepository()
    payment = await payment_repo.create_payment(
        user_telegram_id=callback.from_user.id,
        course_id=course_id,
        amount=course.price,
        currency="UZS",
        payment_type="click",
        status="pending"
    )
    
    # Click to'lov havolasi
    click_url = f"https://my.click.uz/services/pay?service_id=YOUR_SERVICE&merchant_id=YOUR_MERCHANT&amount={course.price}&transaction_param={payment.id}"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Click orqali to'lash", url=click_url)
    builder.button(text="✅ To'ladim", callback_data=f"check_payment_{payment.id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"buy_{course_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"💳 <b>Click orqali to'lov</b>\n\n"
        f"📚 Kurs: {course.title}\n"
        f"💰 Summa: {course.price:,} so'm\n\n"
        f"Quyidagi tugmani bosib to'lovni amalga oshiring:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_payme_"))
async def pay_with_payme(callback: CallbackQuery):
    """Payme orqali to'lov"""
    
    course_id = int(callback.data.replace("pay_payme_", ""))
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    payment_repo = PaymentRepository()
    payment = await payment_repo.create_payment(
        user_telegram_id=callback.from_user.id,
        course_id=course_id,
        amount=course.price,
        currency="UZS",
        payment_type="payme",
        status="pending"
    )
    
    # Payme to'lov havolasi
    import base64
    payme_data = f"m=YOUR_MERCHANT_ID;ac.order_id={payment.id};a={course.price * 100}"
    payme_url = f"https://checkout.paycom.uz/{base64.b64encode(payme_data.encode()).decode()}"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Payme orqali to'lash", url=payme_url)
    builder.button(text="✅ To'ladim", callback_data=f"check_payment_{payment.id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"buy_{course_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"💳 <b>Payme orqali to'lov</b>\n\n"
        f"📚 Kurs: {course.title}\n"
        f"💰 Summa: {course.price:,} so'm\n\n"
        f"Quyidagi tugmani bosib to'lovni amalga oshiring:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_ton_"))
async def pay_with_ton(callback: CallbackQuery):
    """TON Crypto orqali to'lov"""
    
    course_id = int(callback.data.replace("pay_ton_", ""))
    
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(course_id)
    
    # TON narxini hisoblash (taxminiy)
    ton_price = course.price / 50000  # 1 TON ≈ 50,000 so'm
    
    payment_repo = PaymentRepository()
    payment = await payment_repo.create_payment(
        user_telegram_id=callback.from_user.id,
        course_id=course_id,
        amount=course.price,
        currency="TON",
        payment_type="ton",
        status="pending"
    )
    
    ton_wallet = "UQD7hkW5-rC8EHHZAmMAnzhddHxexDQKx26ttycUq8hLKVSu"  # TON wallet manzili
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Tonkeeper", url=f"ton://transfer/{ton_wallet}?amount={int(ton_price * 1e9)}&text=course_{payment.id}")
    builder.button(text="✅ To'ladim", callback_data=f"check_payment_{payment.id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"buy_{course_id}")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"💎 <b>TON Crypto orqali to'lov</b>\n\n"
        f"📚 Kurs: {course.title}\n"
        f"💰 Summa: {ton_price:.2f} TON\n\n"
        f"💼 Wallet: <code>{ton_wallet}</code>\n\n"
        f"Comment: <code>course_{payment.id}</code>\n\n"
        f"Quyidagi tugmani bosib to'lovni amalga oshiring:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: CallbackQuery):
    """To'lovni tekshirish"""
    
    payment_id = int(callback.data.replace("check_payment_", ""))
    
    payment_repo = PaymentRepository()
    payment = await payment_repo.get_payment_by_id(payment_id)
    
    if not payment:
        await callback.answer("❌ To'lov topilmadi!", show_alert=True)
        return
    
    if payment.status == "completed":
        await callback.answer("✅ To'lov allaqachon tasdiqlangan!", show_alert=True)
        return
    
    # Bu yerda to'lov tizimidan tekshirish bo'ladi
    # Hozircha admin tasdiqlashi kerak
    
    await callback.answer(
        "⏳ To'lov tekshirilmoqda...\n"
        "Admin tasdiqlashini kuting.",
        show_alert=True
    )
