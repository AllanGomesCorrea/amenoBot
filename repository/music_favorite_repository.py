import sqlite3
import os
import re

def extract_youtube_identifier(url: str) -> str:
    # Extrai o identificador do YouTube (?v= até & ou fim)
    match = re.search(r'[?&]v=([\w-]+)', url)
    if match:
        return match.group(1)
    return url  # fallback: retorna a url inteira se não encontrar

class MusicFavoriteRepository:
    def __init__(self, db_path='favorites.db'):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT UNIQUE,
                url TEXT,
                title TEXT
            )''')
            conn.commit()

    def exists(self, identifier: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT 1 FROM favorites WHERE identifier = ?', (identifier,))
            return c.fetchone() is not None

    def add(self, identifier: str, url: str, title: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO favorites (identifier, url, title) VALUES (?, ?, ?)', (identifier, url, title))
            conn.commit()
            return c.lastrowid

favorite_repo = MusicFavoriteRepository(os.path.join(os.path.dirname(__file__), '../../favorites.db')) 