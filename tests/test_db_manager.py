import pytest
from src.db_manager import DBManager


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


@pytest.fixture
def db_manager(mocker, mock_db_params):
    """Фикстура для создания экземпляра DBManager с замоканным соединением."""
    mocker.patch("psycopg2.connect")
    return DBManager(mock_db_params)


def test_get_companies_and_vacancies_count(db_manager, mocker):
    """Тест получения списка компаний и количества вакансий."""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [("Яндекс", 5), ("СБЕР", 10)]
    db_manager.conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = db_manager.get_companies_and_vacancies_count()

    assert len(result) == 2
    assert result[0] == {"company": "Яндекс", "vacancies_count": 5}
    assert result[1] == {"company": "СБЕР", "vacancies_count": 10}
    mock_cursor.execute.assert_called_once_with("""
                SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
            """)


def test_get_all_vacancies(db_manager, mocker):
    """Тест получения списка всех вакансий."""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("Яндекс", "Программист", 100000, 150000, "https://hh.ru/vacancy/123"),
        ("СБЕР", "Аналитик", 120000, None, "https://hh.ru/vacancy/456")
    ]
    db_manager.conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = db_manager.get_all_vacancies()

    assert len(result) == 2
    assert result[0] == {
        "company": "Яндекс",
        "vacancy": "Программист",
        "salary_from": 100000,
        "salary_to": 150000,
        "url": "https://hh.ru/vacancy/123"
    }
    assert result[1] == {
        "company": "СБЕР",
        "vacancy": "Аналитик",
        "salary_from": 120000,
        "salary_to": None,
        "url": "https://hh.ru/vacancy/456"
    }
    mock_cursor.execute.assert_called_once_with("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
            """)


def test_get_avg_salary(db_manager, mocker):
    """Тест получения средней зарплаты."""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [125000.0]
    db_manager.conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = db_manager.get_avg_salary()

    assert result == 125000.0
    mock_cursor.execute.assert_called_once_with("""
                SELECT AVG(COALESCE(salary_from, salary_to)) 
                FROM vacancies 
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)


def test_get_avg_salary_no_data(db_manager, mocker):
    """Тест получения средней зарплаты при отсутствии данных."""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [None]  # Нет данных
    db_manager.conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = db_manager.get_avg_salary()

    assert result == 0  # Ожидаем значение по умолчанию
    mock_cursor.execute.assert_called_once()


def test_get_vacancies_with_higher_salary(db_manager, mocker):
    """Тест получения вакансий с зарплатой выше средней."""
    # Мокаем get_avg_salary
    mocker.patch.object(db_manager, "get_avg_salary", return_value=125000.0)

    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("Яндекс", "Программист", 150000, 200000, "https://hh.ru/vacancy/123")
    ]
    db_manager.conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = db_manager.get_vacancies_with_higher_salary()

    assert len(result) == 1
    assert result[0] == {
        "company": "Яндекс",
        "vacancy": "Программист",
        "salary_from": 150000,
        "salary_to": 200000,
        "url": "https://hh.ru/vacancy/123"
    }
    mock_cursor.execute.assert_called_once_with("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE COALESCE(v.salary_from, v.salary_to) > %s
            """, (125000.0,))


def test_get_vacancies_with_keyword(db_manager, mocker):
    """Тест получения вакансий по ключевому слову."""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("Яндекс", "Программист Python", 100000, 150000, "https://hh.ru/vacancy/123")
    ]
    db_manager.conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = db_manager.get_vacancies_with_keyword("Python")

    assert len(result) == 1
    assert result[0] == {
        "company": "Яндекс",
        "vacancy": "Программист Python",
        "salary_from": 100000,
        "salary_to": 150000,
        "url": "https://hh.ru/vacancy/123"
    }
    mock_cursor.execute.assert_called_once_with("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.name ILIKE %s
            """, ("%Python%",))