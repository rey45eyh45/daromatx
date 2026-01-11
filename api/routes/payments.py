from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import os

from database.repositories import PaymentRepository, CourseRepository

router = APIRouter()

BOT_USERNAME = os.getenv("BOT_USERNAME", "daromatx_bot")


class CreatePaymentRequest(BaseModel):
    course_id: int
    payment_type: str  # stars, click, payme, ton


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
