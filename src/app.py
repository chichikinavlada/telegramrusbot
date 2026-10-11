"""Запуск бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.bot.handlers import router
from src.config import BOT_TOKEN
from src.services.database import create_table


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        print('Не найден токен. Задай переменную окружения BOT_TOKEN.')
        return

    create_table()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


def run() -> None:
    """Запускает бота (вызывается из main.py)."""
    asyncio.run(main())
