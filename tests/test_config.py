import pytest
from src.config import Config


def test_config_with_all_env_vars(monkeypatch):
    """Тест создания Config с полным набором переменных окружения."""
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_pass")
    monkeypatch.setenv("DB_HOST", "test_host")
    monkeypatch.setenv("DB_PORT", "1234")

    config = Config()
    params = config.get_db_params()

    assert config.db_name == "test_db"
    assert config.db_user == "test_user"
    assert config.db_password == "test_pass"
    assert config.db_host == "test_host"
    assert config.db_port == "1234"
    assert params == {
        "dbname": "test_db",
        "user": "test_user",
        "password": "test_pass",
        "host": "test_host",
        "port": "1234"
    }


def test_config_with_defaults(monkeypatch):
    """Тест создания Config с использованием значений по умолчанию."""
    # Удаляем DB_NAME из окружения, чтобы использовать значение по умолчанию
    monkeypatch.delenv("DB_NAME", raising=False)
    # Устанавливаем только обязательный DB_PASSWORD
    monkeypatch.setenv("DB_PASSWORD", "test_pass")

    config = Config()
    params = config.get_db_params()

    assert config.db_name == "hh_vacancies"  # Значение по умолчанию
    assert config.db_user == "postgres"
    assert config.db_password == "test_pass"
    assert config.db_host == "localhost"
    assert config.db_port == "5432"
    assert params == {
        "dbname": "hh_vacancies",
        "user": "postgres",
        "password": "test_pass",
        "host": "localhost",
        "port": "5432"
    }


def test_config_missing_password(monkeypatch):
    """Тест выброса исключения при отсутствии DB_PASSWORD."""
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="Переменная окружения DB_PASSWORD обязательна и не задана"):
        Config()


def test_config_partial_env_vars(monkeypatch):
    """Тест создания Config с частичным набором переменных окружения."""
    monkeypatch.setenv("DB_NAME", "custom_db")
    monkeypatch.setenv("DB_PASSWORD", "custom_pass")

    config = Config()
    params = config.get_db_params()

    assert config.db_name == "custom_db"
    assert config.db_user == "postgres"
    assert config.db_password == "custom_pass"
    assert config.db_host == "localhost"
    assert config.db_port == "5432"
    assert params == {
        "dbname": "custom_db",
        "user": "postgres",
        "password": "custom_pass",
        "host": "localhost",
        "port": "5432"
    }