from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.services.analyzer import RezultatAnaliza, Sushchnost


class BazaDannyh:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    source_text TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    sentence_count INTEGER NOT NULL,
                    top_lemmas_json TEXT NOT NULL,
                    entities_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    def save_analysis(self, user_id: int, username: str | None, result: RezultatAnaliza) -> int:
        top_lemmas_json = json.dumps(result.top_lemmas, ensure_ascii=False)
        entities_json = json.dumps([asdict(entity) for entity in result.entities], ensure_ascii=False)

        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO analyses (
                    user_id,
                    username,
                    source_text,
                    word_count,
                    sentence_count,
                    top_lemmas_json,
                    entities_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    username,
                    result.source_text,
                    result.word_count,
                    result.sentence_count,
                    top_lemmas_json,
                    entities_json,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def get_recent_analyses(self, user_id: int, limit: int = 5) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT created_at, word_count, sentence_count, top_lemmas_json
                FROM analyses
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

        result: list[dict[str, Any]] = []
        for row in rows:
            top_lemmas = json.loads(row["top_lemmas_json"])
            result.append(
                {
                    "created_at": row["created_at"],
                    "word_count": row["word_count"],
                    "sentence_count": row["sentence_count"],
                    "top_lemmas": top_lemmas,
                }
            )
        return result

    def get_user_stats(self, user_id: int) -> dict[str, int | float]:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total_analyses, COALESCE(AVG(word_count), 0) AS avg_word_count
                FROM analyses
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        total_analyses = int(row[0]) if row else 0
        avg_word_count = round(float(row[1]), 1) if row else 0.0
        return {
            "total_analyses": total_analyses,
            "avg_word_count": avg_word_count,
        }

    def parse_entities(self, raw_json: str) -> list[Sushchnost]:
        payload = json.loads(raw_json)
        return [Sushchnost(**item) for item in payload]
