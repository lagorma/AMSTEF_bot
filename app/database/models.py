from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Integer, ARRAY, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_async_engine(url=os.getenv('SQLDB'))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), nullable=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'), nullable=True)
    position: Mapped[str] = mapped_column(String(50), nullable=True)
    deleted_flag: Mapped[bool] = mapped_column(nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=True)
    created_dttm = mapped_column(DateTime, nullable=True)
    city: Mapped[str] = mapped_column(String(50), nullable=True)
    push_time = mapped_column(Time, nullable=True)


class Company(Base):
    __tablename__ = 'companies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    inn: Mapped[str] = mapped_column(String(50), nullable=True)
    deleted_flag: Mapped[bool] = mapped_column(nullable=True)
    created_dttm = mapped_column(DateTime, nullable=True)


class AccessCode(Base):
    __tablename__ = 'access_code'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=True)
    valid_from = mapped_column(DateTime, nullable=True)
    valid_to = mapped_column(DateTime, nullable=True)


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)


class TestAnswer(Base):
    __tablename__ = 'answers'

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    created_dttm = mapped_column(DateTime, nullable=True)
    option_id: Mapped[int] = mapped_column(ForeignKey('options.id'), nullable=True)
    answer: Mapped[float] = mapped_column(nullable=True)


class TestQuestion(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True)
    test_type_id: Mapped[int] = mapped_column(ForeignKey('test_types.id'), nullable=True)
    question_text = mapped_column(ARRAY(String(200)), nullable=True)
    created_dttm = mapped_column(DateTime, nullable=True)
    option_id: Mapped[int] = mapped_column(ForeignKey('options.id'), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)


class TestType(Base):
    __tablename__ = 'test_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)


class Option(Base):
    __tablename__ = 'options'

    id: Mapped[int] = mapped_column(primary_key=True)
    answer = mapped_column(ARRAY(Integer), nullable=True)
    answer_text = mapped_column(ARRAY(String(50)), nullable=True)


class MessageHist(Base):
    __tablename__ = 'message_hist'

    id: Mapped[int] = mapped_column(primary_key=True)
    text_message: Mapped[str] = mapped_column(String(200), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    created_dttm = mapped_column(DateTime, nullable=True)
    deleted_flag: Mapped[bool] = mapped_column(nullable=True)
    author_id: Mapped[int] = mapped_column(nullable=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
