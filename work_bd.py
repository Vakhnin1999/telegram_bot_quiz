import aiosqlite
import asyncio


#База Данных
DB_NAME = 'quiz_bot2.db'

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

# async def update_quiz_record(user_id):
#     #ленивый способ
#     record = get_quiz_record(user_id)
#     record_now = get_quiz_record_now(user_id)
#     if record < record_now: # в этом месте возникает ошибка из-за знака
#         async with aiosqlite.connect(DB_NAME) as db:
#             # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
#             await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, record) VALUES (?, ?)',(user_id, record))
#             # Сохраняем изменения
#             await db.commit()

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
# async def update_quiz_index(user_id, index):
#     # Создаем соединение с базой данных (если она не существует, она будет создана)
#     async with aiosqlite.connect(DB_NAME) as db:
#         # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
#         await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
#         # Сохраняем изменения
#         await db.commit()

