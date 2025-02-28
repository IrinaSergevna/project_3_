import requests
from typing import List, Dict, Any, Tuple


class HhApi:
    """Класс для взаимодействия с публичным API hh.ru."""

    BASE_URL = "https://api.hh.ru"

    def get_employers(self, employer_ids: List[str]) -> List[Dict[str, Any]]:
        """Получает данные о работодателях по их ID."""
        employers = []
        for emp_id in employer_ids:
            response = requests.get(f"{self.BASE_URL}/employers/{emp_id}")
            if response.status_code == 200:
                employers.append(response.json())
        return employers

    def get_vacancies(self, employer_id: str) -> tuple[int, List[Dict[str, Any]]]:
        """Получает общее количество вакансий и список вакансий для указанного работодателя."""
        params = {"employer_id": employer_id, "per_page": 100, "page": 0}  # Первая страница
        response = requests.get(f"{self.BASE_URL}/vacancies", params=params)
        if response.status_code == 200:
            data = response.json()
            total_vacancies = data.get("found", 0)  # Общее количество вакансий
            vacancies = data.get("items", [])
            return total_vacancies, vacancies
        return 0, []