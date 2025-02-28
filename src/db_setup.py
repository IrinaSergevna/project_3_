import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Dict


def create_database(db_params: Dict[str, str]) -> None:
    """Создаёт базу данных, если она не существует."""
    conn = psycopg2.connect(
        dbname="postgres",
        user=db_params["user"],
        password=db_params["password"],
        host=db_params["host"],
        port=db_params["port"]
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    db_name = db_params["dbname"]
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {db_name}")
    cursor.close()
    conn.close()


def drop_tables(db_params: Dict[str, str]) -> None:
    """Удаляет существующие таблицы employers и vacancies."""
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS vacancies, employers CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Ошибка в drop_tables:", str(e))
        raise


def create_tables(db_params: Dict[str, str]) -> None:
    """Создаёт таблицы в базе данных."""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            employer_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(20) PRIMARY KEY,
            employer_id VARCHAR(20) REFERENCES employers(employer_id),
            name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            url VARCHAR(255)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()