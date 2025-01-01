import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery
)
from crud_functions import initiate_db, add_user, is_included

API_TOKEN = "0000"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DB_PATH = "database.db"


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


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать")],
        [KeyboardButton(text="Информация")],
        [KeyboardButton(text="Купить")],
        [KeyboardButton(text="Регистрация")]
    ],
    resize_keyboard=True
)


@dp.message(F.text == "/start")
async def start_command(message: Message):
    await message.answer(
        "Привет! Выберите опцию из меню ниже:",
        reply_markup=main_keyboard
    )


@dp.message(F.text == "Регистрация")
async def sing_up(message: Message, state: FSMContext):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await state.set_state(RegistrationState.username)


@dp.message(RegistrationState.username)
async def set_username(message: Message, state: FSMContext):
    username = message.text.strip()
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await state.set_state(RegistrationState.email)


@dp.message(RegistrationState.email)
async def set_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await state.set_state(RegistrationState.age)


@dp.message(RegistrationState.age)
async def set_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError("Возраст должен быть положительным.")

        data = await state.get_data()
        add_user(data['username'], data['email'], age)

        await message.answer(f"Регистрация завершена! Пользователь {data['username']} добавлен.")
        await state.finish()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (положительное число).")


@dp.message(F.text == 'Рассчитать')
async def calculate_calories(message: Message, state: FSMContext):
    await message.answer("Введите свой возраст (число):")
    await state.set_state(UserState.age)


@dp.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError("Возраст должен быть положительным.")
        await state.update_data(age=age)
        await message.answer("Введите свой рост (в см):")
        await state.set_state(UserState.growth)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст.")


@dp.message(UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    try:
        growth = int(message.text)
        if growth <= 0:
            raise ValueError("Рост должен быть положительным.")
        await state.update_data(growth=growth)
        await message.answer("Введите свой вес (в кг):")
        await state.set_state(UserState.weight)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный рост.")


@dp.message(UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным.")
        data = await state.get_data()
        calories = 10 * weight + 6.25 * data['growth'] - 5 * data['age'] + 5

        await message.answer(f"Ваша норма калорий: {calories:.2f} ккал/день.")
        await state.finish()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный вес.")


@dp.message(F.text == 'Информация')
async def information_handler(message: Message):
    await message.answer("Этот бот помогает рассчитать вашу норму калорий.")


@dp.message(F.text == 'Купить')
async def get_buying_list(message: Message):
    products = get_all_products()
    if not products:
        await message.answer("Продукты отсутствуют.")
        return

    inline_keyboard = InlineKeyboardMarkup()
    for product_id, title, description, price in products:
        await message.answer(
            f"Название: {title}\nОписание: {description}\nЦена: {price} рублей."
        )
        inline_keyboard.add(
            InlineKeyboardButton(text=f"Купить {title}", callback_data=f"buy_{product_id}")
        )
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard)


@dp.callback_query(F.data.startswith('buy_'))
async def handle_buy(call: CallbackQuery):
    product_id = call.data.split('_')[1]
    await call.message.answer(f"Вы успешно приобрели продукт с ID {product_id}!")
    await call.answer()


@dp.message()
async def unknown_command(message: Message):
    await message.answer("Неизвестная команда. Используйте кнопки меню.")


async def main():
    initiate_db(DB_PATH)
    seed_products()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())