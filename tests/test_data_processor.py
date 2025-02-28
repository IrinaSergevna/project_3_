import pytest
import json
from src.data_processor import save_to_json, load_to_db


@pytest.fixture
def sample_employers():
    """Фикстура с тестовыми данными работодателей."""
    return [
        {"id": "1740", "name": "Яндекс", "alternate_url": "https://hh.ru/employer/1740"},
        {"id": "80", "name": "Альфа-Банк", "alternate_url": "https://hh.ru/employer/80"}
    ]


@pytest.fixture
def sample_vacancies():
    """Фикстура с тестовыми данными вакансий."""
    return [
        {
            "id": "123",
            "employer": {"id": "1740"},
            "name": "Программист",
            "salary": {"from": 100000, "to": 150000},
            "alternate_url": "https://hh.ru/vacancy/123"
        },
        {
            "id": "456",
            "employer": {"id": "80"},
            "name": "Аналитик",
            "salary": None,
            "alternate_url": "https://hh.ru/vacancy/456"
        }
    ]


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


def test_save_to_json(tmp_path, sample_employers):
    """Тест сохранения данных в JSON-файл."""
    file_path = tmp_path / "test.json"
    save_to_json(sample_employers, str(file_path))
    with open(file_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert result == sample_employers
    assert len(result) == 2
    assert result[0]["id"] == "1740"
    assert result[1]["name"] == "Альфа-Банк"


def test_load_to_db(mocker, mock_db_params, sample_employers, sample_vacancies):
    """Тест загрузки данных в базу данных."""
    # Мокаем подключение и курсор
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor  # Просто возвращаем mock_cursor
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Вызываем функцию
    load_to_db(mock_db_params, sample_employers, sample_vacancies)

    # Проверяем вызовы для employers
    assert mock_cursor.execute.call_count >= 4  # Минимум 2 для employers + 2 для vacancies
    mock_cursor.execute.assert_any_call(
        """
            INSERT INTO employers (employer_id, name, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (employer_id) DO NOTHING
        """,
        ("1740", "Яндекс", "https://hh.ru/employer/1740")
    )
    mock_cursor.execute.assert_any_call(
        """
            INSERT INTO employers (employer_id, name, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (employer_id) DO NOTHING
        """,
        ("80", "Альфа-Банк", "https://hh.ru/employer/80")
    )

    # Проверяем вызовы для vacancies
    mock_cursor.execute.assert_any_call(
        """
            INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id) DO NOTHING
        """,
        ("123", "1740", "Программист", 100000, 150000, "https://hh.ru/vacancy/123")
    )
    mock_cursor.execute.assert_any_call(
        """
            INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id) DO NOTHING
        """,
        ("456", "80", "Аналитик", None, None, "https://hh.ru/vacancy/456")
    )

    # Проверяем коммит и закрытие соединения
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()