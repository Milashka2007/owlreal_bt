import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession

from database.engine import create_db, drop_db, session_maker

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.make_post import post_load

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from handlers.make_post import post_router


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)

bot.my_admins_list=[]

dp = Dispatcher()


dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)
dp.include_router(post_router)

async def on_startup(bot):

    #await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('бот ушел из семьи')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    scheduler=AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(post_load, trigger='interval', seconds=60)
    scheduler.start()

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())