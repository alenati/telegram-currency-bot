from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from aiogram.types import LabeledPrice

router_donate = Router()

@router_donate.message(Command("donate"))
async def donate (message: types.Message):

    keyboard_donate = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="10")],
        [KeyboardButton(text="50")],
        [KeyboardButton(text="100")]],
    resize_keyboard = True,
    one_time_keyboard = True
    )
    await message.answer("Выбери количество здезд, которые ты хочешь отправить:",reply_markup=keyboard_donate)

        
@router_donate.pre_checkout_query()
async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router_donate.message(F.successful_payment)
async def success(message: types.Message):
    payload = message.successful_payment.invoice_payload

    if payload == "donation":
        await message.answer("Спасибо!")


@router_donate.message(F.text.in_(["10", "50", "100"]))
async def donate_amount(message: types.Message):
    amount = int(message.text)
    await message.answer_invoice(
                title="Благодарность автору",
                description = "Донат добровольный, не открывает доступ ни к каким функциям, не дает приемуществ, не влияет на работу бота.",
                payload = f"donation{amount}{message.from_user.id}",
                provider_token ="",
                currency="XTR",
                prices= [LabeledPrice(label="ДОНАТ", amount=amount)
            ],
            start_parameter=f"donate{amount}")
    
