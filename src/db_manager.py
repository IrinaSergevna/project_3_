import psycopg2
from typing import List, Dict, Any, Optional


class DBManager:
    """Класс для работы с данными в базе данных PostgreSQL."""

    def __init__(self, db_params: Dict[str, str]):
        """Инициализирует подключение к БД."""
        self.conn = psycopg2.connect(**db_params)

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получает список компаний и количество их вакансий."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
            """)
            return [{"company": row[0], "vacancies_count": row[1]} for row in cursor.fetchall()]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий с данными о компании, зарплате и ссылке."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
            """)
            return [
                {"company": row[0], "vacancy": row[1], "salary_from": row[2], "salary_to": row[3], "url": row[4]}
                for row in cursor.fetchall()
            ]

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по всем вакансиям."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(COALESCE(salary_from, salary_to)) 
                FROM vacancies 
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            return cursor.fetchone()[0] or 0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE COALESCE(v.salary_from, v.salary_to) > %s
            """, (avg_salary,))
            return [
                {"company": row[0], "vacancy": row[1], "salary_from": row[2], "salary_to": row[3], "url": row[4]}
                for row in cursor.fetchall()
            ]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получает вакансии по ключевому слову в названии."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.name ILIKE %s
            """, (f"%{keyword}%",))
            return [
                {"company": row[0], "vacancy": row[1], "salary_from": row[2], "salary_to": row[3], "url": row[4]}
                for row in cursor.fetchall()
            ]

    def __del__(self):
        """Закрывает соединение с БД при уничтожении объекта."""
        self.conn.close()