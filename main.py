import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
#переносим некотурую информацию в другие файлы
from API_Token import API_TOKEN
from quiz_data import quiz_data
from work_bd import *
from bot_function import *
#логирование для важных сообщений
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# # Обновление номера текущего вопроса в базе данных (не работает)
# async def update_and_next(callback,current_question_index):
#     current_question_index += 1
#     await update_quiz_index(callback.from_user.id, current_question_index)
#
#
#     if current_question_index < len(quiz_data):
#         await get_question(callback.message, callback.from_user.id)
#     else:
#         await callback.message.answer("Это был последний вопрос. Квиз завершен!")

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



# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())