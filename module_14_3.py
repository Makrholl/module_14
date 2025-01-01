import asyncio
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

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Product1', callback_data='product_buying')],
    [InlineKeyboardButton(text='Product2', callback_data='product_buying')],
    [InlineKeyboardButton(text='Product3', callback_data='product_buying')],
    [InlineKeyboardButton(text='Product4', callback_data='product_buying')]
])

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
    product_descriptions = [
        ("Product1", "Описание 1", 100, "image1.jpg"),
        ("Product2", "Описание 2", 200, "image2.jpg"),
        ("Product3", "Описание 3", 300, "image3.jpg"),
        ("Product4", "Описание 4", 400, "image4.jpg"),
    ]

    for name, description, price, image_path in product_descriptions:
        await message.answer(
            f"Название: {name} | Описание: {description} | Цена: {price * 100} рублей."
        )
        # Путь к изображению продукта
        try:
            await message.answer_photo(InputFile(image_path))
        except Exception as e:
            await message.answer(f"Не удалось отправить фото: {str(e)}")

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard)

@dp.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("Возраст должен быть числом. Попробуйте снова.")
        return
    await state.update_data(age=float(message.text))
    await message.answer("Введите свой рост (в см):")
    await UserState.growth.set()

@dp.message(UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("Рост должен быть числом. Попробуйте снова.")
        return
    await state.update_data(growth=float(message.text))
    await message.answer("Введите свой вес (в кг):")
    await UserState.weight.set()

@dp.message(UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("Вес должен быть числом. Попробуйте снова.")
        return
    await state.update_data(weight=float(message.text))

    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']

    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал/день.")
    await state.clear()

@dp.callback_query(F.data == 'product_buying')
async def send_confirm_message(call: CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.message()
async def unknown_command(message: Message):
    await message.answer("Неизвестная команда. Используйте кнопки меню.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

