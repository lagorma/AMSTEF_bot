from aiogram import Dispatcher
import asyncio

from app.database.models import async_main
import app.database.requests as rq
from app.handlers import router, set_daily_time_message, scheduler
from config import bot


async def main():
    await async_main()
    await rq.set_roles()
    await set_daily_time_message()
    scheduler.start()
    print("Всё норм")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Всё норм, просто остановка бота")
