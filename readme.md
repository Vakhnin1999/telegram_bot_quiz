# Чат бот
## используемые библиотеки
```python
import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
```
## Глобальные переменные и предустановки

```python
#логирование для важных сообщений
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()
#База Данных
DB_NAME = 'quiz_bot2.db'
```
## Хэндлеры

```python
# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text='Твой рекорд'))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

# Хендлер на команду /record
@dp.message(F.text=="Твой рекорд")
@dp.message(Command("record"))
async def cmd_record(message: types.Message):

    record = await get_quiz_record(message.from_user.id)
    await message.answer(f"Твой рекорд = {record}!")

# ответ на правильный ответ
@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    await callback.message.answer("Верно!")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    record_now = await get_quiz_record_now(callback.from_user.id)+1
    await update_quiz_index(callback.from_user.id, current_question_index, record_now)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        #await update_quiz_record(callback.from_user.id)
        record = await get_quiz_record(callback.from_user.id)
        if record < record_now:
            await update_quiz_record2(callback.from_user.id, record_now)

# ответ на неправильный ответ
@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    record_now = await get_quiz_record_now(callback.from_user.id)
    await update_quiz_index(callback.from_user.id, current_question_index, record_now)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:

        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        #await update_quiz_record(callback.from_user.id)
        record = await get_quiz_record(callback.from_user.id)
        if record < record_now:
            await update_quiz_record2(callback.from_user.id, record_now)

```

## Функции для работы с Telegram
```python
# создание кнопок для ответов
def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

# Создание сообщения с вопросом и вариантами ответа
async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

# Новый Квиз
async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    record_now = 0
    await update_quiz_index(user_id, current_question_index, record_now)
    await get_question(message, user_id)
# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)
```

## Функции для работы с БД
```python
async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        #await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''') \
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, record INTEGER, record_now INTEGER)''')
        # Сохраняем изменения
        await db.commit()


# Возвращение значений
async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def get_quiz_record_now(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT record_now FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def get_quiz_record(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT record FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results[0] is not None:
                return results[0]
            else:
                return 0

# Обновление значений
async def update_quiz_record2(user_id, record):
        async with aiosqlite.connect(DB_NAME) as db:
            # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
            await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, record) VALUES (?, ?)',(user_id, record))
            # Сохраняем изменения
            await db.commit()
async def update_quiz_index(user_id, index, record_now):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, record_now) VALUES (?, ?, ?)', (user_id, index, record_now))
        # Сохраняем изменения
        await db.commit()
```