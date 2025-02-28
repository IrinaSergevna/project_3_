import json
from typing import List, Dict, Any
import psycopg2


def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """Сохраняет данные в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_to_db(db_params: Dict[str, str], employers: List[Dict[str, Any]], vacancies: List[Dict[str, Any]]) -> None:
    """Загружает данные о работодателях и вакансиях в БД."""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Загрузка работодателей
    for emp in employers:
        cursor.execute("""
            INSERT INTO employers (employer_id, name, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (employer_id) DO NOTHING
        """, (emp["id"], emp["name"], emp["alternate_url"]))

    # Загрузка вакансий
    for vac in vacancies:
        salary = vac.get("salary")
        salary_from = salary["from"] if salary and salary.get("from") else None
        salary_to = salary["to"] if salary and salary.get("to") else None
        employer_id = vac["employer"]["id"]  # Извлекаем employer_id из вложенного словаря
        cursor.execute("""
            INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id) DO NOTHING
        """, (vac["id"], employer_id, vac["name"], salary_from, salary_to, vac["alternate_url"]))

    conn.commit()
    cursor.close()
    conn.close()