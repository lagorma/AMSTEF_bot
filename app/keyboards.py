from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.requests import get_test_types, get_option_data
from aiogram.utils.keyboard import InlineKeyboardBuilder

start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Вход", callback_data="sign_in"),
     InlineKeyboardButton(text="Регистрация", callback_data="sign_up")]
])

get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отправить номер", request_contact=True)]],
                                 resize_keyboard=True)

basic_screen = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text="Тестирования", callback_data="tests")],
    [InlineKeyboardButton(text="Статистика", callback_data="statistic")],
    # [InlineKeyboardButton(text="Хочу поиграть", callback_data="game")]
    # [InlineKeyboardButton(text="Чат Поддержки", callback_data="chat_help")]
])

games = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Виселица", callback_data="hangman")]
])

no_code = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="У меня нет входа", callback_data="sign_up")]
])

biba_i_boba = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Дабваить тест", callback_data="add_test")],
    [InlineKeyboardButton(text="Изменить права пользователя", callback_data="change_role")],
    [InlineKeyboardButton(text="Обновление сервера", callback_data="update_server")],
])

back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В главное меню", callback_data="to_main")]
])


async def test_types():
    all_types = await get_test_types()
    keyboard = InlineKeyboardBuilder()
    for test_type in all_types:
        keyboard.add(InlineKeyboardButton(text=test_type.name.capitalize(), callback_data=f'test_type_{test_type.id}'))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data=f'to_main'))
    return keyboard.adjust(2).as_markup()


#
async def test_mood_buttons(option_id):
    option = await get_option_data(option_id)
    keyboard = InlineKeyboardBuilder()
    for data in option:
        for i in range(len(data.answer)):
            keyboard.add(InlineKeyboardButton(text=data.answer_text[i], callback_data=f'answer_{data.answer[i]}'))
    return keyboard.adjust(6).as_markup()


async def test_stress_buttons(option_id):
    option = await get_option_data(option_id)
    keyboard = InlineKeyboardBuilder()
    for data in option:
        for i in range(len(data.answer)):
            keyboard.add(InlineKeyboardButton(text=data.answer_text[i], callback_data=f'answer_{data.answer[i]}'))
    return keyboard.adjust(1).as_markup()
