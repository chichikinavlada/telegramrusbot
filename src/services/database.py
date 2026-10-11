"""Работа с базой данных SQLite: сохраняем историю анализов."""

import os
import sqlite3

from src.config import DB_PATH


def create_table() -> None:
    """Создаёт таблицу text_analyses, если её ещё нет."""
    os.makedirs('data', exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS text_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            word_count INTEGER,
            sentence_count INTEGER,
            top_lemmas TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()


def save_analysis(user_id: int, result: dict) -> None:
    """Сохраняет результат анализа. Леммы записываем в одну строку через запятую."""
    lemmas = []
    for lemma, count in result['top_lemmas']:
        lemmas.append(lemma)
    lemmas_text = ', '.join(lemmas)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        'INSERT INTO text_analyses (user_id, word_count, sentence_count, top_lemmas) VALUES (?, ?, ?, ?)',
        (user_id, result['word_count'], result['sentence_count'], lemmas_text),
    )
    con.commit()
    con.close()


def get_recent_analyses(user_id: int, limit: int = 5) -> list:
    """Возвращает последние анализы пользователя (сначала самые новые)."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        'SELECT created_at, word_count, sentence_count, top_lemmas '
        'FROM text_analyses WHERE user_id = ? ORDER BY id DESC LIMIT ?',
        (user_id, limit),
    )
    rows = cur.fetchall()
    con.close()
    return rows


def get_user_stats(user_id: int) -> tuple:
    """Возвращает количество анализов пользователя и среднее число слов в тексте."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        'SELECT COUNT(id), AVG(word_count) FROM text_analyses WHERE user_id = ?',
        (user_id,),
    )
    total, average = cur.fetchone()
    con.close()

    # если анализов ещё не было, AVG вернёт None
    if average is None:
        average = 0
    return total, round(average, 1)
