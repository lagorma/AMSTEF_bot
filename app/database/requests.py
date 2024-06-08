from app.database.models import async_session
from app.database.models import User, Company, AccessCode, Option, Role, TestType, TestQuestion, TestAnswer
from sqlalchemy import select, func
from datetime import datetime, timedelta, time

from other.functions import my_hash, get_questions_data


async def is_company_consist(company):
    async with async_session() as session:
        return await session.scalar(select(Company).where(Company.name == company))


async def is_user_reg(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def is_uniq_code_consist(code):
    async with async_session() as session:
        return await session.scalar(select(AccessCode).where(AccessCode.code == my_hash(code)))


async def get_none_user_columns(tg_id):
    async with async_session() as session:
        record = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not record:
            return None  # Если запись не найдена, возвращаем None или можно вернуть сообщение об ошибке

        unfilled_fields = []
        # Проходим по всем полям модели и проверяем, есть ли значение None
        for column in User.__table__.columns:
            field_name = column.name
            if getattr(record, field_name) is None:
                unfilled_fields.append(field_name)

        return unfilled_fields


async def create_access_code(password, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        session.add(AccessCode(user_id=user.id, code=my_hash(password), valid_from=datetime.utcnow(),
                               valid_to=datetime.utcnow() + timedelta(days=3650)))
        await session.commit()


async def registrate_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        print(tg_id)
        # company = await session.scalar(select(Company).where(Company.name == company))
        role = await session.scalar(select(Role).where(Role.name == "сотрудник"))

        if not user:
            session.add(User(tg_id=tg_id, deleted_flag=False, role_id=role.id, created_dttm=datetime.utcnow()))
            await session.commit()


async def add_company(company_name):
    async with async_session() as session:
        session.add(Company(name=company_name))
        await session.commit()


async def create_answer(quest_id, option_id, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(TestAnswer(question_id=quest_id, customer_id=user.id, option_id=option_id, answer=0))
        await session.commit()


async def add_answer(number, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        answer = await session.scalar(
            select(TestAnswer).where((TestAnswer.answer == 0) & (TestAnswer.customer_id == user.id)))
        print(answer.answer)
        answer.answer = number
        answer.created_dttm = datetime.utcnow()
        await session.commit()


async def add_new_test(file_name):
    data1 = get_questions_data(file_name, 0)
    data2 = get_questions_data(file_name, 1)
    data3 = get_questions_data(file_name, 2)
    async with async_session() as session:
        session.add(Option(answer=data2['цифра'], answer_text=data2['текст']))
        await session.commit()
        option_id = await session.scalar(select(func.max(Option.id)).select_from(Option))
        test_type = await session.scalar(
            select(TestType).where(TestType.name == data1['тип теста (настроение, выгорание, стрес, и т.д.)'][0]))
        if not test_type:
            session.add(TestType(name=data1['тип теста (настроение, выгорание, стрес, и т.д.)'][0]))
            await session.commit()
        test_type = await session.scalar(
            select(TestType).where(TestType.name == data1['тип теста (настроение, выгорание, стрес, и т.д.)'][0]))
        test_type_id = test_type.id
        description = " " if str(data1['описание теста'][0]) == 'nan' else data1['описание теста'][0]
        session.add(TestQuestion(test_type_id=test_type_id, question_text=data1['список вопросов без нумерации'],
                                 created_dttm=datetime.utcnow(), option_id=option_id, description=description))
        await session.commit()
        # question_id = await session.scalar(select(func.max()).select_from(TestQuestion.id))
        # добавить в расшифровку


async def add_name_to_user(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.name = name
        await session.commit()


async def add_phone_to_user(tg_id, phone):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.phone_number = phone
        await session.commit()


async def add_company_to_user(tg_id, company_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        company = await session.scalar(select(Company).where(Company.name == company_name))
        user.company_id = company.id
        await session.commit()


async def add_position_to_user(tg_id, position):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.position = position
        await session.commit()


async def add_city_to_user(tg_id, city: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.city = city.capitalize()
        await session.commit()


async def add_push_time_to_user(tg_id, time_str, time2):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        time1 = datetime.strptime(time_str, "%H:%M").time()
        delta1 = timedelta(hours=time1.hour, minutes=time1.minute)
        delta2 = timedelta(hours=time2.hour, minutes=time2.minute)
        delta = delta1 - delta2
        total_seconds = delta.total_seconds()

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        user.push_time = time(int(hours), int(minutes), int(seconds))
        await session.commit()


async def set_roles():
    async with async_session() as session:
        role = await session.scalar(select(func.count()).select_from(Role))

        if role == 0:
            session.add(Role(name="сотрудник"))
            session.add(Role(name="руководитель"))
            session.add(Role(name="админ"))
            await session.commit()


async def get_test_types():
    async with async_session() as session:
        return await session.scalars(select(TestType))


async def get_test_type_by_name(test_name):
    async with async_session() as session:
        test = await session.scalar(select(TestType).where(TestType.name == test_name))
        return test.id


async def get_questions(test_type_id):
    async with async_session() as session:
        return await session.scalar(select(TestQuestion).where(TestQuestion.test_type_id == test_type_id))


async def get_option_data(option_id):
    async with async_session() as session:
        return await session.scalars(select(Option).where(Option.id == option_id))


async def get_users_push_time():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id, User.push_time))
        users = result.all()
        user_dict = {user.tg_id: user.push_time for user in users}
        return user_dict


async def get_user_city(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user.city


async def get_mood_answer_and_date(tg_id):
    async with async_session() as session:
        test_type = await session.scalar(select(TestType).where(TestType.name == "настроение"))
        question = await session.scalar(select(TestQuestion).where(TestQuestion.test_type_id == test_type.id))
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        result = select(TestAnswer.answer, TestAnswer.created_dttm).where(
            (TestAnswer.customer_id == user.id) & (TestAnswer.question_id == question.id)
        )
        result = await session.execute(result)
        rows = result.fetchall()
        answers = [row[0] for row in rows]
        created_times = [row[1].strftime("%d.%m") for row in rows]

    return answers, created_times


async def get_stress_answer_and_date(tg_id):
    async with async_session() as session:
        test_type = await session.scalar(select(TestType).where(TestType.name == "стресс"))
        question = await session.scalar(select(TestQuestion).where(TestQuestion.test_type_id == test_type.id))
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        result = select(TestAnswer.answer, TestAnswer.created_dttm).where(
            (TestAnswer.customer_id == user.id) & (TestAnswer.question_id == question.id)
        )
        result = await session.execute(result)
        rows = result.fetchall()
        answers = [row[0] for row in rows]
        created_times = [row[1].strftime("%d.%m") for row in rows]

    return answers, created_times


async def get_users_tg():
    async with async_session() as session:
        result = select(User.tg_id)
        result = await session.execute(result)
        rows = result.fetchall()
        users = [row[0] for row in rows]
        return users
