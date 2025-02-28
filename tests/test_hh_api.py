import pytest
from src.hh_api import HhApi


@pytest.fixture
def hh_api():
    """Фикстура для создания экземпляра HhApi."""
    return HhApi()


def test_get_employers_success(mocker, hh_api):
    """Тест получения данных о работодателях при успешном ответе API."""
    # Мокаем requests.get один раз
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "1740",
        "name": "Яндекс",
        "alternate_url": "https://hh.ru/employer/1740"
    }
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    employer_ids = ["1740", "80"]
    result = hh_api.get_employers(employer_ids)

    assert len(result) == 2  # Два успешных запроса
    assert result[0]["id"] == "1740"
    assert result[0]["name"] == "Яндекс"
    assert result[1]["id"] == "1740"  # Второй запрос возвращает тот же мок
    assert mock_get.call_count == 2
    mock_get.assert_any_call("https://api.hh.ru/employers/1740")
    mock_get.assert_any_call("https://api.hh.ru/employers/80")


def test_get_employers_failure(mocker, hh_api):
    """Тест получения данных о работодателях при неудачном ответе API."""
    # Мокаем requests.get один раз
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    employer_ids = ["9999"]
    result = hh_api.get_employers(employer_ids)

    assert len(result) == 0  # Нет данных при ошибке
    mock_get.assert_called_once_with("https://api.hh.ru/employers/9999")


def test_get_vacancies_success(mocker, hh_api):
    """Тест получения вакансий при успешном ответе API."""
    # Мокаем requests.get один раз
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "found": 150,
        "items": [
            {
                "id": "123",
                "name": "Программист",
                "employer": {"id": "1740"},
                "salary": {"from": 100000, "to": 150000},
                "alternate_url": "https://hh.ru/vacancy/123"
            }
        ],
        "pages": 2
    }
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    total_vacancies, vacancies = hh_api.get_vacancies("1740")

    assert total_vacancies == 150
    assert len(vacancies) == 1
    assert vacancies[0]["id"] == "123"
    assert vacancies[0]["name"] == "Программист"
    mock_get.assert_called_once_with(
        "https://api.hh.ru/vacancies",
        params={"employer_id": "1740", "per_page": 100, "page": 0}
    )


def test_get_vacancies_failure(mocker, hh_api):
    """Тест получения вакансий при неудачном ответе API."""
    # Мокаем requests.get один раз
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    total_vacancies, vacancies = hh_api.get_vacancies("9999")

    assert total_vacancies == 0
    assert vacancies == []
    mock_get.assert_called_once_with(
        "https://api.hh.ru/vacancies",
        params={"employer_id": "9999", "per_page": 100, "page": 0}
    )