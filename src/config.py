"""Настройки бота."""

import os

# токен берём из переменной окружения BOT_TOKEN
BOT_TOKEN = os.getenv('BOT_TOKEN')

# путь к файлу базы данных
DB_PATH = 'data/bot.sqlite3'
