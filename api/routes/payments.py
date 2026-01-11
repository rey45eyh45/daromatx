from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import os
import httpx

from database.repositories import PaymentRepository, CourseRepository, UserRepository

router = APIRouter()

BOT_USERNAME = os.getenv("BOT_USERNAME", "daromatx_bot")
TON_WALLET = os.getenv("TON_WALLET_ADDRESS", "")


class CreatePaymentRequest(BaseModel):
    course_id: int
    payment_type: str  # stars, click, payme, ton


class TonVerifyRequest(BaseModel):
    course_id: int
    

class PaymentResponse(BaseModel):
    id: int
    course_id: int
    amount: float
    currency: str
    payment_type: str
    status: str
    payment_url: Optional[str] = None
    invoice_url: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """To'lov yaratish"""
    
    import json
    from urllib.parse import unquote
    
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    # Kursni topish
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(request.course_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    
    # To'lovni yaratish
    payment_repo = PaymentRepository()
    payment = await payment_repo.create_payment(
        user_telegram_id=telegram_id,
        course_id=request.course_id,
        amount=course.price if request.payment_type != "stars" else course.stars_price,
        currency="XTR" if request.payment_type == "stars" else "UZS",
        payment_type=request.payment_type,
        status="pending"
    )
    
    # To'lov URL yaratish
    payment_url = None
    invoice_url = None
    
    if request.payment_type == "stars":
        # Telegram Stars - bot orqali invoice
        invoice_url = f"https://t.me/{BOT_USERNAME}?start=buy_{request.course_id}"
        payment_url = invoice_url
    elif request.payment_type == "click":
        payment_url = f"https://my.click.uz/services/pay?service_id=YOUR_SERVICE&amount={int(course.price)}&transaction_param={payment.id}"
    elif request.payment_type == "payme":
        import base64
        payme_data = f"m=YOUR_MERCHANT;ac.order_id={payment.id};a={int(course.price * 100)}"
        payment_url = f"https://checkout.paycom.uz/{base64.b64encode(payme_data.encode()).decode()}"
    elif request.payment_type == "ton":
        ton_price = course.price / 50000
        payment_url = f"ton://transfer/YOUR_WALLET?amount={int(ton_price * 1e9)}&text=course_{payment.id}"
    
    return PaymentResponse(
        id=payment.id,
        course_id=payment.course_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_type=payment.payment_type,
        status=payment.status,
        payment_url=payment_url,
        invoice_url=invoice_url
    )


@router.post("/ton/verify")
async def verify_ton_payment(
    request: TonVerifyRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """TON to'lovni tekshirish"""
    import json
    from urllib.parse import unquote
    from datetime import datetime, timedelta
    
    # Telegram user ma'lumotlarini olish
    try:
        data_parts = dict(x.split('=') for x in x_telegram_init_data.split('&'))
        user_data = json.loads(unquote(data_parts.get('user', '{}')))
        telegram_id = user_data.get('id')
    except:
        raise HTTPException(status_code=400, detail="Invalid init data format")
    
    if not TON_WALLET:
        raise HTTPException(status_code=500, detail="TON wallet manzili sozlanmagan")
    
    # Kursni topish
    course_repo = CourseRepository()
    course = await course_repo.get_course_by_id(request.course_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    
    # TON narxini hisoblash (1 TON = 50000 so'm taxminan)
    ton_rate = 50000
    expected_ton = course.price / ton_rate
    expected_nano = int(expected_ton * 1e9)  # nanoton
    
    # TON Center API orqali tranzaksiyalarni tekshirish
    try:
        async with httpx.AsyncClient() as client:
            # Oxirgi 10 ta tranzaksiyani olish
            response = await client.get(
                f"https://toncenter.com/api/v2/getTransactions",
                params={
                    "address": TON_WALLET,
                    "limit": 20,
                    "archival": "false"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="TON API xatosi")
            
            data = response.json()
            
            if not data.get("ok"):
                raise HTTPException(status_code=500, detail="TON tranzaksiyalarni olishda xato")
            
            transactions = data.get("result", [])
            
            # Comment formatini tekshirish: "course_ID" yoki "COURSE_ID_TELEGRAMID"
            expected_comments = [
                f"course_{request.course_id}",
                f"course_{request.course_id}_{telegram_id}",
                f"{request.course_id}",
            ]
            
            # 24 soat ichidagi tranzaksiyalarni tekshirish
            now = datetime.utcnow()
            
            for tx in transactions:
                try:
                    # Vaqtni tekshirish (24 soat ichida bo'lishi kerak)
                    tx_time = datetime.fromtimestamp(tx.get("utime", 0))
                    if now - tx_time > timedelta(hours=24):
                        continue
                    
                    # Kiruvchi tranzaksiya bo'lishi kerak
                    in_msg = tx.get("in_msg", {})
                    if not in_msg:
                        continue
                    
                    # Summani tekshirish
                    value = int(in_msg.get("value", 0))
                    
                    # Kamida 90% to'langan bo'lishi kerak (komissiya uchun)
                    if value < expected_nano * 0.9:
                        continue
                    
                    # Commentni tekshirish
                    comment = in_msg.get("message", "")
                    
                    if any(exp.lower() in comment.lower() for exp in expected_comments):
                        # To'lov topildi! Kursni ochish
                        user_repo = UserRepository()
                        user = await user_repo.get_user_by_telegram_id(telegram_id)
                        
                        if not user:
                            # Foydalanuvchi yaratish
                            user = await user_repo.create_or_update_user(
                                telegram_id=telegram_id,
                                username=user_data.get("username"),
                                full_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                            )
                        
                        # Kurs allaqachon sotib olinganmi tekshirish
                        purchased_course_ids = [uc.course_id for uc in (user.purchased_courses or [])]
                        if request.course_id in purchased_course_ids:
                            return {
                                "success": True,
                                "message": "Kurs allaqachon sotib olingan",
                                "already_purchased": True
                            }
                        
                        # Kursni qo'shish
                        await user_repo.add_purchased_course(telegram_id, request.course_id)
                        
                        # To'lovni saqlash
                        payment_repo = PaymentRepository()
                        await payment_repo.create_payment(
                            user_telegram_id=telegram_id,
                            course_id=request.course_id,
                            amount=expected_ton,
                            currency="TON",
                            payment_type="ton",
                            status="completed",
                            transaction_id=tx.get("transaction_id", {}).get("hash", "")
                        )
                        
                        return {
                            "success": True,
                            "message": "To'lov tasdiqlandi! Kurs ochildi.",
                            "course_id": request.course_id
                        }
                        
                except Exception as e:
                    print(f"Transaction parse error: {e}")
                    continue
            
            # To'lov topilmadi
            return {
                "success": False,
                "message": f"To'lov topilmadi. {expected_ton:.2f} TON yuboring va comment qismiga 'course_{request.course_id}' yozing.",
                "expected_amount": expected_ton,
                "wallet": TON_WALLET
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"TON API bilan bog'lanishda xato: {str(e)}")


@router.get("/ton/info")
async def get_ton_info():
    """TON to'lov ma'lumotlari"""
    return {
        "wallet": TON_WALLET,
        "rate": 50000,  # 1 TON = 50000 so'm
        "currency": "TON"
    }


@router.get("/{payment_id}/status")
async def check_payment_status(payment_id: int):
    """To'lov statusini tekshirish"""
    
    payment_repo = PaymentRepository()
    payment = await payment_repo.get_payment_by_id(payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")
    
    return {
        "id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "currency": payment.currency
    }
