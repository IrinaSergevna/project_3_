import pytest
import psycopg2
from src.db_setup import create_database, drop_tables, create_tables


@pytest.fixture
def mock_db_params():
    """Фикстура с тестовыми параметрами подключения к БД."""
    return {
        "dbname": "test_db",
        "user": "postgres",
        "password": "test_pass",
        "host": "localhost",
        "port": "5432"
    }


def test_create_database_new_db(mocker, mock_db_params):
    """Тест создания новой базы данных, если она не существует."""
    # Мокаем подключение и курсор
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # База ещё не существует
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Вызываем функцию
    create_database(mock_db_params)

    # Проверяем вызовы
    mock_conn.set_isolation_level.assert_called_once_with(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    mock_cursor.execute.assert_any_call("SELECT 1 FROM pg_database WHERE datname = 'test_db'")
    mock_cursor.execute.assert_any_call("CREATE DATABASE test_db")
    assert mock_cursor.execute.call_count == 2
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_create_database_existing_db(mocker, mock_db_params):
    """Тест, когда база данных уже существует."""
    # Мокаем подключение и курсор
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # База уже существует
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Вызываем функцию
    create_database(mock_db_params)

    # Проверяем вызовы
    mock_conn.set_isolation_level.assert_called_once_with(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    mock_cursor.execute.assert_called_once_with("SELECT 1 FROM pg_database WHERE datname = 'test_db'")
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
    # Убеждаемся, что CREATE DATABASE не вызывался
    assert "CREATE DATABASE" not in [call.args[0] for call in mock_cursor.execute.call_args_list]


def test_drop_tables_success(mocker, mock_db_params):
    """Тест успешного удаления таблиц."""
    # Мокаем подключение и курсор
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Вызываем функцию
    drop_tables(mock_db_params)

    # Проверяем вызовы
    mock_cursor.execute.assert_called_once_with("DROP TABLE IF EXISTS vacancies, employers CASCADE")
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_drop_tables_error(mocker, mock_db_params):
    """Тест обработки исключения в drop_tables."""
    # Мокаем подключение с выбросом ошибки
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = psycopg2.Error("Тестовая ошибка")
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Проверяем, что выбрасывается исключение
    with pytest.raises(psycopg2.Error, match="Тестовая ошибка"):
        drop_tables(mock_db_params)

    # Проверяем, что ошибка логируется (print вызывается)
    mock_cursor.execute.assert_called_once_with("DROP TABLE IF EXISTS vacancies, employers CASCADE")


def test_create_tables(mocker, mock_db_params):
    """Тест создания таблиц."""
    # Мокаем подключение и курсор
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Вызываем функцию
    create_tables(mock_db_params)

    # Проверяем вызовы
    assert mock_cursor.execute.call_count == 2
    mock_cursor.execute.assert_any_call("""
        CREATE TABLE IF NOT EXISTS employers (
            employer_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255)
        )
    """)
    mock_cursor.execute.assert_any_call("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(20) PRIMARY KEY,
            employer_id VARCHAR(20) REFERENCES employers(employer_id),
            name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            url VARCHAR(255)
        )
    """)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()