import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery, InputFile
)

API_TOKEN = "0000"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DB_PATH = "database.db"


def initiate_db(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')
    connection.commit()
    connection.close()


def seed_products(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('SELECT COUNT(*) FROM Products')
    if cursor.fetchone()[0] == 0:
        products = [
            ("Product1", "Описание продукта 1", 100),
            ("Product2", "Описание продукта 2", 200),
            ("Product3", "Описание продукта 3", 300),
            ("Product4", "Описание продукта 4", 400)
        ]
        cursor.executemany('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)', products)
        connection.commit()
    connection.close()


def get_all_products(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT id, title, description, price FROM Products')
    products = cursor.fetchall()
    connection.close()
    return products


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать')],
        [KeyboardButton(text='Информация')],
        [KeyboardButton(text='Купить')]
    ],
    resize_keyboard=True
)


@dp.message(F.text == '/start')
async def start_command(message: Message):
    await message.answer(
        "Привет! Я помогу рассчитать норму калорий.\nВыберите опцию ниже:",
        reply_markup=main_keyboard
    )


@dp.message(F.text == 'Рассчитать')
async def calculate_calories(message: Message):
    await message.answer("Введите свой возраст (число):")
    await UserState.age.set()


@dp.message(F.text == 'Информация')
async def information_handler(message: Message):
    await message.answer(
        "Этот бот помогает рассчитать вашу норму калорий по введённым параметрам.\n"
        "Нажмите 'Рассчитать', чтобы начать!"
    )


@dp.message(F.text == 'Купить')
async def get_buying_list(message: Message):
    # Получаем продукты из базы данных
    products = get_all_products(DB_PATH)

    if not products:
        await message.answer("Продукты отсутствуют.")
        return

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product in products:
        product_id, title, description, price = product

        await message.answer(
            f"Название: {title}\nОписание: {description}\nЦена: {price} рублей."
        )

        image_path = os.path.join(
            "/Users/makar/Documents/1Програмирование/Homework1/Files",
            f"{title.lower()}.jpg"
        )
        if os.path.exists(image_path):
            await message.answer_photo(InputFile(image_path))
        else:
            await message.answer("Изображение недоступно.")

        inline_keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"Купить {title}", callback_data=f"buy_{product_id}")
        ])

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard)


@dp.callback_query(F.data.startswith('buy_'))
async def handle_buy(call: CallbackQuery):
    product_id = call.data.split('_')[1]
    await call.message.answer(f"Вы успешно приобрели продукт с ID {product_id}!")
    await call.answer()


@dp.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    try:
        age = float(message.text)
        await state.update_data(age=age)
        await message.answer("Введите свой рост (в см):")
        await UserState.growth.set()
    except ValueError:
        await message.answer("Возраст должен быть числом. Попробуйте снова.")


@dp.message(UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    try:
        growth = float(message.text)
        await state.update_data(growth=growth)
        await message.answer("Введите свой вес (в кг):")
        await UserState.weight.set()
    except ValueError:
        await message.answer("Рост должен быть числом. Попробуйте снова.")


@dp.message(UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)

        data = await state.get_data()
        age = data['age']
        growth = data['growth']
        weight = data['weight']

        calories = 10 * weight + 6.25 * growth - 5 * age + 5
        await message.answer(f"Ваша норма калорий: {calories:.2f} ккал/день.")
        await state.clear()
    except ValueError:
        await message.answer("Вес должен быть числом. Попробуйте снова.")


@dp.message()
async def unknown_command(message: Message):
    await message.answer("Неизвестная команда. Используйте кнопки меню.")


async def main():
    # Инициализация базы данных
    initiate_db(DB_PATH)
    seed_products(DB_PATH)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

