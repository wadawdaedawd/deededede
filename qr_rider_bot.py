from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram.filters import Command
import qrcode
import cv2
import numpy as np
import asyncio

API_TOKEN = '7707061253:AAG3sRf5ATO2zDF8ZYBllfpdPSM0iPoqgzY'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_qr = State()

router = Router()

@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer("Отправьте мне изображение QR-кода, чтобы получить информацию из него.")

@router.message(F.photo)
async def handle_photo(message: types.Message):
    await dp.storage.set_state(message.from_user.id, Form.waiting_for_qr)
    await message.answer("Обрабатываю ваш QR-код...")

    photo = await bot.download(message.photo[-1].file_id)
    photo_bytes = photo.read()
    nparr = np.frombuffer(photo_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    qr_data = decode_qr_code(img)
    
    if qr_data:
        await message.answer(f"Данные QR-кода: {qr_data}")
    else:
        await message.answer("Не удалось распознать QR-код.")

@router.message(Form.waiting_for_qr)
async def process_invalid_input(message: types.Message):
    await message.answer("Пожалуйста, отправьте корректное изображение QR-кода.")

def decode_qr_code(img):
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    return data if data else None

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
