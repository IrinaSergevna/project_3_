import pytest
from main import main


@pytest.fixture
def mock_dependencies(mocker):
    """Мокаем все зависимости для main."""
    mocker.patch("main.load_dotenv")

    # Мокаем Config
    mock_config = mocker.patch("main.Config")
    mock_config_instance = mock_config.return_value
    mock_config_instance.get_db_params.return_value = {
        "dbname": "test_db",
        "user": "postgres",
        "password": "test_pass",
        "host": "localhost",
        "port": "5432"
    }

    # Мокаем функции db_setup
    mocker.patch("main.create_database")
    mocker.patch("main.drop_tables")
    mocker.patch("main.create_tables")

    # Мокаем HhApi
    mock_hh_api = mocker.patch("main.HhApi")
    mock_hh_api_instance = mock_hh_api.return_value
    employer_ids = ["1740", "80", "15478", "3529", "78638", "2180", "39305", "4219", "676", "1455"]
    mock_hh_api_instance.get_employers.return_value = [
        {"id": emp_id, "name": f"Компания {i}", "alternate_url": f"https://hh.ru/employer/{emp_id}"}
        for i, emp_id in enumerate(employer_ids, 1)
    ]
    mock_hh_api_instance.get_vacancies.side_effect = [
        (150, [{"id": f"{emp_id}-{j}", "employer": {"id": emp_id}, "name": "Программист"}] * 150)
        for j, emp_id in enumerate(employer_ids, 1)
    ]

    # Мокаем save_to_json и load_to_db
    mocker.patch("main.save_to_json")
    mocker.patch("main.load_to_db")

    # Мокаем DBManager
    mock_db_manager = mocker.patch("main.DBManager")
    mock_db_manager_instance = mock_db_manager.return_value
    mock_db_manager_instance.get_companies_and_vacancies_count.return_value = [
        {"company": "Компания 1", "vacancies_count": 150}
    ]
    mock_db_manager_instance.get_all_vacancies.return_value = [
        {"company": "Компания 1", "vacancy": "Программист", "salary_from": 100000, "salary_to": 150000,
         "url": "https://hh.ru/vacancy/123"}
    ]
    mock_db_manager_instance.get_avg_salary.return_value = 125000.0
    mock_db_manager_instance.get_vacancies_with_higher_salary.return_value = [
        {"company": "Компания 1", "vacancy": "Программист", "salary_from": 150000, "salary_to": 200000,
         "url": "https://hh.ru/vacancy/123"}
    ]
    mock_db_manager_instance.get_vacancies_with_keyword.return_value = [
        {"company": "Компания 1", "vacancy": "Программист Python", "salary_from": 100000, "salary_to": 150000,
         "url": "https://hh.ru/vacancy/123"}
    ]


def test_main_initial_execution(mock_dependencies, mocker, capsys):
    """Тест начального выполнения main до интерфейса."""
    mocker.patch("builtins.input", return_value="0")
    main()

    captured = capsys.readouterr()
    assert "Подключено" in captured.out
    assert "1. Список компаний и количество вакансий" in captured.out


def test_main_option_1(mock_dependencies, mocker, capsys):
    """Тест выполнения опции 1 (список компаний и вакансий)."""
    mocker.patch("builtins.input", side_effect=["1", "0"])
    main()

    captured = capsys.readouterr()
    assert "Компания: Компания 1, Вакансий: 150" in captured.out
    # Убираем проверку "Общее количество вакансий всех компаний: 1500", так как она отсутствует в опции "1"


def test_main_option_2(mock_dependencies, mocker, capsys):
    """Тест выполнения опции 2 (список всех вакансий)."""
    mocker.patch("builtins.input", side_effect=["2", "0"])
    main()

    captured = capsys.readouterr()
    assert "Компания: Компания 1, Вакансия: Программист, Зарплата: от 100000 до 150000, Ссылка: https://hh.ru/vacancy/123" in captured.out
    assert "Общее количество вакансий всех компаний: 1500" in captured.out


def test_main_option_3(mock_dependencies, mocker, capsys):
    """Тест выполнения опции 3 (средняя зарплата)."""
    mocker.patch("builtins.input", side_effect=["3", "0"])
    main()

    captured = capsys.readouterr()
    assert "Средняя зарплата: 125000.00" in captured.out


def test_main_exception_handling(mock_dependencies, mocker, capsys):
    """Тест обработки исключений в main."""
    mocker.patch("main.create_database", side_effect=Exception("Тестовая ошибка"))
    main()

    captured = capsys.readouterr()
    assert "Произошла ошибка:" in captured.out
    assert "Тестовая ошибка" in captured.err


def test_main_option_5_with_keyword(mock_dependencies, mocker, capsys):
    """Тест выполнения опции 5 (поиск по ключевому слову)."""
    mocker.patch("builtins.input", side_effect=["5", "Python", "0"])
    main()

    captured = capsys.readouterr()
    assert "Компания: Компания 1, Вакансия: Программист Python, Зарплата: от 100000 до 150000, Ссылка: https://hh.ru/vacancy/123" in captured.out