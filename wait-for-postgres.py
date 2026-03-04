import os
import sys
import time
from urllib.parse import urlparse


def normalize_database_url(raw_url: str) -> str:
    """Normalize SQLAlchemy-style URL variants to libpq-compatible postgres URL."""
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    if raw_url.startswith("postgresql+psycopg://"):
        return raw_url.replace("postgresql+psycopg://", "postgresql://", 1)
    return raw_url


def try_connect_with_psycopg(db_url: str) -> None:
    import psycopg  # type: ignore

    conn = psycopg.connect(db_url, connect_timeout=5)
    conn.close()


def try_connect_with_psycopg2(db_url: str) -> None:
    import psycopg2  # type: ignore

    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port,
        connect_timeout=5,
    )
    conn.close()


def wait_for_postgres() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        sys.stdout.write("DATABASE_URL not found, skipping wait.\n")
        return

    db_url = normalize_database_url(db_url)
    max_retries = int(os.environ.get("DB_WAIT_MAX_RETRIES", "30"))
    sleep_seconds = float(os.environ.get("DB_WAIT_SLEEP_SECONDS", "2"))

    sys.stdout.write("Waiting for database to be ready...\n")

    retries = 0
    while retries < max_retries:
        try:
            try:
                try_connect_with_psycopg(db_url)
            except ModuleNotFoundError:
                try_connect_with_psycopg2(db_url)
            sys.stdout.write("Database is ready!\n")
            return
        except Exception:
            retries += 1
            sys.stdout.write(
                f"Attempt {retries}/{max_retries}: database not ready. Retrying in {sleep_seconds} seconds...\n"
            )
            time.sleep(sleep_seconds)

    sys.stderr.write("Error: could not connect to the database after several retries.\n")
    sys.exit(1)


if __name__ == "__main__":
    wait_for_postgres()
