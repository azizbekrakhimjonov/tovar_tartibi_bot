from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import token
import re

bot = Bot(token=token)
dp = Dispatcher(bot)

# Tugmalar
back_button = KeyboardButton("Orqaga qaytish")
start_button = KeyboardButton("Jismoniy shaxslar tomonidan bojxona chegarasi orqali tovarlarni olib o‘tish tartibi")
custom_button = KeyboardButton("Bojxona to’lovlarini hisoblash")
contact_button = KeyboardButton("Mutaxassis bilan bog’lanish")

start_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(start_button, custom_button, contact_button)
back_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(back_button)

general_rules_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("O‘zbekiston Respublikasi Prezidentining Qarori, 06.02.2018 yildagi PQ-3512-son"),
    KeyboardButton("O‘zbekiston Respublikasi Prezidentining qarori, 07.11.2019 yildagi PQ-4508-son"),
    KeyboardButton("O‘zbekiston Respublikasi Vazirlar Mahkamasining qarori, 22.06.2018 yildagi 463-son"),
    KeyboardButton("O‘zbekiston Respublikasi Vazirlar Mahkamasining qarori, 12.05.2020 yildagi 281-son"),
    back_button
)

border_point_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("avtoyo‘l (piyoda)"),
    KeyboardButton("xalqaro aeroport"),
    KeyboardButton("temir yo‘l va daryo"),
    back_button
)

user_data = {}

# START komandasi
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Bojxona to'lovlari va tovarlarni olib o'tish tartibi haqida ma'lumot olish uchun quyidagi tugmalardan birini tanlang.",
        reply_markup=start_markup
    )

# Jismoniy shaxslar uchun tartiblar
@dp.message_handler(lambda message: message.text.strip().lower() == start_button.text.lower())
async def send_rules(message: types.Message):
    await message.answer("Tovarlarni olib o'tish bo'yicha qoidalarni tanlang:", reply_markup=general_rules_markup)

# Umumiy qoidalar
@dp.message_handler(lambda message: message.text in [
    "O‘zbekiston Respublikasi Prezidentining Qarori, 06.02.2018 yildagi PQ-3512-son",
    "O‘zbekiston Respublikasi Prezidentining qarori, 07.11.2019 yildagi PQ-4508-son",
    "O‘zbekiston Respublikasi Vazirlar Mahkamasining qarori, 22.06.2018 yildagi 463-son",
    "O‘zbekiston Respublikasi Vazirlar Mahkamasining qarori, 12.05.2020 yildagi 281-son"])
async def link_to_decision(message: types.Message):
    await message.answer(
        "Sizning so'rovingiz bo'yicha quyidagi havolani topishingiz mumkin: [Qaror](https://www.lex.uz/uz/)",
        parse_mode="Markdown",
        reply_markup=back_markup
    )

# Bojxona to'lovlarini hisoblash
@dp.message_handler(lambda message: message.text == custom_button.text)
async def calculate_customs_fee(message: types.Message):
    await message.answer("Chegara o`tkazish punktini tanlang:", reply_markup=border_point_markup)

@dp.message_handler(lambda message: message.text in ["avtoyo‘l (piyoda)", "xalqaro aeroport", "temir yo‘l va daryo"])
async def border_point_selected(message: types.Message):
    user_data['border_point'] = message.text
    await message.answer("Chegara oxirgi marta kesib o’tgan sanani kiriting (dd/mm/yyyy):", reply_markup=back_markup)

# Oldingi handlerlar o'zgarmaydi
@dp.message_handler(lambda message: bool(re.match(r'\d{2}/\d{2}/\d{4}', message.text)))
async def get_last_crossing_date(message: types.Message):
    user_data['last_crossing_date'] = message.text
    await message.answer("Tovarlarning qiymatini AQSH dollarida kiriting:", reply_markup=back_markup)


@dp.message_handler(lambda message: message.text.replace(".", "", 1).isdigit() and 'value' not in user_data)
async def get_value(message: types.Message):
    user_data['value'] = float(message.text)
    await message.answer("Tovarlarning og’irligini kiriting (kg):", reply_markup=back_markup)


@dp.message_handler(lambda message: message.text.replace(".", "", 1).isdigit() and 'value' in user_data)
async def calculate_fee(message: types.Message):
    user_data['weight'] = float(message.text)
    value = user_data['value']
    weight = user_data['weight']
    customs_fee = max(value * 0.30, weight * 3)
    await message.answer(
            f"""Sizning {value}$ qiymatdagi tovaringizdan tovarning bojxona qiymatidan 30 foiz,
            lekin har bir kilogrami uchun 3 AQSh dollaridan kam bo‘lmagan miqdorda
            yagona bojxona to‘lovi undiriladi ({customs_fee}$).""",
            reply_markup=back_markup
        )

@dp.message_handler(lambda message: message.text == contact_button.text)
async def contact_specialist(message: types.Message):
    await message.answer("Mutaxassis bilan bog'lanish uchun: @calibr_i", reply_markup=back_markup)

# Orqaga qaytish tugmasi
@dp.message_handler(lambda message: message.text == back_button.text)
async def go_back(message: types.Message):
    user_data.pop('value', None)
    user_data.pop('weight', None)

    await message.answer("Yana biror tanlov qilishingiz mumkin.", reply_markup=start_markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
