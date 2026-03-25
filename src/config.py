from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class Nastroyki:
    bot_token: str
    db_path: Path

    @classmethod
    def iz_konfiga(cls) -> "Nastroyki":
        bot_token = os.getenv("BOT_TOKEN", "PASTE_BOT_TOKEN_HERE").strip()
        raw_db_path = os.getenv("DB_PATH", "data/bot.sqlite3")
        db_path = Path(raw_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        return cls(bot_token=bot_token, db_path=db_path)
