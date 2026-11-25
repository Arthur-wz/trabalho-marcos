import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env", override=False)


def obter_conexao():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não encontrada no arquivo .env."
        )

    return psycopg.connect(
        database_url,
        row_factory=dict_row,
        connect_timeout=10
    )