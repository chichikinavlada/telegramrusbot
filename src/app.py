from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers import setup_handlers
from src.config import Nastroyki
from src.services.analyzer import AnalizatorTeksta
from src.services.database import BazaDannyh


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = Nastroyki.iz_konfiga()
    database = BazaDannyh(settings.db_path)
    database.initialize()
    analyzer = AnalizatorTeksta()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(setup_handlers(database, analyzer))

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


def run() -> None:
    asyncio.run(main())
