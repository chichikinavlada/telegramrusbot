"""Настройки бота."""

import os

# токен берём из переменной окружения BOT_TOKEN, в коде его хранить нельзя
BOT_TOKEN = os.getenv('BOT_TOKEN')

# путь к файлу базы данных
DB_PATH = 'data/bot.sqlite3'
