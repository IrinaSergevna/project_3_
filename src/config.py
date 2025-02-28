from os import getenv
from typing import Optional


class Config:
    """Конфигурация проекта с параметрами подключения к БД."""

    def __init__(self):
        self.db_name: str = getenv("DB_NAME") or "hh_vacancies"
        self.db_user: str = getenv("DB_USER") or "postgres"
        self.db_password: str = getenv("DB_PASSWORD")
        self.db_host: str = getenv("DB_HOST") or "localhost"
        self.db_port: str = getenv("DB_PORT") or "5432"

        if not self.db_password:
            raise ValueError("Переменная окружения DB_PASSWORD обязательна и не задана")

    def get_db_params(self) -> dict[str, str]:
        """Возвращает параметры подключения к БД."""
        return {
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "host": self.db_host,
            "port": self.db_port
        }