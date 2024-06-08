import hashlib
import string
import random
import pandas as pd
from config import bot


def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(10))
    return password


def my_hash(text: str):
    return hashlib.sha1(text.encode()).hexdigest()


def get_questions_data(file_name, num):
    sheet = pd.read_excel(file_name, sheet_name=num)
    data = sheet.to_dict()

    lst = dict()
    for i in data:
        lst[i.lower()] = list(data[i].values())
    return lst


async def kill_mesage(chat_id, message_id, count_del=1):
    if count_del < 0:
        del_list = range(0, count_del, -1)
    else:
        del_list = range(count_del)

    for i in del_list:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id - i)
        except Exception as error:
            continue
