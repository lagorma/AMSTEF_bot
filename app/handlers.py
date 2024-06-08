from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ContentType, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.jobstores.base import JobLookupError
from aiogram.fsm.storage.memory import MemoryStorage
from random import sample

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz
from datetime import datetime, timedelta

import app.keyboards as kb
import app.database.requests as rq
from other.functions import generate_password, get_questions_data, kill_mesage
from other.mood_graph import create_mood_graph, create_stress_graph
from config import bot

router = Router()
scheduler = AsyncIOScheduler()
geolocator = Nominatim(user_agent="AMSTEF")
tf = TimezoneFinder()


class Register(StatesGroup):
    name = State()
    phone = State()
    company = State()
    position = State()
    push_time = State()
    city = State()


class SignIn(StatesGroup):
    code = State()


class TestCreate(StatesGroup):
    file = State()


class Update(StatesGroup):
    time = State()


class StressTest(StatesGroup):
    answer_len = State()
    answer = State()
    answer_text = State()
    option_id = State()
    answer_data = State()


class Hangman(StatesGroup):
    word = State()
    letter = State()
    win_lose = State()


# region Comands
@router.message(Command("start", "main_menu"))
async def start_message(message: Message, state: FSMContext):
    result = await rq.is_user_reg(message.from_user.id)
    if not result:
        await message.answer("Добро пожаловать в AMSTEF\nАвторизируйтесь на платформе", reply_markup=kb.start)
        await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
    else:
        await message.answer(f'Добро пожаловать', reply_markup=kb.basic_screen)
        data = await rq.get_none_user_columns(message.from_user.id)
        print(data)
        if len(data) != 0:
            await message.answer(f'У вас не заполненные данные')
            await update_data_user(data[0], message, state)
        await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)


@router.message(Command("biba_i_boba"))
async def start_message(message: Message):
    await message.answer("Добро пожаловать сэр. Чего изволите?", reply_markup=kb.biba_i_boba)
    await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)


# endregion

# region SignIn
@router.callback_query(F.data == "sign_in")
async def sign_in(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Выполните вход")
    await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await state.set_state(SignIn.code)
    await callback.message.answer("Введите уникальный код, выданный вашим работодателем")


@router.message(SignIn.code)
async def register_age(message: Message, state: FSMContext):
    result = await rq.is_uniq_code_consist(message.text)
    if result:
        await state.update_data(code=message.text)
        await state.clear()
        await message.answer("Вход выполнен")
        await message.answer(f'Добро пожаловать', reply_markup=kb.basic_screen)
        data = await rq.get_none_user_columns(message.from_user.id)
        if len(data) != 0:
            await message.answer(f'У вас не заполненные данные')
            await update_data_user(data[0], message, state)
        else:
            await message.answer("Спасибо, данные успешно сохранены!")
            await state.clear()

    else:
        await state.set_state(SignIn.code)
        await message.answer("Попробуйте ещё раз")


# endregion

# region SignUp
@router.callback_query(F.data == "sign_up")
async def sign_in(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Выполните регистрацию")
    await rq.registrate_user(callback.from_user.id)
    password = generate_password()
    await rq.create_access_code(password, callback.from_user.id)

    data = await rq.get_none_user_columns(callback.from_user.id)
    if len(data) != 0:
        await update_data_user(data[0], callback.message, state)


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    if len(message.text.split()) >= 3:
        await rq.add_name_to_user(message.from_user.id, message.text)
        data = await rq.get_none_user_columns(message.from_user.id)
        if len(data) != 0:
            await update_data_user(data[0], message, state)
        else:
            await message.answer("Спасибо, данные успешно сохранены!", reply_markup=kb.back_to_main_menu)
            await state.clear()
    else:
        await state.set_state(Register.name)
        await message.answer("Неверный формат\nВведите ФИО через пробел")


@router.message(Register.phone)
async def register_phone(message: Message, state: FSMContext):
    if "+7" in message.text and len(message.text) == 12:
        await rq.add_phone_to_user(message.from_user.id, message.text)
        data = await rq.get_none_user_columns(message.from_user.id)
        if len(data) != 0:
            await update_data_user(data[0], message, state)
        else:
            await message.answer("Спасибо, данные успешно сохранены!", reply_markup=kb.back_to_main_menu)
            await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
            await state.clear()
    else:
        await state.set_state(Register.phone)
        await message.answer("Неверный формат\nВведите номер телефона в формате +79999999999")


@router.message(Register.company)
async def register_company(message: Message, state: FSMContext):
    result = await rq.is_company_consist(message.text)
    if not result:
        await rq.add_company(message.text)
    await rq.add_company_to_user(message.from_user.id, message.text)
    data = await rq.get_none_user_columns(message.from_user.id)
    if len(data) != 0:
        await update_data_user(data[0], message, state)
    else:
        await message.answer("Спасибо, данные успешно сохранены!", reply_markup=kb.back_to_main_menu)
        await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
        await state.clear()


@router.message(Register.position)
async def register_position(message: Message, state: FSMContext):
    await rq.add_position_to_user(message.from_user.id, message.text)
    data = await rq.get_none_user_columns(message.from_user.id)
    if len(data) != 0:
        await update_data_user(data[0], message, state)
    else:
        await message.answer("Спасибо, данные успешно сохранены!", reply_markup=kb.back_to_main_menu)
        await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
        await state.clear()


@router.message(Register.city)
async def register_time(message: Message, state: FSMContext):
    city = message.text.lower()
    await rq.add_city_to_user(message.from_user.id, city)
    data = await rq.get_none_user_columns(message.from_user.id)
    if len(data) != 0:
        await update_data_user(data[0], message, state)
    else:
        await message.answer("Спасибо, данные успешно сохранены!", reply_markup=kb.back_to_main_menu)
        await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
        await state.clear()


@router.message(Register.push_time)
async def register_time(message: Message, state: FSMContext):
    if len(message.text.split(":")) == 2:
        city = await rq.get_user_city(message.from_user.id)

        location = geolocator.geocode(city, language='ru')
        if location:
            latitude = location.latitude
            longitude = location.longitude
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_str:
                timezone = pytz.timezone(timezone_str)
                utc_time = datetime.utcnow()
                local_time = utc_time.astimezone(timezone)
                different = datetime.strptime(str(local_time).split("+")[1], "%H:%M").time()
                await rq.add_push_time_to_user(message.from_user.id, message.text, different)
                await set_daily_time_message()
            else:
                print("Извините, не удалось определить временную зону для этого города.")
        else:
            print("Извините, не удалось найти этот город.")

        data = await rq.get_none_user_columns(message.from_user.id)
        if len(data) != 0:
            await update_data_user(data[0], message, state)
        else:
            await message.answer("Спасибо, данные успешно сохранены!", reply_markup=kb.back_to_main_menu)
            await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
            await state.clear()
            await send_daily_mood_test(message.from_user.id)
    else:
        await state.set_state(Register.push_time)
        await message.answer("Неверный формат\nВведите время в которое вам удобно проходить тест в формате ##:##")


# endregion

# region Tests
# @router.callback_query(F.data == "tests")
# async def choose_test(callback: CallbackQuery, state: FSMContext):
#     await callback.answer(" ")
#     await state.set_state(Test.answer_len)
#     await callback.message.answer("Выберете показатель, который хотели бы оценить",
#                                   reply_markup=await kb.test_types())
#     await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=2)
#
#
# @router.callback_query(F.data.startswith("test_type_"), Test.answer_len)
# async def test(callback: CallbackQuery, state: FSMContext):
#     await callback.answer(" ")
#     question_data = await rq.get_questions(int(callback.data.split('_')[-1]))
#     await state.update_data(answer_len=len(question_data.question_text))
#     await state.update_data(answer=0)
#     await state.update_data(answer_text=question_data.question_text)
#     await state.update_data(option_id=question_data.option_id)
#     await state.set_state(Test.answer)
#     if question_data.description:
#         await callback.message.answer(question_data.description)
#     await callback.message.answer(question_data.question_text[0],
#                                   reply_markup=await kb.test_buttons(question_data.option_id))
#     await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=2)


# region STRESS TIME TEST
# @router.message(Command("stress_test"))
async def send_daily_stress_test(callback: CallbackQuery, state: FSMContext):
    test_type_id = await rq.get_test_type_by_name("стресс")
    question_data = await rq.get_questions(test_type_id)
    quest_with = []
    quest_without = []
    for i in question_data.question_text:
        if "*" in i:
            quest_with.append(i[2:])
        else:
            quest_without.append(i)

    quest_data = sample(quest_without, 2) + sample(quest_with, 2)

    await state.update_data(answer_len=len(quest_data))
    await state.update_data(answer=0)
    await state.update_data(answer_text=quest_data)
    await state.update_data(option_id=question_data.option_id)
    await state.update_data(answer_data=[])
    print(question_data.id, question_data.option_id, callback.from_user.id)
    await rq.create_answer(quest_id=question_data.id, option_id=question_data.option_id, tg_id=callback.from_user.id)

    await state.set_state(StressTest.answer)
    # await rq.create_answer(quest_id=question_data.id, option_id=question_data.option_id, tg_id=message.from_user.id)
    await callback.message.answer(quest_data[0],
                                  reply_markup=await kb.test_stress_buttons(question_data.option_id))


@router.callback_query(F.data.startswith("answer_"), StressTest.answer)
async def get_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer(" ")
    await state.update_data(answer=int(data["answer"]) + 1)
    await state.update_data(answer_data=data["answer_data"] + [int(callback.data.split('_')[-1])])
    if data["answer"] < data["answer_len"] - 1:
        await state.set_state(StressTest.answer)
        await callback.message.answer(data["answer_text"][data["answer"] + 1],
                                      reply_markup=await kb.test_stress_buttons(data["option_id"]))
        await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)
    else:
        data = await state.get_data()
        num = ((data["answer_data"][0] + data["answer_data"][1]) / 2) + (
                7 - ((data["answer_data"][2] + data["answer_data"][3]) / 2))
        await rq.add_answer(int(num), callback.from_user.id)
        print(num, callback.from_user.id)
        await callback.message.answer("Спасибо за ответ.", reply_markup=kb.back_to_main_menu)
        await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)
        await state.clear()


# endregion

# region MOOD TEST

async def send_daily_mood_test(user_id):
    test_type_id = await rq.get_test_type_by_name("настроение")
    question_data = await rq.get_questions(test_type_id)
    await rq.create_answer(quest_id=question_data.id, option_id=question_data.option_id, tg_id=user_id)
    await bot.send_message(user_id, question_data.question_text[0],
                           reply_markup=await kb.test_mood_buttons(question_data.option_id))


@router.callback_query(F.data.startswith("answer_"))
async def get_answer(callback: CallbackQuery, state: FSMContext):
    print(int(callback.data.split('_')[-1]))
    await callback.answer(" ")
    await rq.add_answer(int(callback.data.split('_')[-1]), callback.from_user.id)
    await callback.message.answer("Спасибо за ответ.\nТеперь тест на стресс")
    await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)
    await state.clear()
    await send_daily_stress_test(callback, state)


# endregion

# endregion

# region ChitCodes
@router.callback_query(F.data == "add_test")
async def add_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Хорошо, Сэр")
    await state.set_state(TestCreate.file)
    await callback.message.answer("Отправьте excel файл заполненый по шаблону")


@router.message(TestCreate.file)
async def save_reg_data(message: Message, state: FSMContext):
    await message.bot.download(file=message.document.file_id, destination=message.document.file_name)
    await rq.add_new_test(message.document.file_name)
    await message.answer(f'Проверяйте Сэр')
    await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)
    await state.clear()


@router.callback_query(F.data == "update_server")
async def add_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Как пожелаете, Сэр")
    await state.set_state(Update.time)
    await callback.message.answer("В какое время по utc это произойдёт? (формат - ##:##)")


@router.message(Update.time)
async def save_reg_data(message: Message, state: FSMContext):
    users_tg_id = await rq.get_users_tg()

    for user_id in users_tg_id:
        city = await rq.get_user_city(user_id)

        location = geolocator.geocode(city, language='ru')
        if location:
            latitude = location.latitude
            longitude = location.longitude
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_str:
                timezone = pytz.timezone(timezone_str)
                utc_time = datetime.utcnow()
                local_time = utc_time.astimezone(timezone)
                different = datetime.strptime(str(local_time).split("+")[1], "%H:%M").time()
                time1 = datetime.strptime(message.text, "%H:%M").time()
                delta1 = timedelta(hours=time1.hour, minutes=time1.minute)
                delta2 = timedelta(hours=different.hour, minutes=different.minute)
                delta = delta1 + delta2
                total_seconds = delta.total_seconds()

                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                await bot.send_message(str(user_id),
                                       f"Планируется обновление бота и перезапуск сервера в {int(hours)}:{int(minutes)}"
                                       f":00 на 5 минут, бот в это время работать не будет")
    await message.answer(f'Уведомление отправленно Сэр')
    await state.clear()


# endregion

@router.callback_query(F.data == "to_main")
async def main_screen(callback: CallbackQuery):
    await callback.answer(" ")
    await callback.message.answer(f'Добро пожаловать', reply_markup=kb.basic_screen)
    await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)


@router.callback_query(F.data == "statistic")
async def sign_in(callback: CallbackQuery):
    await callback.answer(" ")
    await create_mood_graph(callback.from_user.id)
    await create_stress_graph(callback.from_user.id)

    photo_mood = FSInputFile(f"img/mood/{callback.from_user.id}mood.png")
    await callback.message.answer_photo(photo_mood, caption="Ваше настроение по дням")
    photo_stress = FSInputFile(f"img/stress/{callback.from_user.id}stress.png")
    await callback.message.answer_photo(photo_stress, caption="Ваш уровень стресса", reply_markup=kb.back_to_main_menu)
    await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)


@router.callback_query(F.data == "game")
async def sign_in(callback: CallbackQuery):
    await callback.answer(" ")
    await callback.message.answer(f'Выберите игру', reply_markup=kb.games)
    await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)


# region Games

@router.callback_query(F.data == "hangman")
async def sign_in(callback: CallbackQuery):
    await callback.answer(" ")
    await callback.message.answer(f'Выберите игру', reply_markup=kb.games)
    await kill_mesage(chat_id=callback.from_user.id, message_id=callback.message.message_id, count_del=10)


# endregion


async def update_data_user(param, message, state):
    match param:
        case "name":
            await state.set_state(Register.name)
            await message.answer("Введите фамилию, имя и отчество\n(через пробел)")
        case "phone_number":
            await state.set_state(Register.phone)
            await message.answer('Введите номер телефона в формате +79*********')
        case "company_id":
            await state.set_state(Register.company)
            await message.answer("Введите название компании")
        case "position":
            await state.set_state(Register.position)
            await message.answer("Введите свою должность")
        case "city":
            await state.set_state(Register.city)
            await message.answer("Введите город, в котором проживаете")
        case "push_time":
            await state.set_state(Register.push_time)
            await message.answer("Введите время в которое вам удобно проходить тест в формате ##:##")
    await kill_mesage(chat_id=message.from_user.id, message_id=message.message_id, count_del=10)


async def set_daily_time_message():
    user_dict = await rq.get_users_push_time()
    for i in user_dict:
        job_id = f'notification_{i}'
        try:
            scheduler.remove_job(job_id)
        except JobLookupError:
            pass
        try:
            scheduler.add_job(send_daily_mood_test, 'cron', hour=user_dict[i].hour, minute=user_dict[i].minute,
                              args=[i],
                              id=job_id)
            print(i, ": hour -", user_dict[i].hour, "minute -", user_dict[i].minute)
        except Exception:
            pass
